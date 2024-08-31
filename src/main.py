from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from database import database
from example import router as test_router
from QnA_CRUD import qna
from ox import router as ox_router
from following import router as following_router

from like import like
from Auth import login

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("하이")
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# CORS 설정 (필요한 경우)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router.router, prefix="/api/test")
app.include_router(login.router, prefix="/api/auth")
app.include_router(qna.router, prefix="/api/qna")
app.include_router(ox_router.router, prefix="/api/ox")
app.include_router(following_router.router, prefix="/api/follow")
app.include_router(like.router, prefix="/api/like")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)