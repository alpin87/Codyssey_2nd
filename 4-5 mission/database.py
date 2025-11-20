# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 접속 주소
SQLALCHEMY_DATABASE_URL = 'sqlite:///./myapi.db'

# SQLite 설정 (check_same_thread: False 필수)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

# 세션 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 객체 생성 (이 부분이 없어서 에러가 난 것입니다)
Base = declarative_base()