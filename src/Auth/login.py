from fastapi import APIRouter, HTTPException, status
from database import database
from typing import Optional, List
from pydantic import BaseModel



router = APIRouter(
    tags=["Auth"],
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
    
    - **userId**: 로그인할 유저 ID
    - **password**: 로그인할 유저 비밀번호
    
    '''

    if len(user.userId)<=0 or len(user.userId)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )
    if len(user.password)<=0 or len(user.password)>25:
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

    
    return {"Message": "Login Successful"}
    


# Pydantic 모델 정의
class User(BaseModel):
    userId: str
    password: str
    username: str
    country: str

@router.post("/signup", summary="회원가입", response_model = User)
async def insert_item(user: User):
    """
    데이터를 'user' 테이블에 삽입하는 엔드포인트입니다.
    
    - **userId**: ID (필수)
    - **password**: 비밀번호 (필수)
    - **username**: 이름 (필수)
    - **country**: 국가 (필수)
    """
    print("데이터 삽입 시작")

    # id 필드가 있는지 여부에 따라 다른 INSERT 쿼리를 생성

    if len(user.userId)<=0 or len(user.userId)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )
    if len(user.password)<=0 or len(user.password)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 1글자 이상 25글자 이하여야 합니다."
        )
    if len(user.username)<=0 or len(user.username)>50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이름은 1글자 이상 50글자 이하여야 합니다."
        )
    if len(user.country)<=0 or len(user.country)>20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="국가 이름은 1글자 이상 20글자 이하여야 합니다."
    
        )
    
    try:
        # id 필드가 있는 경우
        query = "INSERT INTO user (id, password, name, country) VALUES (%s, %s, %s, %s)"
        params = (user.userId, user.password, user.username, user.country)
    
        # 쿼리 실행
        await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {
        "userId": user.userId,
        "password": user.password,
        "username": user.username,
        "country": user.country
    }

class User(BaseModel):
    userId: str

@router.post("/searchId")
async def get_users(user: User):

    '''  
    ID를 받아서 DB에서 조회하는 엔드포인트입니다.
    
    - **userId**: 찾을 유저 ID
    
    '''

    if len(user.userId)<=0 or len(user.userId)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )    

    try:
        query = 'SELECT * FROM user WHERE id=%s'
        params = user.userId
        result = await database.execute_query(query, params)
        if len(result) == 0:
            return {"Message": "요청하신 ID가 없습니다."}
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

    
    return {"userId": user.userId}





class User(BaseModel):
    userId: str
    password: str

@router.post("/updatePassword")
async def get_users(user: User):

    '''  
    ID와 PW를 받아서 DB를 업데이트하는 엔드포인트입니다.
    
    - **userId**: 찾을 유저 ID
    
    '''

    if len(user.userId)<=0 or len(user.userId)>30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID는 1글자 이상 30글자 이하여야 합니다."
        )    

    if len(user.password)<=0 or len(user.password)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 1글자 이상 25글자 이하여야 합니다."
        )
    

    try:
        query = 'UPDATE user SET password = %s WHERE id = %s'
        params = (user.password, user.userId)
        await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

    
    return {"Message": "비밀번호 변경 완료"}