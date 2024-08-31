from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from database import database
from example import router as test_router
from Login import login
from ox import router as ox_router


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
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router.router, prefix="/api/test")
app.include_router(login.router, prefix="/api/login")
app.include_router(ox_router.router, prefix="/api/ox")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)