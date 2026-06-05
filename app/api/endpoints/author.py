# app/api/endpoints/author.py
from fastapi import APIRouter, Query
from typing import List
from app.schemas.common import AuthorInfo
from app.services.author_svc import get_author_info

router = APIRouter()

@router.get("/", response_model=List[AuthorInfo])
def search_authors(name: str = Query(..., description="作者姓名")):
    return get_author_info(author_name=name)