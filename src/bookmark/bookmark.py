from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(
    tags=["bookmark"],
    responses={404: {"description" : "Not Found"}},
)

class bookmark(BaseModel):
    postID: int
    postType: str

@router.post("", summary="리포스트(북마크)")
async def insert_item(item: bookmark, userId: str = Header()):
    """
    글의 좋아요 여부와 누른 사람들을 담은 엔드포인트입니다.
   
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
        query = "SELECT * FROM bookmark WHERE user_id = %s AND post_id = %s AND post_type = %s"
        params = (userId, item.postID, item.postType)
        # 쿼리 실행
        result = await database.execute_query(query, params)

        if len(result) == 0:
            query = "INSERT INTO bookmark (user_id, post_id, post_type) VALUES (%s, %s, %s)"
            params = (userId, item.postID, item.postType)
            await database.execute_query(query, params)
            return {"message": "Bookmarked successfully"}
        else:
            query = "DELETE FROM `bookmark` WHERE user_id = %s AND post_id = %s AND post_type = %s"
            params = (userId, item.postID, item.postType)
            await database.execute_query(query, params)
            return {"message": "Bookmarked contents removed successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

class OXItem(BaseModel):
    id: int = Field(..., description="OX 퀴즈의 고유 ID")
    content: str = Field(..., description="OX 퀴즈 질문 내용")
    author: str = Field(..., description="OX 퀴즈 작성자의 사용자 ID")
    oCount: int = Field(..., description="퀴즈에 대한 'O' 투표 수")
    xCount: int = Field(..., description="퀴즈에 대한 'X' 투표 수")
    voted: bool = Field(..., description="현재 사용자가 이 퀴즈에 투표했는지 여부")
    postType: str = Field(..., description="게시물의 유형 (예: 'ox')")
    created_at: datetime = Field(..., description="퀴즈가 생성된 날짜와 시간")
    liked: bool = Field(..., description="현재 사용자가 이 퀴즈를 좋아요 했는지 여부")
    likeCount: int = Field(..., description="퀴즈에 대한 총 좋아요 수")
    
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

@router.get("/{targetUserId}", summary="리포스트(북마크) 조회하기", response_model=bookmarkListResponse)
async def search_item(targetUserId: str, userId: str = Header()):
    """
    북마크에 담은 포스트들을 조회하는 엔드포인트입니다.
    
    - **targetUserId**: 북마크를 조회할려는 user의 ID (필수) (parameter)

    - **userId**: 현재 접속중인 유저 이름 (parameter)
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
            o.content,
            o.author,
            o.created_at,
            o.o_count,
            o.x_count,
            CASE WHEN c.id IS NOT NULL THEN TRUE ELSE FALSE END AS voted,
            CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
            COALESCE(like_count_table.like_count, 0) AS like_count 
        FROM ox o
        JOIN `bookmark` b ON o.id = b.post_id
        LEFT JOIN `ox_check` c ON o.id = c.post_id AND c.user_id = %s
        LEFT JOIN `like` l ON o.id = l.post_id AND l.user_id = %s AND l.post_type = 'ox'
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count 
            FROM `like`
            WHERE post_type = 'ox'
            GROUP BY post_id
        ) AS like_count_table ON o.id = like_count_table.post_id 
        WHERE b.user_id = %s AND b.post_type = 'ox'
        """
        params = (userId, userId, targetUserId)
        # 쿼리 실행
        result = await database.execute_query(query, params)
        ox = [{"id": row['id'], "content": row['content'], "oCount": row["o_count"], "xCount": row["x_count"], "voted": row["voted"], "author": row["author"], "created_at": row["created_at"], "postType": "ox", "liked": row["liked"], "likeCount": row["like_count"]} for row in result]  
    
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
        params = (userId, targetUserId)
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