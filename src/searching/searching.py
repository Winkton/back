from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["searching"],
    responses={404: {"description" : "Not Found"}},
)

@router.get("", summary="유저 검색 시 팔로우 여부")
async def user_search(userId: str = Header()):
    """
    유저의 팔로우 여부를 검색 시에 보여주는 엔드포인트입니다.

    - **userId**: 현재 접속중인 유저 이름 (parameter)

    """
    print("데이터 조회 시작")
    if len(userId)<=0 or len(userId)>25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유저 이름은 1글자 이상 25글자 이하여야 합니다."
        )
    
    try:
        query = """
                SELECT 
                    u.id, 
                    u.name, 
                    CASE 
                        WHEN f.follower IS NOT NULL THEN TRUE 
                        ELSE FALSE 
                    END AS followed
                FROM user u
                LEFT JOIN following f 
                    ON u.id = f.follower 
                    AND f.following = %s -- 특정 사용자가 팔로우하는지 확인할 사용자 ID
                """
                
        
        params = (userId,)  # 특정 사용자를 팔로우하는지 확인할 사용자 ID

        # 쿼리 실행
        result = await database.execute_query(query, params)

        # 쿼리 결과 출력 또는 반환
        response = [{"id": row["id"], "name": row["name"], "followed": bool(row["followed"])} for row in result]
        return {"userList": response}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="예상치 못한 오류가 발생했습니다."
        )