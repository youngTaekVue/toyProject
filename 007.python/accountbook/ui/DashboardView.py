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
        self.rowconfigure(1, weight=1) # 상단 (지출상세 + Top5)
        self.rowconfigure(2, weight=1) # 하단 (지출 추이 + 카테고리 분석)

        # 2. 객체 생성
        self.tv = TransactionView(self)
        
        # 3. 상단 헤더
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ttk.Label(self.header_frame, text="📊 대시보드 통합 조회 월:", font=("맑은 고딕", 11, "bold")).pack(side=tk.LEFT)
        self.month_cb = ttk.Combobox(self.header_frame, textvariable=self.tv.shared_month_var, state="readonly", width=15)
        self.month_cb.pack(side=tk.LEFT, padx=10)

        # 4. [상단 영역] TransactionView 활용 (지출상세 + Top 5)
        self.tv.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # TransactionView 내부 구성 요소 조정
        if hasattr(self.tv, 'top_bar'): self.tv.top_bar.pack_forget()
        if hasattr(self.tv, 'card_list'): self.tv.card_list.grid_forget()
        
        # 기존 "이달의 요약" 숨기기
        if hasattr(self.tv, 'card_summary'):
            self.tv.card_summary.grid_forget()
            
        # SpendingManagement의 Top 5를 "이달의 요약" 자리에 배치
        self.sm_top5 = SpendingManagement(self.tv.main_frame, display_sections=['top_merchants'])
        self.sm_top5.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # TransactionView 내부의 0번 열(차트)과 1번 열(Top 5) 비율 조정
        self.tv.main_frame.columnconfigure(0, weight=3)
        self.tv.main_frame.columnconfigure(1, weight=2)

        # 5. [하단 영역] SpendingManagement 활용 (지출 추이 + 카테고리 분석)
        # KPI와 Top 5를 제외한 차트와 카테고리 분석만 표시
        # 차트 클릭 시 DashboardView의 _on_month_change를 호출하도록 콜백 전달
        self.sm = SpendingManagement(self, display_sections=['chart', 'category_analysis'], on_month_select=self._on_month_change)
        self.sm.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        self._sync_month_selector()

    def _sync_month_selector(self):
        if not self.winfo_exists(): return
        vals = self.tv.cb_shared_month['values']
        if vals:
            self.month_cb['values'] = vals
            if not self.month_cb.get(): 
                current_month = self.tv.shared_month_var.get()
                if current_month:
                    self.month_cb.set(current_month)
                else:
                    self.month_cb.set(vals[0])
            self.month_cb.bind("<<ComboboxSelected>>", self._on_month_change)
            
            # 초기 데이터 동기화
            # 현재 콤보박스에 설정된 월을 기준으로 모든 컴포넌트 업데이트
            self._on_month_change(self.month_cb.get()) 
        else:
            self.after(500, self._sync_month_selector)

    def _on_month_change(self, selected_month_or_event):
        # 이벤트 객체인지, 월 문자열인지 확인하여 selected_month 추출
        if isinstance(selected_month_or_event, str):
            selected_month = selected_month_or_event
            # 차트 클릭으로 월이 변경된 경우 콤보박스도 업데이트
            if self.month_cb.get() != selected_month:
                self.month_cb.set(selected_month)
        else: # ComboboxSelected 이벤트인 경우
            selected_month = self.month_cb.get()

        # TransactionView 업데이트 (내부 차트 등)
        # TransactionView의 shared_month_var를 업데이트하고 on_month_change 호출
        self.tv.shared_month_var.set(selected_month)
        self.tv.on_month_change(None) # 이벤트 객체는 필요 없으므로 None 전달

        # SpendingManagement Top 5 업데이트
        if hasattr(self, 'sm_top5'):
            self.sm_top5.update_top_merchants(selected_month)
            
        # SpendingManagement 하단(차트 + 카테고리) 업데이트
        if hasattr(self, 'sm'):
            # sm의 내부 selected_month_idx를 업데이트하여 차트 하이라이트 동기화
            if selected_month in self.sm.all_months:
                self.sm.selected_month_idx = self.sm.all_months.index(selected_month)
            self.sm.update_analysis_by_month(selected_month)
