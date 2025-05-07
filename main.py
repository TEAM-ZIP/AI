from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from routes.bookEmbedding import router as embedding_router
from routes.userProfile import router as profile_router
from fastapi import FastAPI
from contextlib import asynccontextmanager
from clients.chroma import chroma_client


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    chroma_client.persist()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://bookstore-zip.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(embedding_router)
app.include_router(profile_router)
