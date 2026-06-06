import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="古文智慧分析系統 API")

# 允許前端進行跨網域連線 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 從環境變數中讀取 Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("找不到 GEMINI_API_KEY 環境變數，請在 Render 設定中確認。")

genai.configure(api_key=api_key)

class TextRequest(BaseModel):
    text: str

def call_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 呼叫失敗: {str(e)}")

# 💡 注意：這裡的路徑必須跟前端完全對齊！
@app.post("/api/v1/translations/")
async def translate_text(request: TextRequest):
    prompt = f"你是一位精通中國古典文學的教授。請將以下古文翻譯成流暢的現代白話文，並分段適當排版：\n\n{request.text}"
    return {"result": call_gemini(prompt)}

@app.post("/api/v1/research/")
async def research_text(request: TextRequest):
    prompt = f"你是一位精通中國古典文學的教授。請針對以下古文或語句，進行深入的作者背景考證、寫作歷史時空背景分析與典故解說：\n\n{request.text}"
    return {"result": call_gemini(prompt)}

@app.post("/api/v1/appreciation/")
async def appreciate_text(request: TextRequest):
    prompt = f"你是一位精通中國古典文學的教授。請從文學修辭、結構美學、情感寓意等多維度，對以下古文進行深度賞析：\n\n{request.text}"
    return {"result": call_gemini(prompt)}

# 💡 這個是首頁路由，有了它，你直接點開 Render 網址就不會再出現 404，而是會出現 healthy！
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "古文系統後端正在運行中！"}