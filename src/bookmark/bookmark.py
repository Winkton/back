from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["bookmark"],
    responses={404: {"description" : "Not Found"}},
)

class bookmark(BaseModel):
    postID: int

@router.post("", summary="리포스트(북마크)")
async def insert_item(item: bookmark, user_id: str = Header()):
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
        query = "SELECT * FROM bookmark WHERE user_id = %s AND post_id = %s"
        params = (user_id, item.postID)
        # 쿼리 실행
        result = await database.execute_query(query, params)

        if len(result) == 0:
            query = "INSERT INTO bookmark (user_id, post_id) VALUES (%s, %s)"
            params = (user_id, item.postID)
            await database.execute_query(query, params)
            return {"message": "Bookmarked successfully"}
        else:
            query = "DELETE FROM `bookmark` WHERE user_id = %s AND post_id = %s"
            params = (user_id, item.postID)
            await database.execute_query(query, params)
            return {"message": "Bookmarked contents removed successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )


    




@router.get("/{userId}", summary="리포스트(북마크) 조회하기")
async def search_item(userId: str):
    """
    북마크에 담은 포스트들을 조회하는 엔드포인트입니다.
    
    - **id**: auto Increment ID
   
    - **post_id**: 글 ID

    - **user_id**: 현재 접속중인 유저 이름 (parameter)
    """
    print("데이터 조회 시작")
    if len(userId)<=0 or len(userId)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 이름은 1글자 이상 25글자 이하여야 합니다."
        )
    
    try:
        query = "SELECT post_id FROM `bookmark` WHERE user_id = %s"
        params = (userId)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        post_ids = [row["post_id"] for row in result]

        if len(result) == 0:
            return {"message": "There's no Bookmarked contents"}
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    print("데이터 조회 완료")
    return {"postIdLIst":post_ids}