import tkinter as tk
from tkinter import ttk

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # 2x2 그리드 구성을 위해 column/row 가중치 설정
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 카드 1: 서버 상태
        frame1 = ttk.LabelFrame(self, text="서버 상태")
        frame1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame1, text="CPU 사용량: 45%", font=("Consolas", 15)).pack(expand=True)
        ttk.Progressbar(frame1, value=45, length=200).pack(pady=10)

        # 카드 2: 접속자 현황
        frame2 = ttk.LabelFrame(self, text="실시간 접속자")
        frame2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame2, text="1,240 명", font=("맑은 고딕", 20, "bold"), foreground="blue").pack(expand=True)

        # 카드 3: 복잡한 입력 폼 (Grid 중첩)
        frame3 = ttk.LabelFrame(self, text="빠른 검색")
        frame3.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        ttk.Label(frame3, text="검색어:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame3).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame3, text="기간:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        combo = ttk.Combobox(frame3, values=["오늘", "이번주", "이번달"])
        combo.current(0)
        combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(frame3, text="조회").grid(row=0, column=4, padx=10, sticky="ew")

        frame3.columnconfigure(1, weight=1)
        frame3.columnconfigure(3, weight=1)

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

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="시스템 설정 화면입니다.", font=("맑은 고딕", 15)).pack(expand=True)

class LogsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="로그 조회 화면입니다.", font=("맑은 고딕", 15)).pack(expand=True)