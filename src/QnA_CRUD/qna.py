from fastapi import APIRouter
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["test"],
    responses={404: {"description" : "Not Found"}},
)

# 일반적인 Endpoint
@router.get("/")
async def root():
    return {"message": "Hello World"}

# 매개변수로 받기
@router.get("/user/{userID}")
async def get_user(userID: str):
    return {"userID": userID}

# Pydantic 모델 정의
class qa(BaseModel):
    content: str
    author: str
# RequestBody로 받기
@router.post("/users/", summary="Requestbody로 받기 예제")
async def create_user(user: qa):
    return {"userID": user.userID, "name": user.name, "email": user.email}

# Query 날리기 예제1 (SELECT)
@router.get("/select", summary="Query 실행 예제 1번")
async def get_filtered_names(
    name: str,  # 첫 번째 필수 필터 값
    dd: Optional[str] = None  # 두 번째 선택적 필터 값
):
    """
    두 개의 필터 값을 사용하여 데이터를 검색하는 엔드포인트입니다.
    
    - **name**: 첫 번째 필터 값 (필수)
    - **dd**: 두 번째 필터 값 (선택)
    """
    print("쿼리 실행")
    
    # 여러 조건을 가진 쿼리 생성
    query = "SELECT * FROM test WHERE name = %s"
    params = [name]  # 첫 번째 필터 값을 파라미터로 설정
    
    # 두 번째 필터 값이 있는 경우 쿼리에 추가
    if dd:
        query += " AND dd = %s"
        params.append(dd)
    
    # 쿼리 실행
    result = await database.execute_query(query, tuple(params))  # 파라미터를 튜플로 변환하여 전달
    
    # 결과가 있는 경우 모든 필드를 포함한 리스트로 반환
    formatted_result = [{"name": row['name'], "dd": row['dd'], "id": row['ff']} for row in result]  # 모든 필드를 포함
    
    return {"result": formatted_result}

# Pydantic 모델 정의

# Query 날리기 예제 2 (INSERT)
@router.post("/insert", summary="Query 실행 예제 2번")
async def insert_item(item: qa):
    """
    데이터를 'test' 테이블에 삽입하는 엔드포인트입니다.
    
    - **name**: 이름 (필수)
    - **dd**: 숫자 (선택)
    - **ff**: ID (필수)
    """
    print("데이터 삽입 시작")

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



@router.post("/qna/create", summary="Qna 글 생성")
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


@router.get("/qna/read", summary="Qna 글 불러오기")
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
    id: int
    content: str

@router.post("/qna/update", summary="Qna 글 업데이트")
async def create_item(text: qa):
    """
    'qa' 테이블의 데이터를 id를 통해 불러와서 수정하는 엔드포인트입니다.
    
    - **id**: 게시글 id

    - **content**: 게시글 내용
    """
    print("데이터 삽입 시작")

    query = "UPDATE qa SET content = %s WHERE id = %s"
    params = (text.content, text.id)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data updated successfully"}

class qa(BaseModel):
    id: int

@router.post("/qna/delete", summary="Qna 글 삭제")
async def create_item(text: qa):
    """
    'qa' 테이블의 데이터를 id를 통해 조회해서 삭제하는 엔드포인트입니다.
    
    - **id**: 게시글 id
    """
    print("데이터 삭제 시작")

    query = "DELETE FROM qa WHERE id = %s"
    params = (text.id)
    
    # 쿼리 실행
    await database.execute_query(query, params)
    
    return {"message": "Data deleted successfully"}