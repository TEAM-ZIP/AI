from chromadb import PersistentClient
import os

print("📍 현재 경로:", os.getcwd())

# Chroma 클라이언트 경로
client = PersistentClient(path="./chroma_store")

# 사전 정의된 컬렉션
collection_options = {
    "1": "book_embeddings",
    "2": "user_profiles"
}

print("\n🔎 조회할 컬렉션을 선택하세요:")
print("1. 📘 책 임베딩 (book_embeddings)")
print("2. 👤 사용자 프로파일 (user_profiles)")

choice = input("번호 입력 (1 또는 2): ").strip()

if choice not in collection_options:
    print("❌ 잘못된 입력입니다. 1 또는 2를 입력해주세요.")
    exit()

collection_name = collection_options[choice]

try:
    collection = client.get_collection(collection_name)
except Exception:
    print(f"❌ 컬렉션 '{collection_name}'을 찾을 수 없습니다.")
    exit()

count = collection.count()
print(f"\n📦 컬렉션 '{collection_name}'에는 총 {count}개의 데이터가 저장되어 있습니다.\n")

if count == 0:
    print("⚠️ 저장된 데이터가 없습니다.")
else:
    data = collection.get(include=["metadatas"])
    for i in range(len(data["ids"])):
        print(f"[{i+1}] ID: {data['ids'][i]}")
        print("메타데이터:", data["metadatas"][i])
        print("-" * 50)
