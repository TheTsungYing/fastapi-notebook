from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from router import auth, users, notes
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
origins = os.getenv("CORS_ORIGINS").split(",")

# 初始化 FastAPI 應用程式
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # 允許的來源列表
    allow_credentials=True,         # 允許發送 cookie
    allow_methods=["*"],            # 允許所有 HTTP 方法 (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],            # 允許所有請求頭
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.get("/")
def index():
    return {"FastAPI":"Hello World!"}