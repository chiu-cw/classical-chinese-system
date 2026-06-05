# app/schemas/common.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ─── 1. 翻譯服務所需之 Schema ───
class TranslationRequest(BaseModel):
    text: str
    enable_notes: Optional[bool] = True

class TranslationResult(BaseModel):
    original_text: str
    translated_text: str
    # 將 Dict[str, str] 設為 Optional 且預設為空字典，防止 Gemini 沒吐注釋時海關崩潰
    notes: Optional[Dict[str, str]] = Field(default_factory=dict)


# ─── 2. 作者服務所需之 Schema ───
class AuthorRequest(BaseModel):
    name: str

class AuthorInfo(BaseModel):
    name: str
    dynasty: str
    birth_death_years: Optional[str] = "資料暫缺"
    biography: str
    major_works: Optional[List[str]] = Field(default_factory=list)


# ─── 3. 賞析服務所需之 Schema ───
class AppreciationRequest(BaseModel):
    text: str

class AppreciationResult(BaseModel):
    title: Optional[str] = "古文賞析"
    core_meaning: str
    literary_style: str
    historical_context: str