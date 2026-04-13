import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from utils.Logger import logger

class LogsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 페이징 관련 변수
        self.page_size = 50
        self.current_page = 1
        self.total_pages = 1
        self.filtered_data = []

        self.setup_ui()
        self.filter_logs() # 초기 로드

    def setup_ui(self):
        # 1. 상단 필터 영역
        top_frame = ttk.LabelFrame(self, text="로그 필터")
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        # 레벨 필터
        ttk.Label(top_frame, text="로그 레벨:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_level = ttk.Combobox(top_frame, values=["ALL", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        self.cb_level.current(0)
        self.cb_level.grid(row=0, column=1, padx=5, pady=5)

        # 기간 필터 (From ~ To)
        ttk.Label(top_frame, text="기간:").grid(row=0, column=2, padx=5, pady=5)
        today = datetime.date.today()
        
        self.ent_from = ttk.Entry(top_frame, width=12)
        self.ent_from.insert(0, (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        self.ent_from.grid(row=0, column=3, padx=2)
        
        ttk.Label(top_frame, text="~").grid(row=0, column=4)
        
        self.ent_to = ttk.Entry(top_frame, width=12)
        self.ent_to.insert(0, today.strftime("%Y-%m-%d"))
        self.ent_to.grid(row=0, column=5, padx=2)

        # 검색어 필터
        ttk.Label(top_frame, text="메시지 검색:").grid(row=0, column=6, padx=5, pady=5)
        self.ent_search = ttk.Entry(top_frame, width=20)
        self.ent_search.grid(row=0, column=7, padx=5, pady=5)
        self.ent_search.bind("<Return>", lambda e: self.filter_logs())

        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=0, column=8, padx=10)
        ttk.Button(btn_frame, text="조회", command=self.filter_logs).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="초기화", command=self.reset_filters).pack(side="left", padx=2)

        # 2. 로그 리스트 (Treeview)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        columns = ("time", "level", "source", "message")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("time", text="시간")
        self.tree.heading("level", text="레벨")
        self.tree.heading("source", text="소스")
        self.tree.heading("message", text="메시지")

        self.tree.column("time", width=150, anchor="center")
        self.tree.column("level", width=80, anchor="center")
        self.tree.column("source", width=100, anchor="center")
        self.tree.column("message", width=400, anchor="w")

        self.tree.tag_configure("INFO", foreground="black")
        self.tree.tag_configure("WARNING", foreground="#E67E22")
        self.tree.tag_configure("ERROR", foreground="red")
        self.tree.bind("<Double-1>", self.on_double_click)

        # 3. 하단 페이징 컨트롤
        pagination_frame = ttk.Frame(self)
        pagination_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.btn_prev = ttk.Button(pagination_frame, text="◀ 이전", command=self.prev_page)
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_page_info = ttk.Label(pagination_frame, text="Page 1 of 1")
        self.lbl_page_info.pack(side="left", padx=20)

        self.btn_next = ttk.Button(pagination_frame, text="다음 ▶", command=self.next_page)
        self.btn_next.pack(side="left", padx=5)

        ttk.Label(pagination_frame, text="표시 개수:").pack(side="right", padx=5)
        self.cb_page_size = ttk.Combobox(pagination_frame, values=["20", "50", "100", "200"], width=5, state="readonly")
        self.cb_page_size.set("50")
        self.cb_page_size.pack(side="right", padx=5)
        self.cb_page_size.bind("<<ComboboxSelected>>", self.change_page_size)

    def filter_logs(self):
        """필터 조건에 따라 전체 데이터를 먼저 필터링"""
        target_level = self.cb_level.get()
        keyword = self.ent_search.get().strip().lower()
        
        try:
            from_date = datetime.datetime.strptime(self.ent_from.get(), "%Y-%m-%d").date()
            to_date = datetime.datetime.strptime(self.ent_to.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("오류", "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)")
            return

        self.filtered_data = []
        for log in reversed(logger.logs):
            # 1. 레벨 필터링
            if target_level != "ALL" and log["level"] != target_level:
                continue
            
            # 2. 기간 필터링
            try:
                log_date = datetime.datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S").date()
                if not (from_date <= log_date <= to_date):
                    continue
            except: continue

            # 3. 검색어 필터링
            if keyword and keyword not in log["message"].lower() and keyword not in log["source"].lower():
                continue

            self.filtered_data.append(log)

        # 페이징 초기화 및 업데이트
        self.current_page = 1
        self.update_pagination_info()
        self.show_page_data()

    def show_page_data(self):
        """현재 페이지에 해당하는 데이터만 트리뷰에 표시"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        
        page_data = self.filtered_data[start_idx:end_idx]

        for log in page_data:
            self.tree.insert("", "end", values=(log["time"], log["level"], log["source"], log["message"]), tags=(log["level"],))

    def update_pagination_info(self):
        """페이지 번호 및 버튼 상태 업데이트"""
        total_items = len(self.filtered_data)
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        self.lbl_page_info.config(text=f"Page {self.current_page} of {self.total_pages} (Total: {total_items})")
        
        self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < self.total_pages else "disabled")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination_info()
            self.show_page_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination_info()
            self.show_page_data()

    def change_page_size(self, event):
        self.page_size = int(self.cb_page_size.get())
        self.current_page = 1
        self.update_pagination_info()
        self.show_page_data()

    def reset_filters(self):
        self.cb_level.current(0)
        today = datetime.date.today()
        self.ent_from.delete(0, "end")
        self.ent_from.insert(0, (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        self.ent_to.delete(0, "end")
        self.ent_to.insert(0, today.strftime("%Y-%m-%d"))
        self.ent_search.delete(0, "end")
        self.filter_logs()

    def on_double_click(self, event):
        item_id = self.tree.selection()
        if not item_id: return
        item = self.tree.item(item_id)
        values = item['values']
        popup = tk.Toplevel(self)
        popup.title("로그 상세 정보")
        popup.geometry("500x350")
        ttk.Label(popup, text=f"[{values[1]}] {values[2]}", font=("bold", 12)).pack(pady=10)
        ttk.Label(popup, text=f"발생 시간: {values[0]}").pack(anchor="w", padx=10)
        ttk.Label(popup, text="메시지 내용:").pack(anchor="w", padx=10, pady=(10, 0))
        txt_msg = tk.Text(popup, height=10, width=50)
        txt_msg.pack(padx=10, pady=5, fill="both", expand=True)
        txt_msg.insert("1.0", values[3])
        txt_msg.configure(state="disabled")
        ttk.Button(popup, text="닫기", command=popup.destroy).pack(pady=10)
