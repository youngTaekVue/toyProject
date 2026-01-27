import tkinter as tk
from app import ComplexLayoutApp
import database # DB 모듈 임포트

def on_closing(root):
    """애플리케이션 종료 시 호출될 함수"""
    # 커넥션 풀은 보통 앱 종료 시 자동으로 정리되므로 명시적 종료는 필수가 아닙니다.
    print("Application closing.")
    root.destroy()

if __name__ == "__main__":
    # 1. 애플리케이션 시작 전, DB 커넥션 풀 초기화
    database.init_db_pool()

    root = tk.Tk()
    app = ComplexLayoutApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()