# app/services/appreciation_svc.py
import os
import json
from google import genai
from google.genai import types
from app.schemas.common import AppreciationResult

def analyze_article(text: str) -> AppreciationResult:
    if len(text.strip()) < 5:
        raise ValueError("輸入文本過短，無法進行有效分析")
        
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("缺少環境變數 GEMINI_API_KEY")
        
    client = genai.Client(api_key=gemini_key)
    
    system_prompt = (
        "你是一位精通古典詩詞賞析的文學泰斗。請針對使用者提供的文言文作品進行三維度的深度解析。\n"
        "必須且只能回傳以下純 JSON 格式，絕對不可以包含任何 Markdown 標籤：\n"
        "{\n"
        "  \"title\": \"確認篇名（若未知則根據文本猜測填入）\",\n"
        "  \"core_meaning\": \"核心主旨與思想（100-200字）\",\n"
        "  \"literary_style\": \"寫作特色、修辭手法與藝術風格（100-200字）\",\n"
        "  \"historical_context\": \"創作背景、作者當時的情感心境與現代啟示（100-200字）\"\n"
        "}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"請針對以下這段古文內文進行深度多維度賞析：\n\n{text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        # 清理可能夾雜的空白或 Markdown 標籤，防止 json.loads 失敗
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
        result_json = json.loads(clean_text)
        return AppreciationResult.model_validate(result_json)
    except Exception as e:
        print(f"❌ [Appreciation Service Error]: {str(e)}")
        raise RuntimeError(f"Gemini 賞析服務異常: {str(e)}")