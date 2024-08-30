from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
from io import BytesIO
import boto3 
import os
from datetime import datetime
import pytz

load_dotenv()

# S3 버킷 이름과 AWS 자격 증명 설정
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# S3 내 파일 업로드
# [file_name 형식]
#  1. 확장자와 함께 넘어온 경우. Input: address.xlsx -> address-YYYY-MM-DD.xlsx
#  2. 확장자 없이 넘어온 경우 ".xlsx" 추가. Input: address -> address-YYYY-MM-DD.xlsx 
async def upload_file(file: BytesIO, file_name: str):
    try:
        file_name_only, ext = split_file_name(file_name)
    
        # 현재 한국 시간 반환하여 파일 이름에 시간 등록
        korea_date = get_korea_date().strftime("%Y-%m-%d")
        
        # 현재 한국 시간과 파일명을 더함 ex)2024-07-03-***.xlsx
        file_name = file_name_only + "-" + korea_date + ext
        
        # S3에 파일 업로드
        s3_client.upload_fileobj(file, S3_BUCKET, file_name)

        # 파일의 S3 URL 생성
        file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"

        return file_url
    
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not available")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete credentials provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 현재 한국 시간 반환
def get_korea_date():
    seoul_tz = pytz.timezone('Asia/Seoul')
    korea_time = datetime.now(seoul_tz)
    return korea_time

def split_file_name(file_name:str):
    name_parts = file_name.split(".")

    # 확장자 없이 온 경우
    if len(name_parts) < 2:
        file_name_only = file_name
        ext = ".xlsx"
    
    # 확장자 포함해서 온 경우
    else:
        file_name_only = ".".join(name_parts[:-1])
        ext = "." + name_parts[-1]

    return file_name_only, ext