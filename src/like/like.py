from fastapi import APIRouter, Header, HTTPException, status
from database import database
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(
    tags=["like"],
    responses={404: {"description" : "Not Found"}},
)

class like(BaseModel):
    id: int
    postID: int

class likeListResponse(BaseModel):
    result: List[like]

@router.post("/like", summary="좋아요 테이블 조회")
async def insert_item(item: like, user_id: str = Header(), response_model = likeListResponse):
    """
    글의 좋아요 여부와 누른 사람들을 담은 엔드포인트입니다.
    
    - **id**: auto Increment ID
   
    - **post_id**: 글 ID

    - **user_id**: 현재 접속중인 유저 이름 (parameter)
    """
    print("데이터 조회 시작")
    if len(user_id)<=0 or len(user_id)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 이름은 1글자 이상 25글자 이하여야 합니다."
        )
    
    try:
        query = "SELECT user_id, post_id FROM like WHERE user_id = %s AND post_id = %s"
        params = (user_id, item.postID)
        # 쿼리 실행
        result = await database.execute_query(query, params)

        if len(result) == 0:
            query = "INSERT INTO like (user_id, post_id) VALUES (%s, %s)"
            params = (user_id, item.postID)
            
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {"message": "Data searched successfully"}