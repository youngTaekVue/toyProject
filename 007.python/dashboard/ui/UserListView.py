import tkinter as tk
from tkinter import ttk
import requests # API 호출을 위한 requests 모듈

class UserListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.all_data = []
        # API 엔드포인트 설정 (실제 서버 주소로 변경 필요)
        self.api_url = "http://localhost:3000/python/userInfo"
        self.setup_ui()
        self.load_data_from_api() # UI 생성 후 API에서 데이터 로드

    def setup_ui(self):
        # 상단 프레임 (타이틀 + 검색창)
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=10, pady=(10, 0))

        lbl_header = ttk.Label(top_frame, text="전체 사용자 목록", font=("맑은 고딕", 14, "bold"))
        lbl_header.pack(side="left")

        # 검색 UI (오른쪽 정렬)
        ttk.Button(top_frame, text="조회", command=self.search_data).pack(side="right")
        self.ent_search = ttk.Entry(top_frame, width=20)
        self.ent_search.pack(side="right", padx=5)
        self.ent_search.bind("<Return>", lambda event: self.search_data()) # 엔터키로도 조회 가능
        ttk.Label(top_frame, text="검색:").pack(side="right")


        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        # API 응답 데이터 구조에 맞춰 컬럼 설정
        columns = ("id", "userId", "userNm", "content")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("id", text="ID")
        self.tree.heading("userId", text="이름")
        self.tree.heading("userNm", text="이메일")
        self.tree.heading("content", text="가입일")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("userId", width=100)
        self.tree.column("userNm", width=200)
        self.tree.column("content", width=100, anchor="center")

    def load_data_from_api(self, keyword=None):
        """REST API를 호출하여 사용자 데이터를 조회하고 트리뷰를 업데이트합니다."""
        try:
            params = {}
            if keyword:
                params['search'] = keyword  # 백엔드 API 스펙에 맞는 파라미터명 사용 (예: search, q, keyword 등)

            # API 호출 (GET 요청)
            # verify=False는 개발 환경에서 SSL 인증서 검증 무시 (필요 시 사용)
            response = requests.get(self.api_url, params=params)
            print(f"API 호출 성공: {response.status_code} - {response.text}")
            if response.status_code == 200:
                self.all_data = response.json() # JSON 응답 파싱
                self.update_tree(self.all_data)
            else:
                print(f"API 호출 실패: {response.status_code} - {response.text}")
                self.all_data = []
                self.update_tree([])

        except Exception as e:
            print(f"API 연동 중 오류 발생: {e}")
            self.all_data = []
            self.update_tree([])

    def search_data(self):
        """검색어에 따라 API를 다시 호출합니다."""
        keyword = self.ent_search.get().strip()
        self.load_data_from_api(keyword)

    def update_tree(self, data):
        """트리뷰 비우고 새로운 데이터 채우기"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for user in data:
            # API 응답 키값에 맞춰 데이터 추출 (안전하게 get 사용)
            # 예: user.get("joinDate") 등 실제 키값 확인 필요
            user_id = user.get("id", "")
            name = user.get("userId", "")
            email = user.get("userNm", "")
            date = user.get("content", "") # 또는 user.get("joinDate")

            self.tree.insert("", "end", values=(user_id, name, email, date))

