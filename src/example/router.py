from fastapi import APIRouter, HTTPException, status, Header
from database import database
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    tags=["profile"],
    responses={404: {"description" : "Not Found"}},
)
