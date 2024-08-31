from fastapi import APIRouter, HTTPException, status
from database import database
from typing import List, Optional
from pydantic import BaseModel

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

@router.get("", summary="OX 퀴즈 목록 받아오기")
async def get_list(id: Optional[str] = None):
    """
    OX 퀴즈 목록을 받아오는 EndPoint입니다.
    
    - **id**: 쉼표로 구분된 작성자 ID 리스트 (선택) (str) (없으면 전체를 받아옵니다)
    """
    
    query = "SELECT * FROM ox"
    params = []
    
    if id:
        query += " WHERE author = %s"
        params.append(id)
        
    result = await database.execute_query(query, tuple(params)) 
    
    formatted_result = [{"id": row['id'], "question": row['question'], "answer": row['answer'], "created_at": row["created_at"]} for row in result]  
    
    return {"result": formatted_result}
    
class OX(BaseModel):
    userID: str
    question: str
    answer: bool

@router.post("", summary="OX 퀴즈 업로드")
async def getList(ox: OX):
    """
    OX 퀴즈를 업로드하는 EndPoint입니다.
    
    - **userID**: 작성자 ID (필수) (str)
    - **question**: 질문할 문제 (필수) (str 100자 이하)
    - **answer**: 질문에 대한 답 (필수) (bool)
    """
    
    if len(ox.question) > 100 or len(ox.question) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(ox.userID) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    try:
        query = "INSERT INTO ox (author, question, answer) VALUES (%s, %s, %s)"
        params = (ox.userID, ox.question, ox.answer)
        
        await database.execute_query(query, params)
        
        return {"message": "Successfully Uploaded"}
    
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )

class OXModify(BaseModel):
    postID: int
    userID: str
    question: str
    answer: bool

@router.put("", summary="OX 퀴즈 수정")
async def modify(ox: OXModify):
    """
    OX 퀴즈를 수정하는 EndPoint입니다.
    
    - **
    - **userID**: 작성자 ID (필수) (str)
    - **question**: 질문할 문제 (필수) (str 100자 이하)
    - **answer**: 질문에 대한 답 (필수) (bool)
    """
    
    if len(ox.question) > 100 or len(ox.question) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="질문 길이는 반드시 1자 이상 100이하여야 됩니다."
        )
        
    if len(ox.userID) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성자는 필수입니다."
        )
        
    query = "SELECT * FROM ox WHERE author = %s AND id = %s"
    params = (ox.userID, ox.postID)   
    count = await database.execute_query(query, params)
    
    if count == 0:  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 글에 수정 권한이 없습니다."
        )
        
    try:
        query = "UPDATE ox SET question = %s, answer = %s WHERE author = %s AND id = %s"
        params = (ox.question, ox.answer, ox.userID, ox.postID)        
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
