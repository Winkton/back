from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from database import database
from pydantic import BaseModel

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

# CORS 설정 (필요한 경우)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 일반적인 Endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 매개변수로 받기
@app.get("/{userID}")
async def get_user(userID: str):
    return {"userID": userID}

# Pydantic 모델 정의
class User(BaseModel):
    userID: int
    name: str
    email: str

# RequestBody로 받기
@app.post("/users/")
async def create_user(user: User):
    return {"userID": user.userID, "name": user.name, "email": user.email}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)