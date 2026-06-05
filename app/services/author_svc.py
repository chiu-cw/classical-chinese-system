# app/services/author_svc.py
import os
import json
from typing import List
from google import genai
from google.genai import types
from app.schemas.common import AuthorInfo

def get_author_info(author_name: str) -> List[AuthorInfo]:
    if not author_name.strip():
        return []
        
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("缺少環境變數 GEMINI_API_KEY")
        
    client = genai.Client(api_key=gemini_key)
    
    # 🎯 終極 Prompt 防禦：明確告訴 Gemini 輸入可能是「名字」或「整篇古文」
    system_prompt = (
        "你是一位中國歷史文學專家。使用者會提供一個『作者姓名』或『一整段文言文文本』。\n"
        "你的唯一任務是：分析該輸入，考證出對應的歷史作者（若輸入是文本，請自動分析出它是誰寫的）。\n"
        "如果文本找不到明確作者，請推測一個最可能的作者或匿名（如：佚名、佚名(詩經)）。\n\n"
        "【強制格式指導原則】:\n"
        "必須且只能回傳一個 JSON 陣列（List），裡面包含該作者的物件規格，絕對不可包含任何 Markdown 標籤：\n"
        "[\n"
        "  {\n"
        "    \"name\": \"作者姓名（如：蘇軾）\",\n"
        "    \"dynasty\": \"朝代（如：宋）\",\n"
        "    \"birth_death_years\": \"字號或生卒年\",\n"
        "    \"biography\": \"100字左右的精華生平導讀\",\n"
        "    \"major_works\": [\"代表作一\", \"代表作二\"]\n"
        "  }\n"
        "]"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"請根據以下輸入，全自動分析考證出作者生平背景:\n\n{author_name}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # 清理可能夾雜的空白或 Markdown 標籤，防止 json.loads 失敗
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
        # 解析並校對 JSON
        result_json = json.loads(clean_text)
        
        # 安全防禦：如果 Gemini 沒吐出 List，而是吐了單個 Dict，手動幫它包成 List
        if isinstance(result_json, dict):
            result_json = [result_json]
            
        return [AuthorInfo.model_validate(item) for item in result_json]
    except Exception as e:
        # 印出錯誤在後端黑畫面方便排查，同時回傳空陣列防崩潰
        print(f"❌ [Author Service Error]: {str(e)}")
        return []