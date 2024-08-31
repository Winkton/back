from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["팔로잉"],
    responses={404: {"description" : "Not Found"}},
)

@router.post("/{follow_user}", summary="특정 유저 팔로잉")
async def follow_user(follow_user: str, user_id: str = Header()):
    """
    특정 유저를 팔로잉 합니다.
    
    - **userID**: 작성자 ID (필수) (str) (Header)
    - **follow_user**: 팔로잉할 유저 ID (필수) (str) (Parameter)
    """
    
    query = "SELECT * FROM user WHERE id = %s AND id = %s"
    params = (follow_user, user_id)   
    count = await database.execute_query(query, params)
    
    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 유저입니다"
        )
    
    query = "SELECT * FROM following WHERE following = %s AND follower = %s"
    params = (user_id, follow_user)   
    count = await database.execute_query(query, params)

    if len(count) != 0:  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 팔로우 중입니다"
        )
    
    try:
        query = "INSERT INTO following (following, follower) VALUES (%s, %s)"
        params = (user_id, follow_user)
        
        await database.execute_query(query, params)
        
        return {"message": "Successfully Followed"}
    
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    
    
    
    