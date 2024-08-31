from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import List, Optional
from pydantic import BaseModel
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
    id: int
    question: str
    answer: bool
    created_at: datetime

class OXListResponse(BaseModel):
    result: List[OXItem]
    
@router.get("", summary="OX 퀴즈 목록 받아오기", response_model=OXListResponse)
async def get_list(userId: Optional[str] = None):
    """
    OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
    - **userId**: 작성자 ID (선택) (str) (없으면 전체를 받아옵니다)
    """
    
    query = "SELECT * FROM ox"
    params = []
    
    if userId:
        query += " WHERE author = %s"
        params.append(userId)
        
    result = await database.execute_query(query, tuple(params)) 
    
    formatted_result = [{"id": row['id'], "question": row['question'], "answer": row['answer'], "created_at": row["created_at"]} for row in result]  
    
    return {"result": formatted_result}
    
@router.get("/following", summary="팔로잉한 사람들의 OX 퀴즈 목록 받아오기", response_model=OXListResponse)
async def get_list(user_id: str = Header()):
    """
    OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
    - **userId**: 작성자 ID (선택) (str) (없으면 전체를 받아옵니다)
    """
    
    query = """
    SELECT * 
    FROM ox o
    JOIN following f ON f.follower = o.author
    WHERE f.following = %s;
    """
    
    params = [user_id]
            
    result = await database.execute_query(query, tuple(params)) 
    
    formatted_result = [{"id": row['id'], "question": row['question'], "answer": row['answer'], "created_at": row["created_at"]} for row in result]  
    
    return {"result": formatted_result}
    
class OX(BaseModel):
    question: str
    answer: bool    

@router.post("", summary="OX 퀴즈 업로드", response_model= SuccessResponse)
async def getList(ox: OX, user_id: str = Header()):
    """
    OX 퀴즈를 업로드하는 EndPoint입니다.
    
    - **user_id**: 작성자 ID (필수) (str) (Header)
    - **question**: 질문할 문제 (필수) (str 100자 이하)
    - **answer**: 질문에 대한 답 (필수) (bool)
    """
    
    if len(ox.question) > 100 or len(ox.question) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(user_id) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    try:
        query = "INSERT INTO ox (author, question, answer) VALUES (%s, %s, %s)"
        params = (user_id, ox.question, ox.answer)
        
        await database.execute_query(query, params)
        
        return {"message": "Successfully Uploaded"}
    
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

class OXModify(BaseModel):
    question: str
    answer: bool

@router.put("/{postID}", summary="OX 퀴즈 수정", response_model= SuccessResponse)
async def modify(postID: int, ox: OXModify, user_id: str = Header()):
    """
    OX 퀴즈를 수정하는 EndPoint입니다.
    
    - **userID**: 작성자 ID (필수) (str) (Header)
    - **postID**: 글 ID (필수) (int) (Parameter)
    - **question**: 질문할 문제 (필수) (str 100자 이하)
    - **answer**: 질문에 대한 답 (필수) (bool)
    """
    
    if len(ox.question) > 100 or len(ox.question) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(user_id) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    query = "SELECT * FROM ox WHERE author = %s AND id = %s"
    params = (user_id, postID)   
    count = await database.execute_query(query, params)

    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 글에 수정 권한이 없습니다."
        )
        
    try:
        query = "UPDATE ox SET question = %s, answer = %s WHERE author = %s AND id = %s"
        params = (ox.question, ox.answer, user_id, postID)        
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
async def delete(postID: int, user_id: str = Header()):
    """
    'ox' 테이블의 데이터를 id를 통해 조회해서 삭제하는 엔드포인트입니다.
    
    - **postID**: 게시글 id (int)
    - **userID**: 작성자 ID (필수) (str) (Header)
    """
    
    query = "SELECT * FROM ox WHERE author = %s AND id = %s"
    params = (user_id, postID)   
    count = await database.execute_query(query, params)
    
    if len(count) == 0:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 글에 삭제 권한이 없거나 존재하지 않습니다."
        )
    
    query = "DELETE FROM ox WHERE id = %s AND author = %s"
    params = (postID, user_id)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data deleted successfully"}