from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Literal
from openai import OpenAI
from dotenv import load_dotenv
from clients.chroma import book_collection
import os

# 초기 설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

router = APIRouter()

class BookEmbeddingRequest(BaseModel):
    book_id: str
    title: str
    book_image_url: str
    book_type: Literal["normal", "indep"]
    description: str  # 벡터 생성용

@router.post("/book/embedding")
async def embed_book(req: BookEmbeddingRequest):
    input_text = f"{req.title}\n{req.description}"

    try:
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=input_text
        )
        vector = embedding.data[0].embedding
    except Exception as e:
        return {"status": "❌ 임베딩 실패", "error": str(e)}

    book_collection.add(
        ids=[req.book_id],
        embeddings=[vector],
        metadatas=[{
            "bookId": req.book_id,
            "title": req.title,
            "bookImageUrl": req.book_image_url,
            "bookType": req.book_type,
            "description" : req.description
        }]
    )
    return {"status": "✅ 책 임베딩 완료", "book_id": req.book_id}
