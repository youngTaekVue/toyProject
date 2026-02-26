import tkinter as tk
from tkinter import messagebox
import sys
import os
from dotenv import load_dotenv
from app import ComplexLayoutApp
import database # DB 모듈 임포트

def on_closing(root):
    """애플리케이션 종료 시 호출될 함수"""
    print("Application closing.")
    root.destroy()

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()

    # 1. 애플리케이션 시작 전, DB 연결 테스트
    try:
        database.init_db_pool()
    except Exception as e:
        # DB 연결 실패 시
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("DB 연결 오류", f"데이터베이스에 연결할 수 없습니다.\n.env 설정을 확인해주세요.\n\n에러 내용: {e}")
        root.destroy()
        sys.exit(1)

    root = tk.Tk()
    try:
        # 앱 초기화 (여기서 API 연결 등을 시도하다가 에러가 날 수 있음)
        app = ComplexLayoutApp(root)
    except Exception as e:
        # 콘솔에 에러 출력 (디버깅용)
        print(f"앱 실행 중 오류 발생: {e}")

        # .env에서 API 정보 가져오기 (없으면 기본값 localhost:3000 사용)
        api_host = os.getenv("API_HOST", "localhost")
        api_port = os.getenv("API_PORT", "3000")

        root.withdraw()
        messagebox.showerror(
            "API 서버 연결 오류",
            f"API 서버({api_host}:{api_port})에 연결할 수 없습니다.\n"
            f"백엔드 서버가 실행 중인지, .env 설정이 올바른지 확인해주세요.\n\n"
            f"에러 내용: {e}"
        )
        root.destroy()
        sys.exit(1)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()