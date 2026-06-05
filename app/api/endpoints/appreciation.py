# app/api/endpoints/appreciation.py
from fastapi import APIRouter, HTTPException
from app.schemas.common import AppreciationRequest, AppreciationResult
from app.services.appreciation_svc import analyze_article

router = APIRouter()

@router.post("/", response_model=AppreciationResult)
def create_appreciation(request: AppreciationRequest):
    try:
        # 🎯 已修正：配合 Schema，只傳遞 request.text。讓 Gemini 大腦自動從文本內考證標題與背景！
        return analyze_article(text=request.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 在後端黑畫面印出詳細錯誤，方便我們排查
        print(f"💥 [API Endpoint Appreciation Error]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"賞析路由崩潰: {str(e)}")