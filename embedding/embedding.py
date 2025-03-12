from sentence_transformers import SentenceTransformer
from getMySQL import dataframes

# 📌 임베딩 모델 로드
model = SentenceTransformer("all-MiniLM-L6-v2")

# 📌 테이블별 임베딩할 텍스트 가공
def create_embedding_text(table_name, row):
    """
    테이블별로 필요한 필드를 조합하여 벡터화할 텍스트를 생성하는 함수
    """
    if table_name == "books":
        return f"책 제목: {row['book_name']} / 설명: {row.get('book_content', '')} / 저자: {row.get('author', '')} / 책 표지: {row.get('book_image_url', '')} / 책 아이디: {row.get('book_id', '')}"
    
    elif table_name == "book_review":
        return f"책 리뷰: {row['bookreview_text']} / 작성자: {row.get('member_id', '')} / 평점: {row.get('book_rating', '')} / 책 아이디: {row.get('book_id', '')} / 책 리뷰 아이디: {row.get('bookreview_id', '')}"
    
    elif table_name == "book_review_likes":
        return f"사용자 {row['member_id']}가 리뷰 {row['bookreview_id']}를 좋아요"
    
    elif table_name == "bookstores":
        return f"서점 이름: {row['name']} / 주소: {row.get('address', '')} / 설명: {row.get('description', '')} / 서점 아이디: {row.get('bookstore_id', '')} / 설명: {row.get('category', '')} / 별점: {row.get('rating', '')}"
    
    elif table_name == "members":
        return f"회원 이름: {row['nickname']} / 이메일: {row.get('email', '')} / 가입일: {row.get('created_at', '')} / 회원 아이디: {row.get('member_id', '')}"
    
    elif table_name == "picked_books":
        return f"사용자 {row['member_id']}가 {row['book_id']}를 찜함"
    
    else:
        return "정보 없음"
    
id_columns = {
    "books": "book_id",
    "book_review": "bookreview_id",
    "book_review_likes": "bookreview_id",  # 좋아요는 리뷰 ID를 사용
    "bookstores": "bookstore_id",
    "members": "member_id",
    "picked_books": "book_id"  # 찜한 책의 ID
}

# 📌 모든 테이블에 임베딩 추가
for table_name, df in dataframes.items():
    # 테이블에 존재하는 ID 컬럼 가져오기
    id_column = id_columns.get(table_name, None)

    if id_column and id_column in df.columns:
        df["embedding_text"] = df.apply(lambda row: create_embedding_text(table_name, row), axis=1)
        df["embedding"] = df["embedding_text"].apply(lambda x: model.encode(x).tolist())  # 벡터 변환

        print(f"✅ {table_name} 테이블 벡터 변환 완료!")
    else:
        print(f"⚠️ {table_name} 테이블에 '{id_column}' 컬럼이 존재하지 않음, ID 없이 저장합니다.")