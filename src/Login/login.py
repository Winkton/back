from fastapi import APIRouter
from database import database
from typing import Optional
from pydantic import BaseModel



router = APIRouter(
    tags=["test"],
    responses={404: {"description" : "Not Found"}},
)


# Pydantic 모델 정의
class User(BaseModel):
    id: str
    password: str
    

@router.post("/login")
async def get_users(user: User):
    '''  
    ID와 password를 받아서 DB에 전달하는 엔드포인트입니다.
    
    - **id**: 첫 번째 필터 값 (필수)
    - **password**: 두 번째 필터 값 (필수)
    '''
    query = 'SELECT * FROM user WHERE id=%s AND password=%s'
    params = [user.id, user.password]
    result = await database.execute_query(query, tuple(params))
    return {"user": result}
    