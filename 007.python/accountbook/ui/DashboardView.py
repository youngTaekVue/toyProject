import tkinter as tk
from tkinter import ttk
from ui.TransactionView import TransactionView
from ui.SpendingManagement import SpendingManagement

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # 1. 대시보드 전체 레이아웃 (2행 구성)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # 헤더
        self.rowconfigure(1, weight=1) # 상단 (지출상세 + 요약/Top5)
        self.rowconfigure(2, weight=1) # 하단 (지출 추이)

        # 2. 객체 생성
        self.tv = TransactionView(self)
        self.sm = SpendingManagement(self)

        # 3. 상단 헤더
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ttk.Label(self.header_frame, text="📊 대시보드 통합 조회 월:", font=("맑은 고딕", 11, "bold")).pack(side=tk.LEFT)
        self.month_cb = ttk.Combobox(self.header_frame, textvariable=self.tv.shared_month_var, state="readonly", width=15)
        self.month_cb.pack(side=tk.LEFT, padx=10)

        # 4. [상단 영역] TransactionView 활용 (지출상세 + 요약)
        # tv를 1행에 배치하고, 내부의 리스트만 숨깁니다.
        self.tv.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        if hasattr(self.tv, 'top_bar'): self.tv.top_bar.pack_forget()
        if hasattr(self.tv, 'card_list'): self.tv.card_list.grid_forget()

        # TransactionView 내부의 0번 열(차트)과 1번 열(요약) 비율 조정
        self.tv.main_frame.columnconfigure(0, weight=3)
        self.tv.main_frame.columnconfigure(1, weight=2)

        # 5. [상단 우측에 Top 5 추가] SpendingManagement의 Top 5를 TransactionView 내부로 배치
        # TclError를 피하기 위해, tv.card_summary 아래에 sm의 Top 5를 배치하지 않고
        # sm을 하단에 배치하되 그 구성을 조정합니다.

        # 6. [하단 영역] SpendingManagement 활용 (지출 추이 + Top 5)
        # sm을 2행에 배치합니다.
        self.sm.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # SpendingManagement 내부 레이아웃 재조정
        if hasattr(self.sm, 'kpi_frame'): self.sm.kpi_frame.pack_forget()
        if hasattr(self.sm, 'left_analysis'): self.sm.left_analysis.pack_forget()

        # 하단 섹션에서 '증감'은 숨기고 'Top 5'만 차트 옆에 보이도록 재배치
        if hasattr(self.sm, 'bottom_section') and hasattr(self.sm, 'top_section'):
            self.sm.top_section.pack_forget()
            self.sm.bottom_section.pack_forget()

            # 차트(top_section)를 좌측에, Top 5(bottom_section)를 우측에 배치
            self.sm.top_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            # pack() does not support 'width' option. Use configure() on the widget instead if needed.
            self.sm.bottom_section.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        self._sync_month_selector()

    def _sync_month_selector(self):
        if not self.winfo_exists(): return
        vals = self.tv.cb_shared_month['values']
        if vals:
            self.month_cb['values'] = vals
            if not self.month_cb.get(): self.month_cb.set(vals[0])
            self.month_cb.bind("<<ComboboxSelected>>", self._on_month_change)
        else:
            self.after(500, self._sync_month_selector)

    def _on_month_change(self, event):
        self.tv.on_month_change(event)
        selected_month = self.month_cb.get()
        if selected_month in self.sm.all_months:
            self.sm.selected_month_idx = self.sm.all_months.index(selected_month)
            self.sm.update_analysis_by_month(selected_month)