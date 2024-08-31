from fastapi import APIRouter, HTTPException, status
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
    name: str
    country: str



@router.post("/signup", summary="회원가입")
async def insert_item(user: User):
    """
    데이터를 'user' 테이블에 삽입하는 엔드포인트입니다.
    
    - **id**: ID (필수)
    - **password**: 비밀번호 (필수)
    - **name**: 이름 (필수)
    - **country**: 국가 (필수)
    """
    print("데이터 삽입 시작")

    # id 필드가 있는지 여부에 따라 다른 INSERT 쿼리를 생성

    if len(user.id)<=0 and len(user.id)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )
    if len(user.password)<=0 and len(user.password)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 1글자 이상 25글자 이하여야 합니다."
        )
    if len(user.name)<=0 and len(user.name)>50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이름은 1글자 이상 50글자 이하여야 합니다."
        )
    if len(user.country)<=0 and len(user.country)>20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="국가 이름은 1글자 이상 20글자 이하여야 합니다."
    
        )
    # id 필드가 있는 경우
    query = "INSERT INTO user (id, password, name, country) VALUES (%s, %s, %s, %s)"
    params = (user.id, user.password, user.name, user.country)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data inserted successfully"}