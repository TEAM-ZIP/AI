from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from clients.chroma import profile_collection
import json

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
이 사용자의 독서 성향을 분석해 JSON 형태로 출력해주세요.
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
            {"role": "system", "content": "너는 독서 리뷰를 분석하여 사용자 독서 성향을 추론하는 분석가야."},
            {"role": "user", "content": prompt},
        ]
    )

    profile_json = response.choices[0].message.content.strip()

    try:
        parsed_profile = json.loads(profile_json)
    except json.JSONDecodeError:
        return {"error": "GPT가 올바른 JSON을 반환하지 않았습니다.", "raw": profile_json}

    # 2. 성향 요약 전체를 문자열로 만들어서 임베딩
    summary_text = (
        "주요 선호 장르: " + ", ".join(parsed_profile.get("주요 선호 장르", [])) + "\n" +
        "스타일 키워드: " + ", ".join(parsed_profile.get("스타일 키워드", [])) + "\n" +
        "독서 성향 설명: " + parsed_profile.get("독서 성향 설명", "")
    )

    # 3. 임베딩 생성 (GPT 또는 다른 임베딩 모델)
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",  # 또는 text-embedding-ada-002
        input=summary_text
    )
    embedding = embedding_response.data[0].embedding

    # 4. ChromaDB에 저장 (user_id로 고유하게 저장)
    profile_collection.add(
        ids=[req.user_id],
        embeddings=[embedding],
        metadatas=[parsed_profile]
    )

    return {"status": "✅ GPT 기반 성향 저장 완료", "profile": parsed_profile}
