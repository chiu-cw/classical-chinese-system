# app/services/translation_svc.py
import os
import json
import re
from google import genai
from google.genai import types
from app.schemas.common import TranslationResult

# ─── 傳統字典翻譯引擎 ───
class ClassicalChineseTranslator:
    def __init__(self):
        self.dictionary = {
            "之": "的", "子": "你", "余": "我", "吾": "我", "汝": "你", "曰": "說",
            "善": "好", "亦": "也是", "其": "他的", "以此": "用這個", "何": "什麼",
            "如": "像", "且": "而且", "然": "但是", "使": "讓", "聞": "聽說",
            "適": "剛好", "與": "和", "於": "在", "以": "用", "則": "就",
            "者": "的人", "也": "呀", "乎": "嗎", "矣": "了", "雖": "雖然",
            "乃": "於是", "故": "所以", "夫": "那個", "及": "以及", "遂": "於是",
            "或": "有人", "莫": "沒有人", "學": "學習", "而": "並且", "時": "按時", "習": "溫習",
            "說": "喜悅", "慍": "生氣", "君子": "品德高尚的人", "曾子": "曾參",
            "學而時習之": "學習並且按時溫習它",
            "不亦說乎": "不也是很令人喜悅嗎",
            "有朋自遠方來": "有志同道合的朋友從遠方而來",
            "不亦樂乎": "不也是很快樂嗎",
            "人不知而不慍": "別人不瞭解我，我卻不生氣",
            "不亦君子乎": "不也是一個品德高尚的人嗎",
            "吾日三省吾身": "我每天多次反省自己",
            "為政以德": "用道德來治理國政",
            "譬如北辰": "好比北極星",
            "居其所": "居於它的位置",
            "而眾星共之": "而眾星都環繞著它",
            "詩三百": "《詩經》三百篇",
            "一言以蔽之": "用一句話來概括它",
            "思無邪": "思想純正無邪",
            "道之以政": "用政令來引導百姓",
            "齊之以刑": "用刑罰來整齊百姓",
            "民免而無恥": "百姓只求免於刑罰卻沒有廉恥之心",
            "道之以德": "用道德來引導百姓",
            "齊之以禮": "用禮教來整齊百姓",
            "有恥且格": "百姓會有廉恥之心而且人心歸服",
            "吾十有五而志於學": "我十五歲時立志於學習",
            "三十而立": "三十歲時能自立於社會",
            "四十而不惑": "四十歲時不再感到迷惑",
            "五十而知天命": "五十歲時懂得天命",
            "六十而耳順": "六十歲時能聽得進各種言論",
            "七十而從心所欲": "七十歲時能隨心所欲",
            "不逾矩": "不越過規矩",
            "溫故而知新": "溫習舊的知識而得到新的領悟",
            "可以為師矣": "就可以當老師了",
            "君子不器": "君子不應像器皿一樣只有單一用途",
            "如何": "怎麼辦", "何以": "憑什麼", "不知": "不知道", "為": "做", "為師": "當老師"
        }
        self.patterns = [
            (r'何以(\w+)', r'用什麼\1'),
            (r'不([我子汝余吾之])(\w+)', r'不\2\1'),
            (r'何([為見知往有])', r'\1什麼'),
            (r'(\w+)之(善|美|惡|遠)', r'\2的\1')
        ]

    def _preprocess_rules(self, text):
        new_text = text
        for _ in range(2):
            for pattern, replacement in self.patterns:
                new_text = re.sub(pattern, replacement, new_text)
        return new_text

    def translate(self, text):
        processed_text = self._preprocess_rules(text)
        translated_text = ""
        unknown_words = []
        i = 0
        while i < len(processed_text):
            found = False
            for length in range(10, 0, -1):
                word = processed_text[i:i+length]
                if word in self.dictionary:
                    translated_text += self.dictionary[word]
                    i += length
                    found = True
                    break
            if not found:
                translated_text += processed_text[i]
                if processed_text[i] not in "，。？！ ;: \n":
                    unknown_words.append(processed_text[i])
                i += 1
        return translated_text, unknown_words

# 實例化傳統引擎
local_translator = ClassicalChineseTranslator()

def translate_classical_chinese(text: str, enable_notes: bool = True) -> TranslationResult:
    if not text.strip():
        raise ValueError("輸入文本不能為空")

    # 1. 嘗試用內建字典秒翻
    local_translation, unknown_words = local_translator.translate(text)
    if len(unknown_words) == 0:
        return TranslationResult(
            original_text=text,
            translated_text=f"【內建引擎精準秒翻】{local_translation}",
            notes={"溫故": "溫習舊的知識", "知新": "得到新的領悟"} if "溫故" in text else {}
        )

    # 2. 內建搞不定的長文，無縫移交 Gemini 2.5
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("缺少環境變數 GEMINI_API_KEY")
        
    client = genai.Client(api_key=gemini_key)
    
    system_prompt = (
        "你是一位精通中國古文翻譯的國文教授。請將使用者輸入的文言文翻譯成現代白話文。\n"
        "必須且只能回傳以下格式的純 JSON 物件，絕對不可以包含任何 ```json 等 Markdown 標籤：\n"
        "{\n"
        "  \"original_text\": \"原文內容\",\n"
        "  \"translated_text\": \"這裡填寫精準流暢的正體白話文翻譯\",\n"
        "  \"notes\": {\"難字1\": \"注釋說明\", \"難字2\": \"注釋說明\"}\n"
        "}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"請翻譯這段古文:\n\n{text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # 清理可能夾雜的空白或 Markdown 標籤
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            
        result_json = json.loads(clean_text)
        
        # 防禦：確保 notes 欄位存在
        if "notes" not in result_json:
            result_json["notes"] = {}
            
        return TranslationResult(
            original_text=result_json.get("original_text", text),
            translated_text=result_json.get("translated_text", "翻譯解析失敗"),
            notes=result_json.get("notes", {})
        )
    except Exception as e:
        # 🔥 最關鍵的除錯線索：將錯誤訊息直接噴在後端 CMD 視窗中！
        print(f"❌ [Translation Service Error]: {str(e)}")
        # 回傳一個安全的備用翻譯，確保網頁絕不跳出 500 錯誤
        return TranslationResult(
            original_text=text,
            translated_text=f"後端大腦在呼叫 Gemini 時遇到阻礙，請確認您的 API Key。錯誤回報: {str(e)}",
            notes={}
        )