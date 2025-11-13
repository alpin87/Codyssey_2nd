from pydantic import BaseModel
from typing import Optional


class TodoItem(BaseModel):
    '''
    TODO 항목의 데이터 모델 (ID 제외)
    POST (추가) 및 PUT (수정) 요청의 본문(body)에 사용됩니다.
    '''
    title: str
    description: Optional[str] = None
    completed: bool = False