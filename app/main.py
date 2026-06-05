# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import translation, author, appreciation

app = FastAPI(
    title="文言文智慧賞析系統 API - 專業拆分版",
    description="提供獨立的古文翻譯、作者介紹與文章賞析微服務",
    version="1.0.0"
)

# 補上跨網域 CORS，確保 Streamlit 前端網頁呼叫時不會被瀏覽器攔截
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊你設計的三大黃金路由線路
app.include_router(translation.router, prefix="/api/v1/translations", tags=["Translation"])
app.include_router(author.router, prefix="/api/v1/authors", tags=["Author"])
app.include_router(appreciation.router, prefix="/api/v1/appreciations", tags=["Appreciation"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}