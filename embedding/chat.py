from getMySQL import dataframes
from embedding import model
from chromaDB import chroma_client

# 📌 검색어 입력
query = "내 회원 아이디는 6이야. 내가 재밌게 읽은 책은?"
query_embedding = model.encode(query).tolist()

# 📌 모든 컬렉션에서 검색
for table_name in dataframes.keys():
    collection = chroma_client.get_collection(name=f"{table_name}_collection")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print(f"\n🔍 [{table_name}]에서 검색된 결과:")
    for i, doc in enumerate(results["metadatas"][0]):
        print(f"{i+1}. {doc['text']}")
