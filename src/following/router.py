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
    
class UserFollowingListResponse(BaseModel):
    result: List[UserFollowingResponse]

@router.get("/following/{targetUserId}", summary="특정 유저가 팔로잉한 목록을 받아옵니다.", response_model=UserFollowingListResponse)
async def get_following_user(targetUserId: str):
    """
    특정 유저가 팔로잉한 목록을 받아옵니다.
    
    - **targetUserId**: 유저 ID (필수) (str) (Parameter)
    """
    
    query = """
    SELECT u.id, u.name
    FROM following f
    JOIN user u ON f.follower = u.id
    WHERE f.following = %s  
    """
    params = (targetUserId,) 
    
    try:
        result = await database.execute_query(query, params)
        
        return { "result" : [{"userId": row['id'], "name": row['name']} for row in result] }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="데이터를 가져오는 중 오류가 발생했습니다."
        )
        
@router.get("/follower/{targetUserId}", summary="특정 유저를 팔로잉한 팔로워들 목록을 받아옵니다.", response_model=UserFollowingListResponse)
async def get_following_user(targetUserId: str):
    """
    특정 유저를 팔로잉한 팔로워들 목록을 받아옵니다.
    
    - **targetUserId**: 유저 ID (필수) (str) (Parameter)
    """
    
    query = """
    SELECT u.id, u.name
    FROM following f
    JOIN user u ON f.following = u.id   
    WHERE f.follower = %s  
    """
    params = (targetUserId,) 
    
    try:
        result = await database.execute_query(query, params)
        
        return { "result" : [{"userId": row['id'], "name": row['name']} for row in result] }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="데이터를 가져오는 중 오류가 발생했습니다."
        )
        
@router.post("/{follow_user}", summary="특정 유저 팔로잉하기", response_model= SuccessResponse)
async def follow_user(follow_user: str, userId: str = Header()):
    """
    특정 유저를 팔로잉 합니다.
    
    - **userId**: 작성자 ID (필수) (str) (Header)
    - **follow_user**: 팔로잉할 유저 ID (필수) (str) (Parameter)
    """
    
    if(userId == follow_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신은 팔로우를 할 수 없습니다"
        )
    
    query = "SELECT * FROM user WHERE id = %s"
    params = (follow_user)   
    count = await database.execute_query(query, params)
    
    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 유저입니다"
        )
    
    query = "SELECT * FROM following WHERE following = %s AND follower = %s"
    params = (userId, follow_user)   
    count = await database.execute_query(query, params)

    if len(count) == 0:  
        query = "INSERT INTO following (following, follower) VALUES (%s, %s)"
        params = (userId, follow_user)
        
        await database.execute_query(query, params)
        
        return {"message": "Successfully Followed"}
    else:
        query = "DELETE FROM following WHERE follower = %s AND following = %s"
        params = (follow_user, userId)
    
        await database.execute_query(query, params)
        
        return {"message": "Successfully UnFollowed"}
    
    
    
    
    