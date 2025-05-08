from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, re, json
from clients.chroma import book_collection

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

router = APIRouter()

class BookUpdateRequest(BaseModel):
    book_id: str
    new_reviews: list[str]

@router.post("/book/update")
async def update_book_embedding(req: BookUpdateRequest):
    # 1. 기존 메타데이터 가져오기
    try:
        result = book_collection.get(ids=[req.book_id], include=["metadatas"])
        old_metadata = result["metadatas"][0]
        old_description = old_metadata.get("description", "")
    except Exception as e:
        return {"status": "❌ 기존 메타데이터 조회 실패", "error": str(e)}

    # 2. GPT로 요약 생성
    combined_text = old_description + "\n" + "\n".join(req.new_reviews)
    prompt = f"""
다음은 책 소개와 사용자 리뷰입니다. 이 내용을 바탕으로 책의 핵심 내용을 3줄에서 5줄 사이로 요약해주세요.

내용:
\"\"\"{combined_text}\"\"\"

요약:
"""

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 책 소개와 리뷰를 종합해 요약을 잘해주는 요약가야."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = gpt_response.choices[0].message.content.strip()
    except Exception as e:
        return {"status": "❌ GPT 요약 실패", "error": str(e)}

    # 3. 임베딩 생성
    try:
        embed_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=summary
        )
        new_vector = embed_response.data[0].embedding
    except Exception as e:
        return {"status": "❌ 임베딩 실패", "error": str(e)}

    # 4. ChromaDB 업데이트
    try:
        book_collection.update(
            ids=[req.book_id],
            embeddings=[new_vector],
            metadatas=[{**old_metadata, "description": summary}]
        )
    except Exception as e:
        return {"status": "❌ ChromaDB 업데이트 실패", "error": str(e)}

    return {"status": "✅ 책 임베딩 업데이트 완료", "book_id": req.book_id, "summary": summary}


