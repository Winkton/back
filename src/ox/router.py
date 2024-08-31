from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(
    tags=["OX 게시판"],
    responses={404: {"description" : "Not Found"}},
)

# @router.get("/")
# async def get_list(id: Optional[str] = None):
#     """
#     OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
#     - **id**: 쉼표로 구분된 작성자 ID 리스트 (선택) (str) (없으면 전체를 받아옵니다)
#     """
    
#     # 기본 쿼리 정의 (id가 없는 경우 모든 레코드를 가져옴)
#     query = "SELECT * FROM ox"
#     params = []
    
#     # id 리스트가 제공된 경우, 쿼리에 조건 추가
#     if id:
#         # 쉼표로 구분된 id 문자열을 리스트로 변환
#         id_list = id.split(',')
#         # id 개수에 맞게 플레이스홀더를 생성하고 파라미터를 추가
#         placeholders = ', '.join(['%s'] * len(id_list))  # '%s'를 id의 개수만큼 생성
#         query += f" WHERE author IN ({placeholders})"
#         params.extend(id_list)  # id 리스트의 값들을 파라미터로 추가
    
#     # 쿼리 실행
#     try:
#         result = await database.execute_query(query, tuple(params))  # 파라미터를 튜플로 변환하여 전달
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Database query failed")
    
#     # 결과가 있는 경우 모든 필드를 포함한 리스트로 반환
#     formatted_result = [{"question": row['question'], "answer": row['answer'], "author": row['author']} for row in result]  # 모든 필드를 포함
    
#     return formatted_result

class SuccessResponse(BaseModel):
    message: str

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

class OXListResponse(BaseModel):
    result: List[OXItem] = Field(..., description="OX 퀴즈 항목의 목록")

@router.get("", summary="OX 퀴즈 목록 받아오기", response_model=OXListResponse)
async def get_list(targetUserId: Optional[str] = None, userId: str = Header()):
    """
    OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
    - **targetUserId**: 작성자 ID (선택) (str) (없으면 전체를 받아옵니다)
    - **userId**: 현재 접속중인 유저 ID (필수) (str) (Header)
    """
    
    query = """
    SELECT 
        o.id, 
        o.content, 
        o.author,
        o.o_count,
        o.x_count,
        o.created_at,
        CASE WHEN c.id IS NOT NULL THEN TRUE ELSE FALSE END AS voted,
        CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,
        COALESCE(like_count_table.like_count, 0) AS like_count 
    FROM ox o
    LEFT JOIN `ox_check` c ON o.id = c.post_id AND c.user_id = %s
    LEFT JOIN `like` l ON o.id = l.post_id AND l.user_id = %s AND post_type = 'ox'
    LEFT JOIN (
        SELECT post_id, COUNT(*) AS like_count 
        FROM `like`
        WHERE post_type = 'ox'
        GROUP BY post_id
    ) AS like_count_table ON o.id = like_count_table.post_id 
    """
    params = [userId, userId]
    
    if targetUserId:
        query += " WHERE o.author = %s"
        params.append(targetUserId)
    
    result = await database.execute_query(query, tuple(params))
    
    formatted_result = [{"id": row['id'], "content": row['content'], "oCount": row["o_count"], "xCount": row["x_count"], "voted": row["voted"], "author": row["author"], "created_at": row["created_at"], "postType": "ox", "liked": row["liked"], "likeCount": row["like_count"]} for row in result]  
    
    return {"result": formatted_result}
    
@router.get("/following", summary="팔로잉한 사람들의 OX 퀴즈 목록 받아오기", response_model=OXListResponse)
async def get_list(userId: str = Header()):
    """
    OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
    - **userId**: 로그인한 유저 ID (필수) (str) (Header)
    """
    
    query = """
    SELECT 
        o.id, 
        o.content, 
        o.author,
        o.o_count,
        o.x_count,
        o.created_at,
        CASE WHEN c.id IS NOT NULL THEN TRUE ELSE FALSE END AS voted,
        CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,  
        COALESCE(like_count_table.like_count, 0) AS like_count 
    FROM ox o
    JOIN following f ON f.follower = o.author  
    LEFT JOIN `ox_check` c ON o.id = c.post_id AND c.user_id = %s
    LEFT JOIN `like` l ON o.id = l.post_id AND l.user_id = %s AND post_type = 'ox'
    LEFT JOIN (
        SELECT post_id, COUNT(*) AS like_count 
        FROM `like`
        WHERE post_type = 'ox'
        GROUP BY post_id
    ) AS like_count_table ON o.id = like_count_table.post_id 
    WHERE f.following = %s;  
    """

    params = [userId,userId, userId]
            
    result = await database.execute_query(query, tuple(params)) 
    
    formatted_result = [{"id": row['id'], "content": row['content'], "oCount": row["o_count"], "xCount": row["x_count"], "voted": row["voted"], "author": row["author"], "created_at": row["created_at"], "postType": "ox", "liked": row["liked"], "likeCount": row["like_count"]} for row in result]  
    
    return {"result": formatted_result}
    
class OX(BaseModel):
    content: str  

@router.post("", summary="OX 퀴즈 업로드", response_model= SuccessResponse)
async def getList(ox: OX, userId: str = Header()):
    """
    OX 퀴즈를 업로드하는 EndPoint입니다.
    
    - **userId**: 현재 접속중인 유저 ID (필수) (str) (Header)
    - **content**: 질문할 문제 (필수) (str 100자 이하)
    """
    
    if len(ox.content) > 100 or len(ox.content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(userId) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    try:
        query = "INSERT INTO ox (author, content) VALUES (%s, %s)"
        params = (userId, ox.content)
        
        await database.execute_query(query, params)
        
        return {"message": "Successfully Uploaded"}
    
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

class OXModify(BaseModel):
    content: str

@router.put("/{postID}", summary="OX 퀴즈 수정", response_model= SuccessResponse)
async def modify(postID: int, ox: OXModify, userId: str = Header()):
    """
    OX 퀴즈를 수정하는 EndPoint입니다.
    
    - **userId**: 현재 접속중인 유저 ID (필수) (str) (Header)
    - **postID**: 글 ID (필수) (int) (Parameter)
    - **content**: 질문할 문제 (필수) (str 100자 이하)
    """
    
    if len(ox.content) > 100 or len(ox.content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(userId) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    query = "SELECT * FROM ox WHERE author = %s AND id = %s"
    params = (userId, postID)   
    count = await database.execute_query(query, params)

    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 글에 수정 권한이 없습니다."
        )
        
    try:
        query = "UPDATE ox SET content = %s WHERE author = %s AND id = %s"
        params = (ox.content, userId, postID)        
        affected_rows = await database.execute_query(query, params)
                
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )
        
    if affected_rows == 0:  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 글이 없습니다."
        )

    return {"message": "Successfully Modified"}

@router.delete("/{postID}", summary="OX 퀴즈 수정", response_model= SuccessResponse)
async def delete(postID: int, userId: str = Header()):
    """
    'ox' 테이블의 데이터를 id를 통해 조회해서 삭제하는 엔드포인트입니다.
    
    - **postID**: 게시글 id (int)
    - **userId**: 현재 접속중인 유저 ID (필수) (str) (Header)
    """
    
    query = "SELECT * FROM ox WHERE author = %s AND id = %s"
    params = (userId, postID)   
    count = await database.execute_query(query, params)
    
    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 글에 삭제 권한이 없거나 존재하지 않습니다."
        )
    
    query = "DELETE FROM ox WHERE id = %s AND author = %s"
    params = (postID, userId)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data deleted successfully"}

class OXVote(BaseModel):
    vote: bool
    
class OXListResponse(BaseModel):
    message: str
    oCount: int
    xCount: int 

@router.post("/vote/{postId}", summary="OX 퀴즈 투표", response_model=OXListResponse)
async def getList(postId: int, vote: OXVote, userId: str = Header()):
    """
    OX 퀴즈에 투표하는 EndPoint입니다.
    
    - **userId**: 현재 접속중인 유저 ID (필수) (str) (Header)
    - **postId**: 투표할 퀴즈의 ID (필수) (int) (Parameter)
    - **vote**: 사용자가 선택한 투표 (True: 'O', False: 'X')
    """
    
    query = "SELECT * FROM ox WHERE id = %s"
    params = (postId)
    result = await database.execute_query(query, params)
    
    if len(result) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 퀴즈가 존재하지 않습니다."
        )
        
    query = "SELECT * FROM `ox_check` WHERE post_id = %s AND user_id = %s"
    params = (postId, userId)
    result = await database.execute_query(query, params)
    
    if len(result) == 0:
        query = "INSERT INTO ox_check (user_id, post_id, vote) VALUES (%s, %s, %s)"
        params = (userId, postId, vote.vote)
        result = await database.execute_query(query, params)
        
        if vote.vote:  
            update_query = "UPDATE ox SET o_count = o_count + 1 WHERE id = %s"
        else:  
            update_query = "UPDATE ox SET x_count = x_count + 1 WHERE id = %s"
            
        await database.execute_query(update_query, (postId,))
        
        query = "SELECT o_count, x_count FROM ox WHERE id = %s"
        params = (postId)
        result = await database.execute_query(query, params)
        
        return {"message": "Voted successfully", "oCount": result[0]['o_count'], "xCount": result[0]['x_count']}
    else:
        if result[0]['vote']:  
            update_query = "UPDATE ox SET o_count = o_count - 1 WHERE id = %s"
        else:  
            update_query = "UPDATE ox SET x_count = x_count - 1 WHERE id = %s"
        
        await database.execute_query(update_query, (postId,))
            
        query = "DELETE FROM ox_check WHERE user_id = %s AND post_id = %s"
        params = (userId, postId)
        result = await database.execute_query(query, params)
        
        query = "SELECT o_count, x_count FROM ox WHERE id = %s"
        params = (postId)
        result = await database.execute_query(query, params)
        
        return {"message": "Voted Canceled successfully", "oCount": result[0]['o_count'], "xCount": result[0]['x_count']}

@router.get("/detail/{postID}")
async def get_ox_detail(postID: str, userId: str = Header()):
    query = """
    SELECT 
        o.id, 
        o.content, 
        o.author,
        o.o_count,
        o.x_count,
        o.created_at,
        CASE WHEN c.id IS NOT NULL THEN TRUE ELSE FALSE END AS voted,
        CASE WHEN l.id IS NOT NULL THEN TRUE ELSE FALSE END AS liked,
        COALESCE(like_count_table.like_count, 0) AS like_count 
    FROM ox o
    LEFT JOIN `ox_check` c ON o.id = c.post_id AND c.user_id = %s
    LEFT JOIN `like` l ON o.id = l.post_id AND l.user_id = %s AND post_type = 'ox'
    LEFT JOIN (
        SELECT post_id, COUNT(*) AS like_count 
        FROM `like`
        WHERE post_type = 'ox'
        GROUP BY post_id
    ) AS like_count_table ON o.id = like_count_table.post_id
    WHERE o.id = %s 
    """
    params = [userId, userId, postID]

    result = await database.execute_query(query, params)
    
    formatted_result = [{"id": row['id'], "content": row['content'], "oCount": row["o_count"], "xCount": row["x_count"], "voted": row["voted"], "author": row["author"], "created_at": row["created_at"], "postType": "ox", "liked": row["liked"], "likeCount": row["like_count"]} for row in result]  
    
    return {"result": formatted_result}
    