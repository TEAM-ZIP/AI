# 서점ZIP

![alt text](<Asset/Slide 16_9 - 1.png>)

## 프로젝트 개요

이 프로젝트는 개인만의 특성을 드러내는 독립출판물의 감성을 즐기는 사용자가 독립출판물을 더 잘 찾아낼 수 있도록, 독립출판물을 비치한 서점에 대한 위치, 키워드, 운영시간 등의 정보와 도서출판전산망에 등록되지 않은 독립출판물 리뷰 제공 및 추천 시스템을 제공합니다.

### 주요 기능: Bookie (RAG 기반 독립출판물 추천)

- LLM + Vector DB를 활용한 RAG 기반 AI 추천 시스템
- 사용자 리뷰 등의 활동 데이터를 바탕으로 개인화된 독립출판물 추천

1. 책 임베딩
2. 사용자 프로파일 생성
3. 사용자에게 책 추천

## Source Code

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Core Functionality**:
  - RAG( Retrieval-Augmented Generation ) 기반 추천 및 컨텐츠 분석 서비스
  - OpenAI API 연동 및 자연어 처리 기능 제공
  - ChromaDB 등 Vector DB를 활용한 벡터 검색 및 임베딩 기반 정보 조회
- **Key Libraries**:
  - **fastapi**: 웹 서버 엔드포인트 정의 및 요청/응답 처리
  - **uvicorn**: ASGI 서버 실행
  - **openai**: OpenAI API 연동을 통한 LLM 활용
  - **pydantic**: 데이터 검증 및 스키마 정의
  - **chromadb**: Vector DB 활용을 통한 유사도 검색 및 임베딩 저장
  - **transformers / sentence-transformers**: 임베딩 모델 및 NLP 모델 사용

## 🛠️ 사용 기술

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)
![python](https://img.shields.io/badge/python-3670A0?style=flat-square&logo=python&logoColor=ffdd54)
![Uvicorn](https://img.shields.io/badge/Uvicorn-43A047?style=flat-square)
![Pydantic](https://img.shields.io/badge/Pydantic-0073E6?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FFCA28?style=flat-square&logo=&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT4o-0072C6?style=flat-square)
![AWS](https://img.shields.io/badge/AWS-EC2-232F3E?style=flat-square&logo=amazonaws&logoColor=white)

---

## 사전 준비

- **환경 변수 설정**: `.env` 파일을 생성하고 설정
  - 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가합니다.
  - .env 파일을 제공받은 경우, 해당 파일의 내용을 그대로 붙여넣기 해 주세요.
  ```bash
  OPENAI_API_KEY= <발급받은 OPEN AI KEY>
  ```

## How to Build

1.  **레포지토리 클론**

    ```bash
    git clone https://github.com/QRAB-EWHA/fastapi.git
    cd fastapi
    ```

2.  **가상환경 생성 및 활성화**
    가상환경을 생성하고 활성화합니다. 가상환경이 제대로 활성화되면 터미널 프롬프트 앞에 (venv)가 표시됩니다.
    - Mac/Linux:
      ```bash
      python -m venv venv
      source venv/bin/activate
      ```
    - Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

## How to Install

1. **프로젝트 코드 및 종속성 설치**<br>
   프로젝트에서 사용된 Python 라이브러리를 설치하려면 위 How to Build와 같이 먼저 가상 환경을 설정한 후 아래 명령어를 실행합니다.<br>

   (1) 라이브러리 설치<br>
   `requirements.txt` 파일에 포함된 모든 종속성을 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

- `requirements.txt`에는 다음과 같은 주요 라이브러리가 포함되어 있습니다.

  ```plaintext
  chromadb
  fastapi
  python-dotenv
  pydantic
  uvicorn
  openai
  ```

  (2) 설치된 라이브러리 확인<br>
  아래 명령어를 사용해 설치된 라이브러리를 확인합니다.

  ```
  pip list
  ```

<br>

2. **빌드 및 실행**

```
python -m uvicorn app.main:app --reload
```

<br>

## How to Test

서버 실행 후 Postman 또는 curl을 통해 API를 테스트할 수 있습니다.

### 1. 챗봇 질문 API

사용자가 책 추천을 받기 위해 직접 사용하는 API

- URL: `POST /chat`
- Header: Authorization 필수
- Body

```json
{
  "user_id": "1",
  "user_name": "용가리코드",
  "message": "책 추천해줘"
}
```

- 응답

```json
{
  "message": "용가리코드님이 좋아할만한 책 두 권을 추천해드릴게요. 두 작품 모두 독특한 여운과 통찰을 제공하니, 꼭 한번 읽어보세요!",
  "books": [
    {
      "title": "소년이 온다",
      "bookId": "9",
      "bookImageUrl": "https://search1.kakaocdn.net/thumb/R120x174.q85/?fname=http%3A%2F%2Ft1.daumcdn.net%2Flbook%2Fimage%2F532683%3Ftimestamp%3D20250325113846"
    },
    {
      "title": "좀머 씨 이야기(2판)(양장본 HardCover)",
      "bookId": "33",
      "bookImageUrl": "https://search1.kakaocdn.net/thumb/R120x174.q85/?fname=http%3A%2F%2Ft1.daumcdn.net%2Flbook%2Fimage%2F505945%3Ftimestamp%3D20220826230936"
    }
  ]
}
```

### 2. 책 임베딩 (최초)

사용자가 리뷰를 작성했을 때 책의 기본 정보를 임베딩하기 위해 호출되는 API

- URL : `GET /book/embedding`
- Body

```json
{
  "book_id": "1",
  "title": "소년이 온다",
  "book_image_url": "[string](https://search1.kakaocdn.net/thumb/R120x174.q85/?fname=http%3A%2F%2Ft1.daumcdn.net%2Flbook%2Fimage%2F532683%3Ftimestamp%3D20250325113846)",
  "book_type": "normal",
  "description": "2014년 만해문학상, 2017년 이탈리아 말라파르테 문학상을 수상하고 전세계 20여개국에 번역 출간되며 세계를 사로잡은 우리 시대의 소설 『소년이 온다』. 이 작품은 『채식주의자』로 인터내셔널 부커상을 수상한 한강 작가에게 “눈을 뗄 수 없는, 보편적이며 깊은 울림”(뉴욕타임즈), “역사와 인간의 본질을 다룬 충격적이고 도발적인 소설..."
}
```

### 3. 책 임베딩 업데이트

사용자가 리뷰를 작성했을 때 사용자 리뷰를 바탕으로 책의 description을 업데이트하기 위해 호출되는 API

- URL : `GET /book/update`
- Body

```json
{
  "book_id": "1",
  "new_reviews": [
    "이 책을 읽고 울지 않는 사람이 있을까? 모든 사람이 꼭 한 번씩은 읽어봤으면 좋겠다"
  ]
}
```

### 4. 사용자 프로파일 생성 및 업데이트

사용자가 리뷰를 작성했을 때 사용자의 리뷰를 바탕으로 사용자의 프로파일을 생성 및 업데이트하기 위해 호출되는 API

- URL : `GET /profile/update`
- Body

```json
{
  "user_id": "1",
  "userName": "책읽자용가리",
  "title": "소년이 온다",
  "rating": 5,
  "reviewText": "이 책을 읽고 울지 않는 사람이 있을까? 모든 사람이 꼭 한 번씩은 읽어봤으면 좋겠다"
}
```

## Database Management

1. ChromaDB에 임베딩 된 데이터 확인하기

```
python3 chroma_data.py
```

- 위 코드로 임베딩된 사용자 프로파일과 책들을 확인 가능

2. ChromaDB에 임베딩 된 데이터 초기화하기

```
python3 chroma_reset.py
```

- 위 코드로 ChromaDB에 저장된 내용들 초기화 가능

## 👋🏻 Members

| <img src="https://github.com/yongaricode.png" width=120/> | <img src="https://github.com/topograp2.png" width=120/> | <img src="https://github.com/sohyu-na.png" width=120/> |
| :-------------------------------------------------------: | :-----------------------------------------------------: | :----------------------------------------------------: |
|         [강다형](https://github.com/yongaricode)          |         [홍지형](https://github.com/topograp2)          |         [소현아](https://github.com/sohyu-na)          |

## 📍 아키텍처

![alt text](/Asset/architecture.png)

## 🗂️ 폴더 구조

```

📂 AI/
│
├─ 📂 __pycache__ ▶️ Python cache files
│
├─ 📂 Asset ▶️ Static assets and resources
│
├─ 📂 chroma_db ▶️ ChromaDB database files
│
├─ 📂 clients ▶️ API client configurations
│
├─ 📂 routes ▶️ FastAPI route handlers
│
├─ 🐍 chroma_data.py ▶️ ChromaDB data management script
├─ 🐍 chroma_reset.py ▶️ ChromaDB reset utility
├─ 🐍 main.py ▶️ FastAPI application entry point
│
└─ 📄 requirements.txt ▶️ Python dependencies

```

<br>

## 📚 오픈소스

## AI Libraries & Tools

1. **FastAPI**: [FastAPI](https://fastapi.tiangolo.com/ko/)
2. **ChromaDB**: [ChromaDB](https://www.trychroma.com/)
3. **Uvicorn**: [Uvicorn](https://www.uvicorn.org/)
4. **OpenAI GPT-4** : [OpenAI](https://openai.com/)
5. **Pydantic**: [Pyndatic](https://docs.pydantic.dev/latest/)
