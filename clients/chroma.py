# clients/chroma.py
import chromadb
from chromadb.config import Settings

# 전역에서 재사용할 클라이언트
chroma_client = chromadb.Client(Settings(persist_directory="./chroma_store"))

# 필요한 컬렉션도 여기서 정의
book_collection = chroma_client.get_or_create_collection("book_embeddings")
profile_collection = chroma_client.get_or_create_collection("user_profiles")
