# app/schemas/author.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class AuthorIdentifyRequest(BaseModel):
    text: str = Field(..., min_length=5)

class AuthorInfoResponse(BaseModel):
    name: str = Field(..., description="作者姓名")
    dynasty: Optional[str] = Field(None, description="朝代")
    birth_death_years: Optional[str] = Field(None, description="字號")
    biography: str = Field(..., description="作者生平精華介紹")
    major_works: List[str] = Field(default_factory=list, description="代表作")
    
    # 🔥 完美承載新程式碼的現代白話翻譯與 Gemini 結構化賞析
    translation: str = Field(..., description="現代白話翻譯")
    analysis: Dict[str, str] = Field(..., description="包含 theme, writing_features, rhetorical_devices, emotional_expression, modern_insight 的字典")