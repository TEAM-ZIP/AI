from chromadb import PersistentClient

client = PersistentClient(path="./chroma_store")

# 현재 컬렉션 목록 조회
collections = client.list_collections()
if not collections:
    print("📦 현재 컬렉션이 존재하지 않습니다.")
    exit()

print("\n📚 현재 존재하는 컬렉션 목록:")
for col in collections:
    print(f" - {col.name}")

# 사용자 입력
target = input("\n🧹 삭제할 컬렉션 이름을 입력하세요: ").strip()

# 삭제 시도
try:
    client.delete_collection(name=target)
    print(f"✅ '{target}' 컬렉션이 성공적으로 삭제되었습니다.")
except Exception as e:
    print(f"❌ 컬렉션 삭제 실패: {e}")
