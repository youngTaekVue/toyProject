import os
import pymysql
from dotenv import load_dotenv

# DB 접속 정보를 담을 전역 딕셔너리
db_config = {}

def init_db_pool():
    """
    애플리케이션 시작 시 DB 연결을 테스트하고 설정을 저장합니다.
    main.py에서 한 번만 호출됩니다.
    """
    global db_config

    # .env 파일에서 환경 변수 로드
    load_dotenv()

    # .env 파일의 정보로 db_config 딕셔너리 채우기
    db_config = {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': int(os.getenv("DB_PORT", 3306)),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'db': os.getenv("DB_NAME"),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 설정된 정보로 DB 연결 테스트
    try:
        # 연결 테스트 후 바로 닫기
        conn = pymysql.connect(**db_config)
        conn.close()
        print("Database connection configured and tested successfully.")
    except Exception as e:
        print(f"Database configuration test failed: {e}")
        # 에러를 다시 발생시켜 main.py의 예외 처리 로직이 동작하도록 함
        raise e

def get_db_connection():
    """
    DB 작업이 필요할 때마다 새로운 커넥션을 생성하여 반환합니다.
    """
    if not db_config:
        # 만약 init_db_pool이 호출되지 않았다면, 여기서 초기화 시도
        try:
            init_db_pool()
        except Exception:
            raise Exception("Database is not configured. Call init_db_pool() first.")

    # 저장된 설정으로 새로운 커넥션 생성
    return pymysql.connect(**db_config)