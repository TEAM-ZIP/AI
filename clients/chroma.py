from chromadb import PersistentClient

# ✅ check_chroma.py와 동일한 방식으로 통일
chroma_client = PersistentClient(path="./chroma_store")

book_collection = chroma_client.get_or_create_collection("book_embeddings")
profile_collection = chroma_client.get_or_create_collection("user_profiles")
