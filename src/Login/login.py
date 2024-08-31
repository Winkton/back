from fastapi import APIRouter, HTTPException, status
from database import database
from typing import Optional
from pydantic import BaseModel



router = APIRouter(
    tags=["login"],
    responses={404: {"description" : "Not Found"}},
)


# Pydantic 모델 정의
class User(BaseModel):
    userId: str
    password: str
    

@router.post("/login")
async def get_users(user: User):
    '''  
    ID와 password를 받아서 DB에 전달하는 엔드포인트입니다.
    
    - **userId**: 첫 번째 필터 값 (필수)
    - **password**: 두 번째 필터 값 (필수)
    
    '''

    if len(user.userId)<=0 and len(user.userId)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )
    if len(user.password)<=0 and len(user.password)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 1글자 이상 25글자 이하여야 합니다."
        )
    

    try:
        query = 'SELECT * FROM user WHERE id=%s AND password=%s'
        params = [user.userId, user.password]
        result = await database.execute_query(query, tuple(params))
        if len(result) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID 또는 비밀번호가 틀립니다."
            )
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

    
    return {"user": result}
    