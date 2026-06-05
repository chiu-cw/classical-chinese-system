# app/api/endpoints/translation.py
from fastapi import APIRouter, HTTPException
from app.schemas.common import TranslationRequest, TranslationResult
from app.services.translation_svc import translate_classical_chinese

router = APIRouter()

@router.post("/", response_model=TranslationResult)
def create_translation(request: TranslationRequest):
    try:
        # 🎯 呼叫我們剛剛融合了傳統字典與 Gemini 的超級翻譯服務
        result = translate_classical_chinese(
            text=request.text, 
            enable_notes=request.enable_notes
        )
        return result
    except ValueError as ve:
        # 如果是輸入空白等資料錯誤，回傳 400 錯誤
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # 🔥 防禦罩：如果後端真的又崩潰，印出詳細紅字在 Uvicorn 黑畫面
        print(f"💥 [API Endpoint Translation Error]: {str(e)}")
        # 回傳 500 的同時，把錯誤訊息帶出來給前端，拒絕冷冰冰的 500 報錯
        raise HTTPException(status_code=500, detail=f"後端內部錯誤: {str(e)}")