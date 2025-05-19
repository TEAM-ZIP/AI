from fastapi import APIRouter
from pydantic import BaseModel
import os, json, requests
from dotenv import load_dotenv
from openai import OpenAI
from clients.chroma import book_collection, profile_collection
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

router = APIRouter()
user_histories: dict[str, list[dict]] = {}

class ChatRequest(BaseModel):
    user_id: str
    user_name: str
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    profile = profile_collection.get(ids=[req.user_id], include=["embeddings"])

    # 사용자 히스토리 초기화
    if req.user_id not in user_histories:
        user_histories[req.user_id] = [{
            "role": "system",
            "content": f"너는 친절하고 유쾌한 성격의 챗봇 Bookie야. 사용자의 이름은 '{req.user_name}'이고, 책 추천이 필요한 경우에만 추천을 해줘. 그렇지 않으면 일상 대화처럼 응답해줘."
        }]
    
    # 사용자 입력 추가
    user_histories[req.user_id].append({"role": "user", "content": req.message})

    # ✅ Step 1. 책 관련 여부 판단
    # 1-1. 책 관련 여부 판단
    intent_prompt = f"""
    다음 사용자의 입력이 책과 관련된 대화인지 판단해주세요. 
    질문이 책을 직접 추천해달라는 명확한 요청이 아니어도, 
    책, 독서, 작가, 장르 등에 대해 언급하거나 관심을 보이면 'yes'라고 답해주세요.

    반드시 'yes' 또는 'no'로만 응답해야 합니다.

    입력: "{req.message}"
    """

    intent_check = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 입력이 책 관련인지 판단하는 판단기야. 반드시 yes 또는 no로만 대답해."},
            {"role": "user", "content": intent_prompt},
        ],
    )

    is_book_related = intent_check.choices[0].message.content.strip().lower() == "yes"
    print("📌 책 관련 여부 판단 응답:", is_book_related)

    # 1-2. 책 관련이 아니라면: 히스토리 기반 응답만
    if not is_book_related:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=user_histories[req.user_id]
        )
        reply = response.choices[0].message.content
        user_histories[req.user_id].append({"role": "assistant", "content": reply})
        return {
            "message": reply,
            "books": []
        }

    # ✅ Step 2. 책 관련 질문
    # 2-1. 임베딩 없으면
    if not profile or len(profile["embeddings"]) == 0:
        print("📌 임베딩 없음:")
        spring_res = requests.get(
            "http://3.38.79.143:8080/api/booksnap/reviews",
            params={"page": 0, "size": 2, "sort": "trend"}
        )
        if spring_res.status_code != 200:
            return {"message": "리뷰가 부족하고 인기 도서를 불러오지 못했어요 😢", "books": []}

        try:
            books_raw = spring_res.json().get("data", {}).get("booksnapPreview", [])[:2]
        except Exception as e:
            print("🔥 spring 응답 처리 중 에러:", e)
            return {"message": "인기 도서를 불러오는 중 문제가 발생했어요 😢", "books": []}

        book_cards = []
        for b in books_raw:
            info = b["bookInfo"]
            book_cards.append({
                "title": info.get("title"),
                "bookId": info.get("bookId"),
                "bookImageUrl": info.get("bookImageUrl")
            })

        book_titles = [book["title"] for book in book_cards]
        prompt = f"""사용자의 입력: "{req.message}"

현재 이 사용자에 대한 리뷰 데이터가 없어, 독서 성향을 파악할 수 없습니다.
입력이 책 추천이라면 아래 인기 도서 중에서 자연스럽게 추천해줘.
그렇지 않으면 따뜻하게 대답해줘.

도서 목록: {book_titles}
"""

        user_histories[req.user_id].append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=user_histories[req.user_id],
        )
        reply = response.choices[0].message.content
        user_histories[req.user_id].append({"role": "assistant", "content": reply})

        return {
            "message": reply,
            "books": book_cards
        }

    # 2-2. 사용자 임베딩이 있는 경우
    user_vector = profile["embeddings"][0]
    print("📌 임베딩 있음")
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=req.message
    )
    question_vector = embedding_response.data[0].embedding
    combined_vector = [(u + q) / 2 for u, q in zip(user_vector, question_vector)]

    results = book_collection.query(
        query_embeddings=[combined_vector],
        n_results=10,
        include=["metadatas"]
    )

    candidates = results["metadatas"][0]

    simplified_candidates = [
        {"title": c.get("title", ""), "description": c.get("description", "")}
    for c in candidates
    ]

    rerank_prompt = f"""
다음은 추천 후보 도서 목록입니다:

{json.dumps(simplified_candidates, ensure_ascii=False, indent=2)}

사용자의 질문은 "{req.message}"입니다.
가장 적절한 책 2권의 **제목만** JSON 문자열 배열로 응답해주세요.
예시: ["책제목1", "책제목2"]
"""


    rerank_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 의미 기반으로 책을 다시 정렬해주는 reranker야. JSON 배열만 응답해."},
            {"role": "user", "content": rerank_prompt},
        ],
    )
    response_text = rerank_response.choices[0].message.content.strip()
    response_text = re.sub(r"```json|```", "", response_text).strip()
    print("📌 rerank 텍스트:", response_text)

    if not response_text:
        return {
        "message": "GPT가 도서 재정렬 응답을 반환하지 않았습니다.",
        "error": "응답이 비어 있음"
        }

    parsed = json.loads(response_text)

    # 응답이 ["책제목1", "책제목2"] 형태일 때
    if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
        top_titles = parsed
    # 응답이 [{"title": "제목"}] 형태일 때
    elif isinstance(parsed, list) and all(isinstance(x, dict) and "title" in x for x in parsed):
        top_titles = [x["title"] for x in parsed]
    else:
        return {
            "message": "GPT 응답 형식이 예상과 달라요 😢",
            "raw": response_text,
            "error": "title 파싱 실패"
        }

    top_books = [book for book in candidates if book.get("title") in top_titles]
    print(top_books)

    if not top_books:
        return {
            "message": "추천할 책이 부족해요. 다른 질문을 해보실래요? 😊",
            "books": []
        }
    
    final_prompt = f"""
    사용자가 책 추천을 요청했고, 다음 두 권의 도서가 선택되었습니다.

    1. {top_books[0]["title"]}: {top_books[0]["description"]}
    2. {top_books[1]["title"]}: {top_books[1]["description"]}

    각 책을 따뜻하고 자연스럽게 소개해줘. 
    책 제목과 설명만 담긴 길지 않은 추천 멘트로 마무리해줘.
    링크나 이미지도 포함하지 마.
    """

    user_histories[req.user_id].append({"role": "user", "content": final_prompt})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=user_histories[req.user_id]
    )
    reply = response.choices[0].message.content
    user_histories[req.user_id].append({"role": "assistant", "content": reply})

    book_cards = [
        {
            "title": book.get("title"),
            "bookId": book.get("bookId"),
            "bookImageUrl": book.get("bookImageUrl"),
        }
        for book in top_books
    ]

    return {
        "message": reply,
        "books": book_cards
    }
