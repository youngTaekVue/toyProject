import tkinter as tk
from tkinter import ttk
from ui.TransactionView import TransactionView
from ui.SpendingManagement import SpendingManagement

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. 대시보드 레이아웃 설정 (가로 5:5 비율)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0) # 상단 컨트롤 바
        self.rowconfigure(1, weight=1) # 차트 영역

        # 2. 기존 메뉴 객체 생성
        self.tv = TransactionView(self)
        self.sm = SpendingManagement(self)

        # 3. 상단 통합 컨트롤 바 배치
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        ttk.Label(self.header_frame, text="📊 대시보드 통합 조회 월:", font=("맑은 고딕", 11, "bold")).pack(side=tk.LEFT)
        self.month_cb = ttk.Combobox(self.header_frame, textvariable=self.tv.shared_month_var, state="readonly", width=15)
        self.month_cb.pack(side=tk.LEFT, padx=10)

        # 4. TransactionView 커스터마이징 (좌측: 지출 현황 파이 차트만 표시)
        self.tv.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        if hasattr(self.tv, 'top_bar'): self.tv.top_bar.pack_forget()
        if hasattr(self.tv, 'card_summary'): self.tv.card_summary.grid_forget()
        if hasattr(self.tv, 'card_list'): self.tv.card_list.grid_forget()
        if hasattr(self.tv, 'card_chart'):
            self.tv.card_chart.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")

        # 5. SpendingManagement 커스터마이징 (우측: 월별 추이 차트 영역만 표시)
        self.sm.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # SpendingManagement 내부의 하단 분석 영역(bottom_section) 숨기기
        if hasattr(self.sm, 'bottom_section'):
            self.sm.bottom_section.pack_forget()

        # 6. 월 목록 동기화
        self._sync_month_selector()

    def _sync_month_selector(self):
        """TV 객체의 월 목록 데이터를 대시보드 콤보박스에 동기화합니다."""
        if not self.winfo_exists(): return
        
        vals = self.tv.cb_shared_month['values']
        if vals:
            self.month_cb['values'] = vals
            if not self.month_cb.get():
                self.month_cb.set(vals[0])
            self.month_cb.bind("<<ComboboxSelected>>", self.tv.on_month_change)
        else:
            self.after(500, self._sync_month_selector)
