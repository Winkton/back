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
    #if len(user_id)
    query = "SELECT user_id, post_id FROM like WHERE user_id = %s AND post_id = %s"
    params = (user_id, item.postID)

    # dd 필드가 있는지 여부에 따라 다른 INSERT 쿼리를 생성
    if item.dd is not None:
        # dd 필드가 있는 경우
        query = "INSERT INTO test (name, dd, ff) VALUES (%s, %s, %s)"
        params = (item.name, item.dd, item.ff)
    else:
        # dd 필드가 없는 경우
        query = "INSERT INTO test (name, ff) VALUES (%s, %s)"
        params = (item.name, item.ff)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data inserted successfully"}