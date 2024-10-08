from fastapi import APIRouter, Header, HTTPException, status
from database import database
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(
    tags=["like"],
    responses={404: {"description" : "Not Found"}},
)

class like(BaseModel):
    postID: int
    post_type: str

@router.post("", summary="좋아요 테이블 조회 및 좋아요 수 증가")
async def insert_item(item: like, userId: str = Header()):
    """
    글의 좋아요 여부와 누른 사람들을 담은 엔드포인트입니다.
    
    - **id**: auto Increment ID
   
    - **post_id**: 글 ID

    - **userId**: 현재 접속중인 유저 이름 (parameter)
    """
    print("데이터 조회 시작")
    if len(userId)<=0 or len(userId)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 이름은 1글자 이상 25글자 이하여야 합니다."
        )
    
    try:
        query = "SELECT * FROM `like` WHERE user_id = %s AND post_id = %s AND post_type = %s"
        params = (userId, item.postID, item.post_type)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        if len(result) == 0:
            query = "INSERT INTO `like` (user_id, post_id, post_type) VALUES (%s, %s, %s)"
            params = (userId, item.postID, item.post_type)
            await database.execute_query(query, params)
            print("좋아요 수 증가")
            return {"message": "like increased successfully"}
        else:
            query = "DELETE FROM `like` WHERE user_id = %s AND post_id = %s AND post_type = %s"
            params = (userId, item.postID, item.post_type)
            await database.execute_query(query, params)
            return {"message": "like decreased successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )