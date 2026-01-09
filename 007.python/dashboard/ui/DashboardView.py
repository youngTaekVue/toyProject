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