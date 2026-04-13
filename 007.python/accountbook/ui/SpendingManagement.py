import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import database
import traceback
from utils.TransactionUtil import TransactionUtil
import ttkbootstrap as tb
import os
import threading
from dotenv import load_dotenv

# Google Gemini API 라이브러리
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# 한글 폰트 및 스타일 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class SpendingManagement(ttk.Frame):
    def __init__(self, parent, display_sections=None, on_month_select=None):
        super().__init__(parent)
        load_dotenv(override=True)
        self.dashboard_util = TransactionUtil()
        self.filtered_df = pd.DataFrame()
        self.all_months = []
        self.monthly_summary = pd.DataFrame()
        self.chart_y = []
        self.selected_month_idx = None
        self.on_month_select = on_month_select
        self.ai_call_timer = None
        self.ai_cache = {}  
        
        # UI 요소 초기화
        self.lbl_curr_val = None
        self.lbl_mom_change = None
        self.lbl_avg_val = None
        self.lbl_max_month = None
        self.lbl_daily_avg = None
        self.lbl_ai_status = None

        if display_sections is None:
            self.display_sections = ['kpi', 'chart', 'category_analysis', 'top_merchants', 'ai_advice']
        else:
            self.display_sections = display_sections

        self.setup_ui()
        self.load_and_plot_data()

    def setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.top_section = ttk.Frame(self.main_container)
        self.bottom_section = ttk.Frame(self.main_container, padding=(15, 2))
        self.ai_section = ttk.Frame(self.main_container, padding=(20, 0))

        if 'kpi' in self.display_sections or 'chart' in self.display_sections:
            self.top_section.pack(fill=tk.BOTH, expand=True)

        if 'kpi' in self.display_sections:
            self.kpi_frame = ttk.Frame(self.top_section, padding=(20, 5))
            self.kpi_frame.pack(fill=tk.X)

            style = ttk.Style()
            style.configure("KPI.TLabel", font=("맑은 고딕", 10), foreground="#666666")
            style.configure("Value.TLabel", font=("맑은 고딕", 16, "bold"))
            style.configure("SubValue.TLabel", font=("맑은 고딕", 9), foreground="#888888")

            c1 = ttk.Frame(self.kpi_frame); c1.pack(side=tk.LEFT, expand=True)
            ttk.Label(c1, text="선택 월 총지출", style="KPI.TLabel").pack()
            self.lbl_curr_val = ttk.Label(c1, text="0원", style="Value.TLabel")
            self.lbl_curr_val.pack()
            self.lbl_mom_change = ttk.Label(c1, text="-", style="SubValue.TLabel")
            self.lbl_mom_change.pack()

            c_daily = ttk.Frame(self.kpi_frame); c_daily.pack(side=tk.LEFT, expand=True)
            ttk.Label(c_daily, text="일평균 지출", style="KPI.TLabel").pack()
            self.lbl_daily_avg = ttk.Label(c_daily, text="0원", style="Value.TLabel", foreground="#1e88e5")
            self.lbl_daily_avg.pack()
            ttk.Label(c_daily, text="(해당 월 기준)", style="SubValue.TLabel").pack()

            c2 = ttk.Frame(self.kpi_frame); c2.pack(side=tk.LEFT, expand=True)
            ttk.Label(c2, text="전체 월평균", style="KPI.TLabel").pack()
            self.lbl_avg_val = ttk.Label(c2, text="0원", style="Value.TLabel", foreground="#43a047")
            self.lbl_avg_val.pack()

            c3 = ttk.Frame(self.kpi_frame); c3.pack(side=tk.LEFT, expand=True)
            ttk.Label(c3, text="최대 지출 월", style="KPI.TLabel").pack()
            self.lbl_max_month = ttk.Label(c3, text="-", style="Value.TLabel", foreground="#fb8c00")
            self.lbl_max_month.pack()

        if 'chart' in self.display_sections:
            self.chart_frame = ttk.Frame(self.top_section, padding=(10, 0))
            self.chart_frame.pack(fill=tk.BOTH, expand=True)
            self.fig = Figure(figsize=(9, 3.8), dpi=100, facecolor='#ffffff')
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvas.mpl_connect('button_press_event', self.on_chart_click)

        if 'category_analysis' in self.display_sections or 'top_merchants' in self.display_sections:
            self.bottom_section.pack(fill=tk.X, pady=(5, 0))

        if 'category_analysis' in self.display_sections:
            self.left_analysis = ttk.LabelFrame(self.bottom_section, text=" 전월 대비 카테고리별 증감 ", padding=10)
            self.left_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,  padx=(10, 10))
            self.tree_category = ttk.Treeview(self.left_analysis, columns=("category", "prev", "curr", "diff"), show="headings", height=5)
            self.tree_category.heading("category", text="카테고리"); self.tree_category.heading("prev", text="지난달")
            self.tree_category.heading("curr", text="선택달"); self.tree_category.heading("diff", text="증감")
            for col in ("category", "prev", "curr", "diff"): self.tree_category.column(col, width=80, anchor="center")
            self.tree_category.pack(fill=tk.BOTH, expand=True)

        if 'top_merchants' in self.display_sections:
            self.right_analysis = ttk.LabelFrame(self.bottom_section, text=" 선택 월 주요 소비처 Top 5 ", padding=10)
            self.right_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,  padx=(10, 10))
            self.tree_merchants = ttk.Treeview(self.right_analysis, columns=("cat", "merchant", "amount"), show="headings", height=5)
            self.tree_merchants.heading("cat", text="카테고리")
            self.tree_merchants.heading("merchant", text="소비처")
            self.tree_merchants.heading("amount", text="금액")
            for col in ("cat", "merchant", "amount"): self.tree_merchants.column(col, width=80, anchor="center")
            self.tree_merchants.pack(fill=tk.BOTH, expand=True)

        if 'ai_advice' in self.display_sections:
            self.ai_section.pack(fill=tk.X, expand=False)
            # 아주 컴팩트하게 높이 조절
            self.ai_advice_frame = ttk.LabelFrame(self.ai_section, text=" AI 소비 진단 ", padding=5)
            self.ai_advice_frame.pack(fill=tk.X, expand=False, padx=5, pady=(0, 5))

            header_sub = ttk.Frame(self.ai_advice_frame)
            header_sub.pack(fill=tk.X)
            self.lbl_ai_status = ttk.Label(header_sub, text="상태: 대기 중", font=("맑은 고딕", 8), foreground="gray")
            self.lbl_ai_status.pack(side=tk.LEFT, padx=5)
            self.advice_text = tk.Text(self.ai_advice_frame, wrap=tk.WORD, height=2, state=tk.DISABLED, font=("맑은 고딕", 9), padx=8, pady=5, background="#f8f9fa", borderwidth=0)
            self.advice_text.pack(fill=tk.X, expand=True)

    def load_and_plot_data(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules = cursor.fetchall()
                    self.dashboard_util.mapping_rules = rules
                    cursor.execute("SELECT transaction_date, amount, transaction_type, description, payment_method FROM transactions")
                    res = cursor.fetchall()
            if not res: return
            df = pd.DataFrame(res)
            df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액'}, inplace=True)
            df['DT'] = pd.to_datetime(df['DT'])
            self.dashboard_util.mapping_rules = sorted(rules, key=lambda x: len(x['merchant']), reverse=True) if rules else []
            classified = df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            df['category'] = classified['대분류']; df['타입'] = classified['타입']; df['abs_amt'] = df['금액'].abs()
            self.filtered_df = df[(df['타입'] == '지출')].copy()
            self.filtered_df['month'] = self.filtered_df['DT'].dt.strftime('%Y-%m')
            self.filtered_df['amount'] = self.filtered_df['금액'].abs()
            self.all_months = sorted(self.filtered_df['month'].unique())
            self.monthly_summary = self.filtered_df.groupby('month')['amount'].sum().reset_index()
            if self.all_months:
                self.selected_month_idx = len(self.all_months) - 1
                self.update_analysis_by_month(self.all_months[self.selected_month_idx])
        except Exception: traceback.print_exc()

    def update_analysis_by_month(self, target_month):
        if self.filtered_df.empty or self.monthly_summary.empty: return
        if target_month not in self.all_months: return
        self.selected_month_idx = self.all_months.index(target_month)

        curr_row = self.monthly_summary[self.monthly_summary['month'] == target_month]
        if curr_row.empty: return
        
        curr_amt = int(curr_row.iloc[0]['amount'])

        if self.lbl_curr_val: self.lbl_curr_val.config(text=f"{curr_amt:,}원")
            
        if self.lbl_mom_change:
            if self.selected_month_idx > 0:
                prev_month = self.all_months[self.selected_month_idx - 1]
                prev_amt = int(self.monthly_summary[self.monthly_summary['month'] == prev_month].iloc[0]['amount'])
                diff = curr_amt - prev_amt
                pct = (diff / prev_amt * 100) if prev_amt != 0 else 0
                sign = "+" if diff > 0 else ""
                color = "#e53935" if diff > 0 else "#1e88e5"
                self.lbl_mom_change.config(text=f"전월대비 {sign}{diff:,}원 ({sign}{pct:.1f}%)", foreground=color)
            else:
                self.lbl_mom_change.config(text="전월 데이터 없음", foreground="#888888")

        if self.lbl_daily_avg:
            curr_month_df = self.filtered_df[self.filtered_df['month'] == target_month]
            days_count = curr_month_df['DT'].dt.day.nunique()
            daily_avg = curr_amt / days_count if days_count > 0 else 0
            self.lbl_daily_avg.config(text=f"{int(daily_avg):,}원")

        if self.lbl_avg_val:
            avg_amt = int(self.monthly_summary['amount'].mean())
            self.lbl_avg_val.config(text=f"{avg_amt:,}원")

        if self.lbl_max_month:
            max_row = self.monthly_summary.loc[self.monthly_summary['amount'].idxmax()]
            self.lbl_max_month.config(text=f"{max_row['month']}")

        if 'category_analysis' in self.display_sections: self.update_category_analysis(target_month)
        if 'top_merchants' in self.display_sections: self.update_top_merchants(target_month)
        if 'chart' in self.display_sections: self.draw_modern_chart(self.monthly_summary)

        if 'ai_advice' in self.display_sections:
            if target_month in self.ai_cache:
                self.display_ai_advice(self.ai_cache[target_month])
                if self.lbl_ai_status: self.lbl_ai_status.config(text="상태: 캐시됨", foreground="gray")
            else:
                self.display_ai_advice(f"'{target_month}' 조언 생성 중...")
                if self.ai_call_timer: self.after_cancel(self.ai_call_timer)
                self.ai_call_timer = self.after(1000, self.get_ai_spending_advice)

    def display_ai_advice(self, text):
        if hasattr(self, 'advice_text'):
            self.advice_text.config(state=tk.NORMAL)
            self.advice_text.delete(1.0, tk.END)
            self.advice_text.insert(tk.END, text)
            self.advice_text.config(state=tk.DISABLED)

    def get_ai_spending_advice(self):
        if not HAS_GEMINI:
            self.display_ai_advice("Gemini 라이브러리 없음")
            return
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.display_ai_advice("API 키 누락")
            return
        target_month = self.all_months[self.selected_month_idx]
        if target_month in self.ai_cache: return
        if self.lbl_ai_status: self.lbl_ai_status.config(text="상태: 분석 중...", foreground="#1e88e5")
        threading.Thread(target=self._fetch_gemini_response, args=(api_key, target_month), daemon=True).start()

    def _fetch_gemini_response(self, api_key, target_month):
        try:
            genai.configure(api_key=api_key)
            try: model = genai.GenerativeModel('models/gemini-2.5-flash')
            except: model = genai.GenerativeModel('gemini-pro')
            curr_spending = self.monthly_summary[self.monthly_summary['month'] == target_month].iloc[0]['amount']
            avg_spending = self.monthly_summary['amount'].mean()
            prompt = (f"{target_month} 가계부 조언. 총지출:{int(curr_spending):,}원, 전체월평균:{int(avg_spending):,}원. "
                      f"한국어로 1~2문장으로 핵심만 짧게 조언해줘.")
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            self.ai_cache[target_month] = result_text
            self.after(0, lambda: self._update_ai_ui(result_text, "분석 완료"))
        except Exception as e:
            error_msg = str(e)
            msg = "AI 호출 한도 초과(무료 버전). 잠시 후 다시 시도해 주세요." if "429" in error_msg else f"AI 분석 오류: {error_msg[:50]}..."
            self.after(0, lambda: self._update_ai_ui(msg, "분석 실패"))

    def _update_ai_ui(self, text, status):
        self.display_ai_advice(text)
        if self.lbl_ai_status: self.lbl_ai_status.config(text=f"상태: {status}", foreground="gray")

    def draw_modern_chart(self, monthly):
        if not hasattr(self, 'ax'): return
        self.ax.clear()
        self.ax.plot(range(len(monthly)), monthly['amount'], marker='o', color='#1e88e5', linewidth=2, markersize=5, alpha=0.5)
        if self.selected_month_idx is not None:
            val = monthly.iloc[self.selected_month_idx]['amount']
            self.ax.plot(self.selected_month_idx, val, marker='o', markersize=14, color='#ffd700', alpha=0.3)
            self.ax.plot(self.selected_month_idx, val, marker='o', markersize=9, color='#ffd700', markeredgecolor='#fbc02d', markeredgewidth=2)
            self.ax.annotate(f"{int(val):,}원", xy=(self.selected_month_idx, val), xytext=(0, 10), textcoords='offset points', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#fbc02d', bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#ffd700', alpha=0.8))
        self.ax.set_xticks(range(len(monthly))); self.ax.set_xticklabels(monthly['month'], rotation=45, fontsize=8)
        self.ax.grid(axis='y', linestyle='--', alpha=0.2)
        self.ax.spines['top'].set_visible(False); self.ax.spines['right'].set_visible(False)
        # tight_layout 대신 subplots_adjust를 사용하여 레이아웃 흔들림 방지
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.82, bottom=0.25)
        self.canvas.draw()

    def on_chart_click(self, event):
        if not hasattr(self, 'ax') or event.inaxes != self.ax: return
        try:
            x_idx = int(round(event.xdata))
            if 0 <= x_idx < len(self.all_months):
                target_month = self.all_months[x_idx]
                if self.selected_month_idx == x_idx: return # 동일 월 클릭 시 무시
                if self.on_month_select: self.on_month_select(target_month)
                else: self.update_analysis_by_month(target_month)
        except: pass

    def update_category_analysis(self, target_month):
        if not hasattr(self, 'tree_category'): return
        for item in self.tree_category.get_children(): self.tree_category.delete(item)
        curr_df = self.filtered_df[self.filtered_df['month'] == target_month]
        cat_sum = curr_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        for cat, amt in cat_sum.items(): self.tree_category.insert("", tk.END, values=(cat, "-", f"{int(amt):,}원", "-"))

    def update_top_merchants(self, target_month):
        if not hasattr(self, 'tree_merchants'): return
        for item in self.tree_merchants.get_children(): self.tree_merchants.delete(item)
        curr_df = self.filtered_df[self.filtered_df['month'] == target_month]
        top_m = curr_df.groupby(['category', '내용'])['amount'].sum().reset_index().sort_values('amount', ascending=False).head(5)
        for _, row in top_m.iterrows(): self.tree_merchants.insert("", tk.END, values=(row['category'], row['내용'], f"{int(row['amount']):,}원"))
