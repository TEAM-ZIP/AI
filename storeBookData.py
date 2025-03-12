from dotenv import load_dotenv
import os
import requests
import mysql.connector
import pandas as pd
import time

# 환경 변수 로드
load_dotenv()

HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')
FILELOCATION = os.getenv('FILELOCATION')

# MySQL 연결 설정
conn = mysql.connector.connect(
    host=HOST,  
    user=USER,       
    password=PASSWORD, 
    database=DATABASE
)

# 엑셀 파일 읽기
book_file = FILELOCATION
df = pd.read_excel(book_file)

# 특정 열에서 제목 가져오기
book_titles = df.iloc[:, 5].dropna().tolist()

# 결과 출력 함수
def search_book(title):
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY가 설정되지 않았습니다.")

    url = "https://dapi.kakao.com/v3/search/book"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": title}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["documents"]
    else:
        print(f"검색 실패: {title} (에러 코드: {response.status_code})")
        return None

cursor = conn.cursor()

for title in book_titles:
    try:
        results = search_book(title)
        if results:
            best_match = results[0]

            # authors는 리스트 형태 → 문자열로 변환 필요
            authors = ", ".join(best_match.get('authors', []))
            isbn = best_match.get('isbn', '')

            # ISBN이 정상적으로 처리되지 않을 경우 건너뛰기
            try:
                isbn = isbn.split(" ")[1] if " " in isbn else isbn
            except IndexError:
                print(f"⚠️ ISBN 처리 실패: {isbn}")
                continue

            # INSERT 쿼리 작성
            sql = """
                INSERT INTO books 
                (book_id, author, book_image_url, book_name, book_content, publisher) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                isbn,
                authors,
                best_match.get('thumbnail', ''),
                best_match.get('title', ''),
                best_match.get('contents', ''),
                best_match.get('publisher', '')
            )

            # 쿼리 실행 및 커밋
            cursor.execute(sql, values)
            conn.commit()

            print(f"✅ '{title}' → {cursor.rowcount} record inserted.")

        else:
            print(f"⚠️ '{title}'에 대한 검색 결과가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # API 호출 간격 조정 (속도 제한 방지)
    time.sleep(1)

# 연결 종료
cursor.close()
conn.close()
