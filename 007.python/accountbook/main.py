import tkinter as tk
from tkinter import messagebox
import sys
import os
from dotenv import load_dotenv
from app import ComplexLayoutApp
import requests # Used for API connection test

# Removed direct database import and Python backend subprocess handling

def on_closing(root):
    """애플리케이션 종료 시 호출될 함수"""
    print("Application closing.")
    root.destroy()

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()

    # Set API_BASE_URL for the frontend to point to the Node.js backend
    # The Node.js backend is expected to be running on localhost:3000
    api_host = os.getenv("API_HOST", "localhost")
    api_port = os.getenv("API_PORT", "3000") # Changed to 3000 for Node.js backend
    os.environ["API_BASE_URL"] = f"http://{api_host}:{api_port}/python" # Added /python prefix for the router

    # Test API connection
    try:
        # Test a simple endpoint, e.g., the root of the python router
        test_url = f"{os.environ['API_BASE_URL']}/transactions" # Use a specific endpoint for testing
        response = requests.get(test_url, timeout=5) # 5-second timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        print(f"Successfully connected to Node.js backend API at {os.environ['API_BASE_URL']}")
    except requests.exceptions.RequestException as e:
        # API connection failed
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API 서버 연결 오류",
            f"Node.js API 서버(http://{api_host}:{api_port})에 연결할 수 없습니다.\n"
            f"백엔드 서버가 실행 중인지, .env 설정이 올바른지 확인해주세요.\n\n"
            f"에러 내용: {e}"
        )
        root.destroy()
        sys.exit(1)

    root = tk.Tk()
    try:
        # App initialization
        app = ComplexLayoutApp(root)
    except Exception as e:
        # Console error for debugging
        print(f"앱 실행 중 오류 발생: {e}")

        root.withdraw()
        messagebox.showerror(
            "앱 실행 오류",
            f"애플리케이션 실행 중 오류가 발생했습니다.\n\n"
            f"에러 내용: {e}"
        )
        root.destroy()
        sys.exit(1)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()
