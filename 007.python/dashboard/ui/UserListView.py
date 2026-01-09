import tkinter as tk
from tkinter import ttk

class UserListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 데이터 초기화 (검색을 위해 멤버 변수로 저장)
        self.user_data = [
            {"id": 1, "name": "홍길동", "email": "hong@example.com", "date": "2023-10-01"},
            {"id": 2, "name": "김철수", "email": "kim@test.com", "date": "2023-10-05"},
            {"id": 3, "name": "이영희", "email": "lee@site.org", "date": "2023-10-12"},
            {"id": 4, "name": "박민수", "email": "park@domain.net", "date": "2023-10-20"},
            {"id": 5, "name": "최지우", "email": "choi@korea.kr", "date": "2023-10-25"},
        ]
        self.setup_ui()

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

        columns = ("id", "name", "email", "date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="이름")
        self.tree.heading("email", text="이메일")
        self.tree.heading("date", text="가입일")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=100)
        self.tree.column("email", width=200)
        self.tree.column("date", width=100, anchor="center")

        # 초기 데이터 로드
        self.update_tree(self.user_data)

    def search_data(self):
        """검색어에 따라 데이터를 필터링"""
        keyword = self.ent_search.get().strip()

        # 검색어가 없으면 전체, 있으면 이름이나 이메일에 포함된 경우만 필터링
        filtered_data = [
            user for user in self.user_data
            if keyword == "" or keyword in user["name"] or keyword in user["email"]
        ]
        self.update_tree(filtered_data)

    def update_tree(self, data):
        """트리뷰 비우고 새로운 데이터 채우기"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for user in data:
            self.tree.insert("", "end", values=(user["id"], user["name"], user["email"], user["date"]))