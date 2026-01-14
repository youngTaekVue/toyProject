import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime

class LogsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 샘플 로그 데이터 생성
        self.log_data = [
            {"time": "2023-10-25 10:00:01", "level": "INFO", "source": "System", "message": "시스템이 시작되었습니다."},
            {"time": "2023-10-25 10:05:23", "level": "INFO", "source": "User", "message": "사용자(admin) 로그인 성공"},
            {"time": "2023-10-25 10:10:45", "level": "WARNING", "source": "Network", "message": "응답 시간이 지연되고 있습니다. (500ms)"},
            {"time": "2023-10-25 10:15:12", "level": "ERROR", "source": "Database", "message": "DB 연결 실패: Connection timed out"},
            {"time": "2023-10-25 10:20:00", "level": "INFO", "source": "Scheduler", "message": "일일 배치 작업 완료"},
            {"time": "2023-10-25 10:22:30", "level": "ERROR", "source": "Auth", "message": "인증 토큰 만료됨"},
            {"time": "2023-10-25 10:30:00", "level": "INFO", "source": "User", "message": "사용자(guest) 접속"},
        ]
        self.setup_ui()

    def setup_ui(self):
        # 1. 상단 필터 영역
        top_frame = ttk.LabelFrame(self, text="로그 필터")
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        # 레벨 필터
        ttk.Label(top_frame, text="로그 레벨:").pack(side="left", padx=5)
        self.cb_level = ttk.Combobox(top_frame, values=["ALL", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        self.cb_level.current(0) # ALL 선택
        self.cb_level.pack(side="left", padx=5)
        self.cb_level.bind("<<ComboboxSelected>>", lambda e: self.filter_logs())

        # 검색어 필터
        ttk.Label(top_frame, text="메시지 검색:").pack(side="left", padx=5)
        self.ent_search = ttk.Entry(top_frame, width=30)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<Return>", lambda e: self.filter_logs())

        ttk.Button(top_frame, text="조회", command=self.filter_logs).pack(side="left", padx=5)
        ttk.Button(top_frame, text="초기화", command=self.reset_filters).pack(side="left", padx=5)

        # 2. 로그 리스트 (Treeview)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        columns = ("time", "level", "source", "message")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # 컬럼 설정
        self.tree.heading("time", text="시간")
        self.tree.heading("level", text="레벨")
        self.tree.heading("source", text="소스")
        self.tree.heading("message", text="메시지")

        self.tree.column("time", width=150, anchor="center")
        self.tree.column("level", width=80, anchor="center")
        self.tree.column("source", width=100, anchor="center")
        self.tree.column("message", width=400, anchor="w")

        # 색상 태그 설정 (중요!)
        self.tree.tag_configure("INFO", foreground="black")
        self.tree.tag_configure("WARNING", foreground="#E67E22") # 주황색
        self.tree.tag_configure("ERROR", foreground="red")      # 빨간색

        # 더블 클릭 이벤트 (상세 보기)
        self.tree.bind("<Double-1>", self.on_double_click)

        # 초기 데이터 로드
        self.filter_logs()

    def filter_logs(self):
        """필터 조건에 맞춰 트리뷰 업데이트"""
        target_level = self.cb_level.get()
        keyword = self.ent_search.get().strip()

        # 트리뷰 비우기
        for item in self.tree.get_children():
            self.tree.delete(item)

        for log in self.log_data:
            # 1. 레벨 필터링
            if target_level != "ALL" and log["level"] != target_level:
                continue
            
            # 2. 검색어 필터링
            if keyword and keyword not in log["message"]:
                continue

            # 데이터 삽입 (tags에 level을 넣어 색상 적용)
            self.tree.insert("", "end", values=(log["time"], log["level"], log["source"], log["message"]), tags=(log["level"],))

    def reset_filters(self):
        """필터 초기화"""
        self.cb_level.current(0)
        self.ent_search.delete(0, "end")
        self.filter_logs()

    def on_double_click(self, event):
        """더블 클릭 시 상세 내용 팝업"""
        item_id = self.tree.selection()
        if not item_id:
            return
        
        item = self.tree.item(item_id)
        values = item['values'] # (time, level, source, message)

        # 팝업창 생성
        popup = tk.Toplevel(self)
        popup.title("로그 상세 정보")
        popup.geometry("400x300")

        ttk.Label(popup, text=f"[{values[1]}] {values[2]}", font=("bold", 12)).pack(pady=10)
        ttk.Label(popup, text=f"발생 시간: {values[0]}").pack(anchor="w", padx=10)
        
        ttk.Label(popup, text="메시지 내용:").pack(anchor="w", padx=10, pady=(10, 0))
        
        # 긴 텍스트를 위한 Text 위젯
        txt_msg = tk.Text(popup, height=10, width=50)
        txt_msg.pack(padx=10, pady=5, fill="both", expand=True)
        txt_msg.insert("1.0", values[3])
        txt_msg.configure(state="disabled") # 읽기 전용

        ttk.Button(popup, text="닫기", command=popup.destroy).pack(pady=10)