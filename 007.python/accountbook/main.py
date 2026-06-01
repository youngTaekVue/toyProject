import tkinter as tk
from tkinter import messagebox
import sys
import os
from dotenv import load_dotenv
from app import ComplexLayoutApp
import subprocess
import time
import requests

# Removed direct database import as it will be handled by the backend API

# Ensure the backend directory is in the path for subprocess
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
BACKEND_API_PATH = os.path.join(BACKEND_DIR, 'api.py')

def on_closing(root, backend_process):
    """애플리케이션 종료 시 호출될 함수"""
    print("Application closing.")
    if backend_process:
        print("Terminating backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("Backend server terminated.")
    root.destroy()

def start_backend_server():
    """Flask 백엔드 서버를 별도의 프로세스로 시작합니다."""
    # Ensure .env is loaded for the backend process as well
    load_dotenv()
    api_host = os.getenv("API_HOST", "127.0.0.1") # Use 127.0.0.1 for local
    api_port = os.getenv("API_PORT", "5000")

    print(f"Starting backend server at http://{api_host}:{api_port}...")
    # Use pythonw.exe to run the backend without opening a new console window on Windows
    # For Linux/macOS, just 'python' is fine.
    python_executable = sys.executable
    if sys.platform == "win32":
        python_executable = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

    # Pass environment variables to the subprocess
    env = os.environ.copy()
    env["FLASK_APP"] = BACKEND_API_PATH
    env["FLASK_RUN_HOST"] = api_host
    env["FLASK_RUN_PORT"] = api_port

    # Use Popen to start the process in the background
    process = subprocess.Popen(
        [python_executable, BACKEND_API_PATH],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0 # Hide console window on Windows
    )

    # Wait for the server to start (optional, but good for robustness)
    for _ in range(10): # Try for 10 seconds
        try:
            response = requests.get(f"http://{api_host}:{api_port}/")
            if response.status_code == 200:
                print("Backend server started successfully.")
                return process
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("Warning: Backend server might not have started correctly.")
    return process

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()

    backend_process = None
    try:
        # Start the backend server
        backend_process = start_backend_server()

        root = tk.Tk()
        # Set API_BASE_URL for the frontend
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "5000")
        os.environ["API_BASE_URL"] = f"http://{api_host}:{api_port}"

        # App initialization
        app = ComplexLayoutApp(root)

        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, backend_process))
        root.mainloop()

    except Exception as e:
        # Console error for debugging
        print(f"App execution error: {e}")

        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "5000")

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API 서버 연결 오류",
            f"API 서버(http://{api_host}:{api_port})에 연결할 수 없습니다.\n"
            f"백엔드 서버가 실행 중인지, .env 설정이 올바른지 확인해주세요.\n\n"
            f"에러 내용: {e}"
        )
        root.destroy()
        sys.exit(1)
    finally:
        if backend_process and backend_process.poll() is None: # If still running
            print("Terminating backend server in finally block...")
            backend_process.terminate()
            backend_process.wait()
            print("Backend server terminated.")
