from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["팔로잉"],
    responses={404: {"description" : "Not Found"}},
)

class SuccessResponse(BaseModel):
    message: str
    
class UserFollowingResponse(BaseModel):
    userId: str
    name: str

@router.get("/following/{userId}", summary="특정 유저가 팔로잉한 목록을 받아옵니다.", response_model=List[UserFollowingResponse])
async def get_following_user(userId: str):
    """
    특정 유저가 팔로잉한 목록을 받아옵니다.
    
    - **userId**: 유저 ID (필수) (str) (Parameter)
    """
    
    query = """
    SELECT u.id, u.name
    FROM following f
    JOIN user u ON f.follower = u.id
    WHERE f.following = %s  
    """
    params = (userId,) 
    
    try:
        result = await database.execute_query(query, params)
        
        return [{"userId": row['id'], "name": row['name']} for row in result]

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="데이터를 가져오는 중 오류가 발생했습니다."
        )
        
@router.get("/follower/{userId}", summary="특정 유저를 팔로잉한 팔로워들 목록을 받아옵니다.", response_model=List[UserFollowingResponse])
async def get_following_user(userId: str):
    """
    특정 유저를 팔로잉한 팔로워들 목록을 받아옵니다.
    
    - **userId**: 유저 ID (필수) (str) (Parameter)
    """
    
    query = """
    SELECT u.id, u.name
    FROM following f
    JOIN user u ON f.following = u.id   
    WHERE f.follower = %s  
    """
    params = (userId,) 
    
    try:
        result = await database.execute_query(query, params)
        
        return [{"userId": row['id'], "name": row['name']} for row in result]

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="데이터를 가져오는 중 오류가 발생했습니다."
        )
        
@router.post("/{follow_user}", summary="특정 유저 팔로잉하기", response_model= SuccessResponse)
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
    
    
    
    
    