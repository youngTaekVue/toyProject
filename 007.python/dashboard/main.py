import tkinter as tk
from tkinter import messagebox
import sys
from app import ComplexLayoutApp
import database # DB 모듈 임포트

def on_closing(root):
    """애플리케이션 종료 시 호출될 함수"""
    # 커넥션 풀은 보통 앱 종료 시 자동으로 정리되므로 명시적 종료는 필수가 아닙니다.
    print("Application closing.")
    root.destroy()

if __name__ == "__main__":
    # 1. 애플리케이션 시작 전, DB 커넥션 풀 초기화
    try:
        database.init_db_pool()
    except Exception as e:
        # DB 연결 실패 시 GUI 창을 띄워 사용자에게 알림
        root = tk.Tk()
        root.withdraw() # 메인 윈도우 숨김
        messagebox.showerror("DB 연결 오류", f"데이터베이스에 연결할 수 없습니다.\n서버가 실행 중인지 확인해주세요.\n\n에러 내용: {e}")
        root.destroy()
        sys.exit(1)

    root = tk.Tk()
    try:
        app = ComplexLayoutApp(root)
    except Exception as e:
        # API 서버(포트 3000) 연결 실패 시 예외 처리
        root.withdraw()
        messagebox.showerror("API 서버 연결 오류", f"서버(localhost:3000)에 연결할 수 없습니다.\n백엔드 서버가 실행 중인지 확인해주세요.\n\n에러 내용: {e}")
        root.destroy()
        sys.exit(1)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()