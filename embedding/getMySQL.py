import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# 📌 MySQL 연결 설정
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")


tables = {
    "books": "SELECT * FROM books",
    "book_review": "SELECT * FROM book_review",
    "book_review_likes": "SELECT * FROM book_review_likes",
    "bookstores": "SELECT * FROM bookstores",
    "members": "SELECT * FROM members",
    "picked_books": "SELECT * FROM picked_book"
}

# 📌 테이블 데이터 저장할 딕셔너리
dataframes = {}

# 📌 모든 테이블을 불러오기
for table_name, query in tables.items():
    df = pd.read_sql(query, engine)
    dataframes[table_name] = df  # 딕셔너리에 저장
    print(f"✅ {table_name} 테이블 로드 완료! ({df.shape[0]} rows)")

# MySQL 연결 종료
engine.dispose()



