from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["test"],
    responses={404: {"description" : "Not Found"}},
)

# Pydantic 모델 정의
class qa(BaseModel):
    content: str
    author: str


@router.post("/qna", summary="Qna 글 생성")
async def create_item(text: qa):
    """
    데이터를 'qa' 테이블에 삽입하는 엔드포인트입니다.
    
    - **Content**: 게시글 내용

    - **Author**: 작성자 이름
    """
    print("데이터 삽입 시작")

    query = "INSERT INTO qa (content, author) VALUES (%s, %s)"
    params = (text.content, text.author)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data inserted successfully"}

class qa(BaseModel):
    id: int
    content: str
    author: str
    created_at: str


@router.get("/qna", summary="Qna 글 불러오기")
async def read_item():
    """
    데이터를 'qa' 테이블에서 불러오는 엔드포인트입니다.
    - **id**: 게시글 ID

    - **Content**: 게시글 내용

    - **Author**: 작성자 이름

    - **created_at**: 게시글 생성일
    """
    print("데이터 불러오기")

    query = "SELECT * FROM qa"
    
    # 쿼리 실행
    result = await database.execute_query(query)
    
    formatted_result = [{"id": row['id'], "content": row['content'], "author": row['author'], "created_at":row['created_at']} for row in result]
    return {"message": "Data loaded successfully", "result": formatted_result}



class qa(BaseModel):
    content: str

@router.put("/qna/{postID}", summary="Qna 글 업데이트")
async def create_item(postID: int, text: qa, user_id: str = Header()):
    """
    'qa' 테이블의 데이터를 id를 통해 불러와서 수정하는 엔드포인트입니다.
    
    - **id**: 게시글 id

    - **content**: 게시글 내용
    """

    query = "SELECT author FROM qa WHERE id = %s"
    params = (postID)
    author = await database.execute_query(query, params)
    if user_id != author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시물 삭제권한이 없습니다."
        )
    
    print("데이터 삽입 시작")

    query = "UPDATE qa SET content = %s WHERE id = %s"
    params = (text.content, postID)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data updated successfully"}



@router.delete("/qna/{postID}", summary="Qna 글 삭제")
async def create_item(postID: int, user_id: str = Header()):
    """
    'qa' 테이블의 데이터를 id를 통해 조회해서 삭제하는 엔드포인트입니다.
    
    - **id**: 게시글 id
    - **current_user**: 현재 접속중인 유저 이름
    """
    
    query = "SELECT author FROM qa WHERE id = %s"
    params = (postID)
    author = await database.execute_query(query, params)
    if user_id != author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시물 삭제권한이 없습니다."
        )
    
    print("데이터 삭제 시작")
    
    query = "DELETE FROM qa WHERE id = %s"
    params = (postID)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data deleted successfully"}