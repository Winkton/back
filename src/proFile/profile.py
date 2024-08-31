from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["profile"],
    responses={404: {"description" : "Not Found"}},
)


@router.get("/{userId}", summary="유저의 프로필 반환")
async def insert_item(userId: str):
    """
    유저의 id, 이름, 국가를 반환해주는 엔드포인트입니다.
    
    - **userId**: 프로필을 조회할 유저 ID
    
    """
    print("데이터 조회 시작")
    if len(userId)<=0 or len(userId)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 ID는 1글자 이상 30글자 이하여야 합니다."
        )
    
    try:
        query = "SELECT * FROM user WHERE id = %s"
        params = (userId)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        formatted_result = [{"userId": row['id'], "username": row['name'], "country": row['country']} for row in result]
        return {"result": formatted_result}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )



@router.put("/{username}&{country}", summary="유저의 프로필 업데이트")
async def insert_item(username: str, country: str, current_user_id: str = Header()):
    """
    본인의 경우, ID를 제외한 이름과 국가의 변경을 위한 엔드포인트입니다.
    
    - **username**: 유저의 바꿀 이름
    
    - **country**: 유저의 바꿀 국가
    
    - **currnent_user_id**: 현재 접속중인 유저 이름 (parameter)
    """
    
    if len(current_user_id)<=0 or len(current_user_id)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 ID는 1글자 이상 30글자 이하여야 합니다."
        )
    
    try:
        query = "UPDATE user SET name = %s, country = %s WHERE id = %s"
        params = (username, country, current_user_id)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        return {"Message": "Updated Successful"}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
        
