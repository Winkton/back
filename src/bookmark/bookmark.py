from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    tags=["bookmark"],
    responses={404: {"description" : "Not Found"}},
)

class bookmark(BaseModel):
    postID: int
    postType: str

@router.post("", summary="리포스트(북마크)")
async def insert_item(item: bookmark, user_id: str = Header()):
    """
    글의 좋아요 여부와 누른 사람들을 담은 엔드포인트입니다.
   
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
        query = "SELECT * FROM bookmark WHERE user_id = %s AND post_id = %s AND post_type = %s"
        params = (user_id, item.postID, item.postType)
        # 쿼리 실행
        result = await database.execute_query(query, params)

        if len(result) == 0:
            query = "INSERT INTO bookmark (user_id, post_id, post_type) VALUES (%s, %s, %s)"
            params = (user_id, item.postID, item.postType)
            await database.execute_query(query, params)
            return {"message": "Bookmarked successfully"}
        else:
            query = "DELETE FROM `bookmark` WHERE user_id = %s AND post_id = %s AND post_type = %s"
            params = (user_id, item.postID, item.postType)
            await database.execute_query(query, params)
            return {"message": "Bookmarked contents removed successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

class OXItem(BaseModel):
    id: int
    question: str
    answer: bool
    author: str
    postType: str
    created_at: datetime
    liked: bool
    likeCount: int
    
class qa(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime
    postType: str
    liked: bool
    likeCount: int

class bookmarkListResponse(BaseModel):
    oxList: List[OXItem]
    qaList: List[qa]

@router.get("/{userId}", summary="리포스트(북마크) 조회하기", response_model=bookmarkListResponse)
async def search_item(targetUserId: str, user_id: str = Header()):
    """
    북마크에 담은 포스트들을 조회하는 엔드포인트입니다.
    
    - **targetUserId**: 북마크를 조회할려는 user의 ID (필수) (parameter)

    - **user_id**: 현재 접속중인 유저 이름 (parameter)
    """
    print("데이터 조회 시작")
    if len(targetUserId)<=0 or len(targetUserId)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 이름은 1글자 이상 25글자 이하여야 합니다."
        )
        
    query = "SELECT * FROM user WHERE id = %s"
    params = (targetUserId)   
    count = await database.execute_query(query, params)
    
    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않는 유저입니다"
        )
    
    try:
        query = """
        SELECT 
            o.id, 
            o.question, 
            o.answer,
            o.author,
            o.created_at,
            CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
            COALESCE(like_count_table.like_count, 0) AS like_count 
        FROM ox o
        JOIN `bookmark` b ON o.id = b.post_id
        LEFT JOIN `like` l ON o.id = l.post_id AND l.user_id = %s AND l.post_type = 'ox'
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count 
            FROM `like`
            WHERE post_type = 'ox'
            GROUP BY post_id
        ) AS like_count_table ON o.id = like_count_table.post_id 
        WHERE b.user_id = %s AND b.post_type = 'ox'
        """
        params = (user_id, targetUserId)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        ox = [{"id": row['id'], "question": row['question'], "answer": row['answer'], "author": row["author"], "created_at": row["created_at"], "postType": "ox", "liked": row["liked"], "likeCount": row["like_count"]} for row in result]  
        
        query = """
        SELECT 
            q.id, 
            q.content, 
            q.author, 
            q.created_at,
            CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
            COALESCE(like_count_table.like_count, 0) AS like_count  
        FROM qa q
        JOIN `bookmark` b ON q.id = b.post_id
        LEFT JOIN `like` l ON q.id = l.post_id AND l.user_id = %s AND l.post_type = 'qa'
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count 
            FROM `like`
            WHERE post_type = 'qa'
            GROUP BY post_id
        ) AS like_count_table ON q.id = like_count_table.post_id 
        WHERE b.user_id = %s AND b.post_type = 'qa'
        """
        params = (user_id, targetUserId)
        # 쿼리 실행
        result2 = await database.execute_query(query, params)
        qa = [{"id": row['id'], "content": row['content'], "author": row['author'], "postType": "qa", "created_at":row['created_at'], "liked": row["liked"], "likeCount": row["like_count"]} for row in result2]
                
        if len(result) == 0 and len(result2):
            return {"message": "There's no Bookmarked contents"}
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    print("데이터 조회 완료")
    return {"oxList": ox, "qaList": qa}