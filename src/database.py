import os
from dotenv import load_dotenv
import asyncpg
from typing import Optional
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

if None in (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME):
    raise ValueError(".env에 DB 환경변수 셋팅이 제대로 진행되지 않았습니다.")

class Database:
    def __init__(self):
        self._conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        self._conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT 
        )
        logging.info("DB 연결 완료")

    async def disconnect(self):
        if self._conn:
            await self._conn.close()
            logging.info("DB 연결 해제 완료")

    @property
    def connection(self) -> Optional[asyncpg.Connection]:
        return self._conn

database = Database()