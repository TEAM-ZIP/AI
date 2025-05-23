from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os, json, re
from clients.chroma import profile_collection

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

class ReviewRequest(BaseModel):
    user_id: str
    userName: str
    title: str
    rating: int
    reviewText: str

@router.post("/profile/update")
async def update_user_profile(req: ReviewRequest):
    # 1. GPT에게 프로파일 생성 요청
    prompt = f"""다음은 사용자가 남긴 책 리뷰입니다.
리뷰: "{req.reviewText}"

이 사용자의 독서 성향을 분석해 다음 형식의 JSON으로 출력해주세요.  
**반드시 코드블록 없이 순수 JSON만 응답해주세요.**

형식:
{{
  "주요 선호 장르": [],
  "스타일 키워드": [],
  "독서 성향 설명": ""
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 독서 리뷰를 분석하여 사용자 독서 성향을 추론하는 분석가야. 반드시 순수 JSON만 출력해야 해."},
            {"role": "user", "content": prompt},
        ]
    )

    profile_json = response.choices[0].message.content.strip()
    profile_json = re.sub(r"```json|```", "", profile_json).strip()  # ✅ 백틱 제거

    try:
        parsed_profile = json.loads(profile_json)
    except json.JSONDecodeError:
        return {"error": "GPT가 올바른 JSON을 반환하지 않았습니다.", "raw": profile_json}

    # ✅ 리스트 값을 문자열로 변환
    cleaned_metadata = {
        k: ", ".join(v) if isinstance(v, list) else v
        for k, v in parsed_profile.items()
    }

    # 2. 성향 요약 전체를 문자열로 만들어서 임베딩
    summary_text = (
        "주요 선호 장르: " + cleaned_metadata.get("주요 선호 장르", "") + "\n" +
        "스타일 키워드: " + cleaned_metadata.get("스타일 키워드", "") + "\n" +
        "독서 성향 설명: " + cleaned_metadata.get("독서 성향 설명", "")
    )

    # 3. 임베딩 생성
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=summary_text 
    )

    embedding = embedding_response.data[0].embedding

    # 4. ChromaDB에 저장
    profile_collection.add(
        ids=[req.user_id],
        embeddings=[embedding],
        metadatas=[cleaned_metadata]
    )

    return {
        "status": "✅ GPT 기반 성향 저장 완료",
        "profile": cleaned_metadata
    }
