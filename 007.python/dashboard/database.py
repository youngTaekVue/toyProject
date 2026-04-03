import mysql.connector.pooling
import os
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트 경로에 있는 .env 파일을 찾습니다)
# 현재 파일 위치: dashboard/database.py -> 상위 폴더(dashboard) -> 상위 폴더(007.python) -> .env
# load_dotenv()는 기본적으로 현재 디렉토리나 상위 디렉토리에서 .env를 찾습니다.
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_DASH_HOST", "localhost"),
    "user": os.getenv("DB_DASH_USER", "root"),
    "password": os.getenv("DB_DASH_PASSWORD", ""),
    "database": os.getenv("DB_DASH_NAME", "test_db")
}

# 풀 사이즈도 환경 변수에서 가져오거나 기본값 사용
POOL_SIZE = int(os.getenv("DB_DASH_POOL_SIZE", 5))

db_pool = None

def init_db_pool():
    """애플리케이션 시작 시 호출되어 DB 커넥션 풀을 생성합니다."""
    global db_pool
    # 예외를 상위(main.py)로 전파하기 위해 try-except 제거
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=POOL_SIZE,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print(f"Database connection pool created successfully. (Host: {DB_CONFIG['host']}, DB: {DB_CONFIG['database']})")

def get_db_connection():
    """커넥션 풀에서 커넥션을 가져옵니다."""
    if db_pool is None:
        # 풀이 초기화되지 않았으면 초기화 시도
        init_db_pool()
        if db_pool is None:
             raise Exception("Database pool could not be initialized.")
    
    return db_pool.get_connection()