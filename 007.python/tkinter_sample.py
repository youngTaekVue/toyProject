import tkinter as tk
from tkinter import ttk, messagebox
import json
#import requests # 실제 API 연동 시 사용

class ApiManager:
    """API 호출 및 테스트 데이터를 관리하는 클래스"""
    def __init__(self):
        self.DEBUG = True  # True: 테스트 데이터 사용 / False: 실제 REST API 사용
        self.BASE_URL = "https://api.example.com" # 실제 API 서버 주소

    def search_user_data(self, user_no):
        """유저 번호로 데이터 조회 (1111111 입력 시에만 데이터 반환)"""
        if self.DEBUG:
            # --- [테스트용 JSON 데이터 생성] ---
            if user_no == "1111111":
                return {
                    "status": 200,
                    "data": {
                        "user_id": "1111111",
                        "user_name": "테스터",
                        "school": "코딩대학교",
                        "status": "재학중"
                    }
                }
            else:
                return {"status": 404, "message": "해당 유저 번호를 찾을 수 없습니다."}
        else:
            # --- [실제 REST API 호출 주석] ---
            """
            try:
                response = requests.get(f"{self.BASE_URL}/users/{user_no}")
                return response.json()
            except Exception as e:
                return {"status": "error", "message": str(e)}
            """
            pass

    def get_complex_history(self, user_no, api_count=2):
        """복합 조회 시뮬레이션 (2개 이상의 API 결합)"""
        if self.DEBUG:
            if user_no == "1111111":
                # API 1 결과 (기본 정보)
                api1_res = {"basic_info": {"user_no": user_no, "point": 5000}}
                # API 2 결과 (수강 내역)
                api2_res = {
                    "courses": [
                        {"id": 101, "name": "파이썬 실전"},
                        {"id": 102, "name": "GUI 설계"}
                    ]
                }

                # 결과 합치기
                combined = {**api1_res, **api2_res}
                return {"status": 200, "result": combined}
            else:
                return {"status": 404, "message": "조회할 내역이 없습니다."}
        else:
            # --- [실제 REST API 연속 호출 주석] ---
            """
            # 첫 번째 호출
            res1 = requests.get(f"{self.BASE_URL}/info/{user_no}")
            # 두 번째 호출
            res2 = requests.get(f"{self.BASE_URL}/history/{user_no}")
            return {**res1.json(), **res2.json()}
            """
            pass

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("데이터 조회 시뮬레이터")
        self.root.geometry("600x650")
        self.api = ApiManager()

        self.setup_ui()

    def setup_ui(self):
        # 상단 입력창
        top_frame = ttk.LabelFrame(self.root, text="검색 조건")
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="유저번호 :").grid(row=0, column=0, padx=5, pady=10)
        self.ent_user_no = ttk.Entry(top_frame)
        self.ent_user_no.insert(0, "1111111") # 예시값 기본 입력
        self.ent_user_no.grid(row=0, column=1, padx=5, pady=10)

        # 메뉴 버튼들 (조회 영역)
        btn_frame = ttk.LabelFrame(self.root, text="기능 선택")
        btn_frame.pack(fill="x", padx=10, pady=5)

        # 그리드 배치
        ttk.Button(btn_frame, text="유저번호 찾기", command=self.handle_search).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="수강 1조회 (2개 API)", command=lambda: self.handle_complex_search(2)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="수강 2조회 (2개 API)", command=lambda: self.handle_complex_search(2)).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="수강 3조회 (3개 API)", command=lambda: self.handle_complex_search(3)).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # 결과 출력 (JSON 뷰어 스타일)
        ttk.Label(self.root, text="조회 결과 (JSON):").pack(anchor="w", padx=10)
        self.log_area = tk.Text(self.root, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 10))
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    def display_result(self, data):
        """결과 텍스트 영역에 JSON 포맷으로 출력"""
        self.log_area.delete("1.0", tk.END)
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
        self.log_area.insert(tk.END, pretty_json)

    def handle_search(self):
        user_no = self.ent_user_no.get().strip()
        result = self.api.search_user_data(user_no)
        self.display_result(result)

    def handle_complex_search(self, count):
        user_no = self.ent_user_no.get().strip()
        result = self.api.get_complex_history(user_no, count)
        self.display_result(result)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()