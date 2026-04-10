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
        self.bottom_section = ttk.Frame(self.main_container, padding=20)
        self.ai_section = ttk.Frame(self.main_container, padding=(20, 0))

        if 'kpi' in self.display_sections or 'chart' in self.display_sections:
            self.top_section.pack(fill=tk.X)

        if 'kpi' in self.display_sections:
            self.kpi_frame = ttk.Frame(self.top_section, padding=(20, 10))
            self.kpi_frame.pack(fill=tk.X)
            
            style = ttk.Style()
            style.configure("KPI.TLabel", font=("맑은 고딕", 10), foreground="#666666")
            style.configure("Value.TLabel", font=("맑은 고딕", 18, "bold"))
            style.configure("Increase.TLabel", font=("맑은 고딕", 10, "bold"), foreground="#e53935")
            style.configure("Decrease.TLabel", font=("맑은 고딕", 10, "bold"), foreground="#1e88e5")

            c1 = ttk.Frame(self.kpi_frame); c1.pack(side=tk.LEFT, expand=True)
            ttk.Label(c1, text="선택 월 지출", style="KPI.TLabel").pack()
            self.lbl_curr_val = ttk.Label(c1, text="0원", style="Value.TLabel")
            self.lbl_curr_val.pack()
            self.lbl_mom_change = ttk.Label(c1, text="-", style="KPI.TLabel")
            self.lbl_mom_change.pack()

            c2 = ttk.Frame(self.kpi_frame); c2.pack(side=tk.LEFT, expand=True)
            ttk.Label(c2, text="전체 월평균 지출", style="KPI.TLabel").pack()
            self.lbl_avg_val = ttk.Label(c2, text="0원", style="Value.TLabel", foreground="#43a047")
            self.lbl_avg_val.pack()

            c3 = ttk.Frame(self.kpi_frame); c3.pack(side=tk.LEFT, expand=True)
            ttk.Label(c3, text="최대 지출 월", style="KPI.TLabel").pack()
            self.lbl_max_month = ttk.Label(c3, text="-", style="Value.TLabel", foreground="#fb8c00")
            self.lbl_max_month.pack()

        if 'chart' in self.display_sections:
            self.chart_frame = ttk.Frame(self.top_section, padding=(20, 0))
            self.chart_frame.pack(fill=tk.X)
            self.fig = Figure(figsize=(9, 2.5), dpi=100, facecolor='#ffffff')
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.get_tk_widget().pack(fill=tk.X, expand=True)
            self.canvas.mpl_connect('button_press_event', self.on_chart_click)

        if 'category_analysis' in self.display_sections or 'top_merchants' in self.display_sections:
            self.bottom_section.pack(fill=tk.X)

        if 'category_analysis' in self.display_sections:
            self.left_analysis = ttk.LabelFrame(self.bottom_section, text=" 전월 대비 카테고리별 증감 ", padding=10)
            self.left_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.tree_category = ttk.Treeview(self.left_analysis, columns=("category", "prev", "curr", "diff"), show="headings", height=5)
            self.tree_category.heading("category", text="카테고리"); self.tree_category.heading("prev", text="지난달")
            self.tree_category.heading("curr", text="선택달"); self.tree_category.heading("diff", text="증감")
            for col in ("category", "prev", "curr", "diff"): self.tree_category.column(col, width=80, anchor="center")
            self.tree_category.pack(fill=tk.BOTH, expand=True)

        if 'top_merchants' in self.display_sections:
            self.right_analysis = ttk.LabelFrame(self.bottom_section, text=" 선택 월 주요 소비처 Top 5 ", padding=10)
            self.right_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.tree_merchants = ttk.Treeview(self.right_analysis, columns=("cat", "merchant", "amount"), show="headings", height=5)
            for col in ("cat", "merchant", "amount"): self.tree_merchants.heading(col, text=col); self.tree_merchants.column(col, width=80)
            self.tree_merchants.pack(fill=tk.BOTH, expand=True)

        if 'ai_advice' in self.display_sections:
            self.ai_section.pack(fill=tk.BOTH, expand=True)
            self.ai_advice_frame = ttk.LabelFrame(self.ai_section, text=" AI 소비 자동 진단 (Google Gemini) ", padding=10)
            self.ai_advice_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            self.lbl_ai_status = ttk.Label(self.ai_advice_frame, text="상태: 대기 중", font=("맑은 고딕", 9), foreground="gray")
            self.lbl_ai_status.pack(anchor=tk.W)
            self.advice_text = tk.Text(self.ai_advice_frame, wrap=tk.WORD, height=5, state=tk.DISABLED, font=("맑은 고딕", 10), padx=10, pady=10, background="#f8f9fa")
            self.advice_text.pack(fill=tk.BOTH, expand=True)

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
        self.selected_month_idx = self.all_months.index(target_month)
        
        curr_row = self.monthly_summary[self.monthly_summary['month'] == target_month]
        if not curr_row.empty:
            self.lbl_curr_val.config(text=f"{int(curr_row.iloc[0]['amount']):,}원")
        
        if 'category_analysis' in self.display_sections: self.update_category_analysis(target_month)
        if 'top_merchants' in self.display_sections: self.update_top_merchants(target_month)
        if 'chart' in self.display_sections: self.draw_modern_chart(self.monthly_summary)
        
        if 'ai_advice' in self.display_sections:
            self.display_ai_advice(f"'{target_month}' 데이터를 분석 중...")
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
            self.display_ai_advice("라이브러리 부족: pip install google-generativeai")
            return
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.display_ai_advice("API 키가 없습니다. .env 파일을 확인하세요.")
            return
        if self.lbl_ai_status: self.lbl_ai_status.config(text="상태: 분석 중...", foreground="#1e88e5")
        threading.Thread(target=self._fetch_gemini_response, args=(api_key,), daemon=True).start()

    def _fetch_gemini_response(self, api_key):
        try:
            genai.configure(api_key=api_key)
            
            # 모델 이름 호환성 확보
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                model = genai.GenerativeModel('gemini-pro')
            
            target_month = self.all_months[self.selected_month_idx]
            curr_spending = self.monthly_summary[self.monthly_summary['month'] == target_month].iloc[0]['amount']
            
            prompt = f"{target_month} 가계부 조언해줘. 총지출: {int(curr_spending):,}원. 한국어로 2문장 내외 짧게."
            response = model.generate_content(prompt)
            self.after(0, lambda: self._update_ai_ui(response.text, "분석 완료"))
        except Exception as e:
            msg = f"AI 분석 오류 (업데이트 권장): {str(e)}"
            self.after(0, lambda: self._update_ai_ui(msg, "분석 실패"))

    def _update_ai_ui(self, text, status):
        self.display_ai_advice(text)
        if self.lbl_ai_status: self.lbl_ai_status.config(text=f"상태: {status}", foreground="gray")

    def draw_modern_chart(self, monthly):
        if not hasattr(self, 'ax'): return
        self.ax.clear()
        self.ax.plot(range(len(monthly)), monthly['amount'], marker='o', color='#1e88e5')
        self.canvas.draw()

    def on_chart_click(self, event):
        if not hasattr(self, 'ax') or event.inaxes != self.ax: return
        try:
            x_idx = int(round(event.xdata))
            if 0 <= x_idx < len(self.all_months):
                self.update_analysis_by_month(self.all_months[x_idx])
        except: pass

    def update_category_analysis(self, target_month):
        if not hasattr(self, 'tree_category'): return
        for item in self.tree_category.get_children(): self.tree_category.delete(item)
        curr_df = self.filtered_df[self.filtered_df['month'] == target_month]
        cat_sum = curr_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        for cat, amt in cat_sum.items():
            self.tree_category.insert("", tk.END, values=(cat, "-", f"{int(amt):,}원", "-"))

    def update_top_merchants(self, target_month):
        if not hasattr(self, 'tree_merchants'): return
        for item in self.tree_merchants.get_children(): self.tree_merchants.delete(item)
        curr_df = self.filtered_df[self.filtered_df['month'] == target_month]
        top_m = curr_df.groupby(['category', '내용'])['amount'].sum().reset_index().sort_values('amount', ascending=False).head(5)
        for _, row in top_m.iterrows():
            self.tree_merchants.insert("", tk.END, values=(row['category'], row['내용'], f"{int(row['amount']):,}원"))
