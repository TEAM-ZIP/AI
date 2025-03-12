import chromadb
from getMySQL import dataframes
from embedding import id_columns

import chromadb

# 📌 ChromaDB 초기화
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 📌 모든 테이블을 개별 컬렉션으로 저장
for table_name, df in dataframes.items():
    collection = chroma_client.get_or_create_collection(name=f"{table_name}_collection")
    id_column = id_columns.get(table_name, None)  # 테이블별 ID 컬럼 가져오기

    # 📌 ChromaDB에 데이터 추가
    for index, row in df.iterrows():
        doc_id = f"{table_name}_{row[id_column]}" if id_column and id_column in df.columns else f"{table_name}_{index}"

        collection.add(
            ids=[doc_id],  # ✅ 테이블별 고유 ID 사용
            embeddings=[row["embedding"]],
            metadatas=[{
                "table": table_name,
                "original_id": row[id_column] if id_column and id_column in df.columns else None,
                "text": row["embedding_text"]
            }]
        )

    print(f"✅ {table_name} 테이블 ChromaDB 저장 완료!")
