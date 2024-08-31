from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    tags=["qna"],
    responses={404: {"description" : "Not Found"}},
)

# Pydantic 모델 정의
class qa(BaseModel):
    content: str

class qaListResponse(BaseModel):
    result: List[qa]

@router.post("", summary="Qna 글 생성")
async def create_item(text: qa, Authorization: str = Header()):
    """
    데이터를 'qa' 테이블에 삽입하는 엔드포인트입니다.
    
    - **Content**: 게시글 내용

    - **Authorization**: 작성자 이름 (parameter)
    """
    print("데이터 삽입 시작")
    if len(text.content)<=0 or len(text.content)>1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="글 내용은 1글자 이상 1000글자 이하여야 합니다."
        )
    

    try:
        query = "INSERT INTO qa (content, author) VALUES (%s, %s)"
        params = (text.content, Authorization)
    
      # 쿼리 실행
        await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {"content":text.content}

class qa(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime
    postType: str
    liked: bool
    likeCount: int

class qaListResponse(BaseModel):
    result: List[qa]

@router.get("", summary="Qna 글 불러오기", response_model=qaListResponse)
async def read_item(userId: Optional[str] = None, user_id: str = Header()):
    """
    데이터를 'qa' 테이블에서 불러오는 엔드포인트입니다.
    
    - **userId**: 작성자 ID (선택) (str) (없으면 전체를 받아옵니다)
    - **user_id**: 현재 접속중인 유저 ID (필수) (str) (Header)
    """

    try:
        query = """
        SELECT
            q.id, 
            q.content, 
            q.author, 
            q.created_at,
            CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
            COALESCE(like_count_table.like_count, 0) AS like_count 
        FROM qa q
        LEFT JOIN `like` l ON q.id = l.post_id AND l.user_id = %s AND post_type = 'qa'
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count 
            FROM `like`
            WHERE post_type = 'qa'
            GROUP BY post_id
        ) AS like_count_table ON q.id = like_count_table.post_id 
        """
        params = [user_id]
        
        if userId:
            query += " WHERE q.author = %s"
            params.append(userId)
        
        # 쿼리 실행
        result = await database.execute_query(query, params)
        formatted_result = [{"id": row['id'], "content": row['content'], "author": row['author'], "postType": "qa", "created_at":row['created_at'], "liked": row["liked"], "likeCount": row["like_count"]} for row in result]
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {
        "result": formatted_result
    }
    
@router.get("/following", summary="Qna 글 불러오기", response_model=qaListResponse)
async def read_item(Authorization: str = Header()):
    """
    팔로잉한 사람들의 Q&A 목록을 받아오는 EndPoint입니다.
    
    - **Authorization**: 현재 접속중인 유저 ID (필수) (str) (Header)
    """
    
    try:
        query = """
        SELECT
            q.id, 
            q.content, 
            q.author, 
            q.created_at,
            CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
            COALESCE(like_count_table.like_count, 0) AS like_count 
        FROM qa q
        JOIN following f ON f.follower = q.author
        LEFT JOIN `like` l ON q.id = l.post_id AND l.user_id = %s AND post_type = 'qa'
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count 
            FROM `like`
            WHERE post_type = 'qa'
            GROUP BY post_id
        ) AS like_count_table ON q.id = like_count_table.post_id 
        WHERE f.following = %s;
        """
        
        params = [Authorization, Authorization]
        
        result = await database.execute_query(query, tuple(params)) 
        formatted_result = [{"id": row['id'], "content": row['content'], "author": row['author'], "postType": "qa", "created_at":row['created_at'], "liked": row["liked"], "likeCount": row["like_count"]} for row in result]
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {
        "result": formatted_result
    }

class qa(BaseModel):
    content: str

class qaListResponse(BaseModel):
    result: List[qa]

@router.put("/{postID}", summary="Qna 글 업데이트")
async def update_item(postID: int, text: qa, Authorization: str = Header()):
    """
    'qa' 테이블의 데이터를 id를 통해 불러와서 수정하는 엔드포인트입니다.
    
    - **postID**: 게시글 id (parameter)

    - **Authorization**: 현재 접속중인 유저 ID (필수) (str) (Header)

    - **content**: 게시글 내용
    """

    if len(text.content)<=0 or len(text.content)>1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="글 내용은 1글자 이상 1000글자 이하여야 합니다."
        )
    
    query = "SELECT author FROM qa WHERE id = %s"
    params = (postID)
    author = await database.execute_query(query, params)
    print(Authorization)
    print(author)
    if Authorization != author[0]['author']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시물 삭제권한이 없습니다."
        )
    
    print("데이터 삽입 시작")

    try:
        query = "UPDATE qa SET content = %s WHERE id = %s"
        params = (text.content, postID)
    
        # 쿼리 실행
        await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    return {"content":text.content}

@router.delete("/{postID}", summary="Qna 글 삭제")
async def delete_item(postID: int, Authorization: str = Header()):
    """
    'qa' 테이블의 데이터를 id를 통해 조회해서 삭제하는 엔드포인트입니다.
    
    - **postID**: 게시글 id (parameter)

    - **Authorization**: 현재 접속중인 유저 ID (필수) (str) (Header)
    """
    
    query = "SELECT author FROM qa WHERE id = %s"
    params = (postID)
    author = await database.execute_query(query, params)
    if Authorization != author[0]['author']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시물 삭제권한이 없습니다."
        )
    
    print("데이터 삭제 시작")
    
    try:
        query = "DELETE FROM qa WHERE id = %s"
        params = (postID)
    
        # 쿼리 실행
        await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
    
    
    
    return {"message": "Data deleted successfully"}