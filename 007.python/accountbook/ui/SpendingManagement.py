import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import database
import traceback
from utils.TransactionUtil import TransactionUtil

# 한글 폰트 및 스타일 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class SpendingManagement(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.dashboard_util = TransactionUtil()
        self.setup_ui()
        self.load_and_plot_data()

    def setup_ui(self):
        # 전체를 담는 메인 컨테이너
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 1. 상단 영역 (KPI + 차트)
        self.top_section = ttk.Frame(self.main_container)
        self.top_section.pack(fill=tk.BOTH, expand=True)

        # 1-1. 상단 요약 카드 영역 (KPI)
        self.kpi_frame = ttk.Frame(self.top_section, padding=(20, 10))
        self.kpi_frame.pack(fill=tk.X)
        
        style = ttk.Style()
        style.configure("KPI.TLabel", font=("맑은 고딕", 10), foreground="#666666")
        style.configure("Value.TLabel", font=("맑은 고딕", 18, "bold"))
        style.configure("Increase.TLabel", font=("맑은 고딕", 10, "bold"), foreground="#e53935")
        style.configure("Decrease.TLabel", font=("맑은 고딕", 10, "bold"), foreground="#1e88e5")

        # KPI 카드들
        c1 = ttk.Frame(self.kpi_frame); c1.pack(side=tk.LEFT, expand=True)
        ttk.Label(c1, text="이번 달 지출", style="KPI.TLabel").pack()
        self.lbl_curr_val = ttk.Label(c1, text="0원", style="Value.TLabel")
        self.lbl_curr_val.pack()
        self.lbl_mom_change = ttk.Label(c1, text="-", style="KPI.TLabel")
        self.lbl_mom_change.pack()

        c2 = ttk.Frame(self.kpi_frame); c2.pack(side=tk.LEFT, expand=True)
        ttk.Label(c2, text="월평균 지출", style="KPI.TLabel").pack()
        self.lbl_avg_val = ttk.Label(c2, text="0원", style="Value.TLabel", foreground="#43a047")
        self.lbl_avg_val.pack()

        c3 = ttk.Frame(self.kpi_frame); c3.pack(side=tk.LEFT, expand=True)
        ttk.Label(c3, text="최대 지출 월", style="KPI.TLabel").pack()
        self.lbl_max_month = ttk.Label(c3, text="-", style="Value.TLabel", foreground="#fb8c00")
        self.lbl_max_month.pack()

        # 1-2. 메인 차트 영역 (월별 추이)
        self.chart_frame = ttk.Frame(self.top_section, padding=(20, 0))
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(9, 4), dpi=100, facecolor='#ffffff')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 2. 하단 상세 분석 영역 (2단 구성)
        self.bottom_section = ttk.Frame(self.main_container, padding=20)
        self.bottom_section.pack(fill=tk.BOTH, expand=True)
        
        # 좌측: 카테고리별 증감
        self.left_analysis = ttk.LabelFrame(self.bottom_section, text=" 전월 대비 카테고리별 증감 ", padding=10)
        self.left_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.tree_category = ttk.Treeview(self.left_analysis, columns=("category", "prev", "curr", "diff"), show="headings", height=6)
        self.tree_category.heading("category", text="카테고리")
        self.tree_category.heading("prev", text="지난달")
        self.tree_category.heading("curr", text="이번달")
        self.tree_category.heading("diff", text="증감")
        self.tree_category.column("category", width=100, anchor="center")
        self.tree_category.column("prev", width=100, anchor="e")
        self.tree_category.column("curr", width=100, anchor="e")
        self.tree_category.column("diff", width=120, anchor="center")
        self.tree_category.pack(fill=tk.BOTH, expand=True)

        # 우측: 주요 소비처 Top 5
        self.right_analysis = ttk.LabelFrame(self.bottom_section, text=" 이번 달 주요 소비처 Top 5 ", padding=10)
        self.right_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree_merchants = ttk.Treeview(self.right_analysis, columns=("cat", "merchant", "amount"), show="headings", height=6)
        self.tree_merchants.heading("cat", text="카테고리")
        self.tree_merchants.heading("merchant", text="상호명")
        self.tree_merchants.heading("amount", text="금액")
        self.tree_merchants.column("cat", width=80, anchor="center")
        self.tree_merchants.column("merchant", width=120, anchor="w")
        self.tree_merchants.column("amount", width=80, anchor="e")
        self.tree_merchants.pack(fill=tk.BOTH, expand=True)

    def load_and_plot_data(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules = cursor.fetchall()
                    self.dashboard_util.mapping_rules = rules
                    
                    query = "SELECT transaction_date, amount, transaction_type, description FROM transactions"
                    cursor.execute(query)
                    res = cursor.fetchall()

            if not res:
                self.show_empty_state()
                return

            df = pd.DataFrame(res)
            df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액'}, inplace=True)
            df['DT'] = pd.to_datetime(df['DT'])
            
            classified = df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            df['category'] = classified['대분류']
            
            df = df[df['타입'] == '지출'].copy()
            df['month'] = df['DT'].dt.strftime('%Y-%m')
            df['amount'] = df['금액'].abs()
            
            if df.empty:
                self.show_empty_state()
                return

            monthly = df.groupby('month')['amount'].sum().reset_index().sort_values('month')
            self.update_kpi(monthly)
            self.draw_modern_chart(monthly)

            self.update_category_analysis(df)
            self.update_top_merchants(df)

        except Exception:
            traceback.print_exc()

    def update_category_analysis(self, df):
        for item in self.tree_category.get_children():
            self.tree_category.delete(item)
            
        months = sorted(df['month'].unique())
        if len(months) < 2: return
        
        curr_month = months[-1]
        prev_month = months[-2]
        
        cat_pivot = df.pivot_table(index='category', columns='month', values='amount', aggfunc='sum').fillna(0)
        
        if curr_month in cat_pivot.columns and prev_month in cat_pivot.columns:
            diff_df = cat_pivot[[prev_month, curr_month]].copy()
            diff_df['diff'] = diff_df[curr_month] - diff_df[prev_month]
            diff_df = diff_df.sort_values('diff', ascending=False)
            
            for cat, row in diff_df.iterrows():
                prev_val = f"{int(row[prev_month]):,}원"
                curr_val = f"{int(row[curr_month]):,}원"
                
                diff = row['diff']
                if diff > 0:
                    diff_str = f"▲ {int(diff):,}원"
                    tags = ('increase',)
                elif diff < 0:
                    diff_str = f"▼ {abs(int(diff)):,}원"
                    tags = ('decrease',)
                else:
                    diff_str = "-"
                    tags = ()
                
                self.tree_category.insert("", tk.END, values=(cat, prev_val, curr_val, diff_str), tags=tags)
        
        self.tree_category.tag_configure('increase', foreground='#e53935')
        self.tree_category.tag_configure('decrease', foreground='#1e88e5')

    def update_top_merchants(self, df):
        for item in self.tree_merchants.get_children():
            self.tree_merchants.delete(item)
            
        months = sorted(df['month'].unique())
        if not months: return
        curr_month = months[-1]
        curr_df = df[df['month'] == curr_month]
        
        top_m = curr_df.groupby(['category', '내용'])['amount'].sum().reset_index()
        top_m = top_m.sort_values('amount', ascending=False).head(5)
        
        for _, row in top_m.iterrows():
            amt_str = f"{int(row['amount']):,}원"
            self.tree_merchants.insert("", tk.END, values=(row['category'], row['내용'], amt_str))

    def update_kpi(self, monthly):
        curr_val = monthly.iloc[-1]['amount']
        self.lbl_curr_val.config(text=f"{int(curr_val):,}원")
        
        if len(monthly) > 1:
            prev_val = monthly.iloc[-2]['amount']
            diff = curr_val - prev_val
            pct = (diff / prev_val) * 100 if prev_val != 0 else 0
            
            if diff > 0:
                self.lbl_mom_change.config(text=f"▲ {int(diff):,}원 ({pct:.1f}%)", style="Increase.TLabel")
            else:
                self.lbl_mom_change.config(text=f"▼ {abs(int(diff)):,}원 ({abs(pct):.1f}%)", style="Decrease.TLabel")
        
        avg_val = monthly['amount'].mean()
        self.lbl_avg_val.config(text=f"{int(avg_val):,}원")
        
        max_row = monthly.loc[monthly['amount'].idxmax()]
        self.lbl_max_month.config(text=f"{max_row['month']}")

    def draw_modern_chart(self, monthly):
        self.ax.clear()
        x = monthly['month']
        y = monthly['amount']

        self.ax.fill_between(x, y, color='#e3f2fd', alpha=0.5)
        self.ax.plot(x, y, color='#1e88e5', marker='o', markersize=8, 
                    markerfacecolor='white', markeredgewidth=2, linewidth=3)
        
        self.ax.set_title("월별 총 지출 추이", fontsize=12, pad=15, fontweight='bold', color='#333333')
        for spine in self.ax.spines.values():
            spine.set_visible(False)
            
        self.ax.grid(axis='y', linestyle='--', alpha=0.3)
        self.ax.tick_params(axis='both', which='both', length=0, labelsize=9, colors='#666666')
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x/10000), ',') + '만'))

        for i, val in enumerate(y):
            if i == len(y) - 1:
                self.ax.text(i, val + (max(y)*0.05), f'{int(val/10000)}만원', 
                            ha='center', fontweight='bold', color='#1e88e5', fontsize=10)
            elif val == max(y):
                self.ax.text(i, val + (max(y)*0.05), 'Peak', ha='center', color='#fb8c00', fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw()

    def show_empty_state(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "데이터를 업로드하면 분석이 시작됩니다.", 
                    ha='center', va='center', transform=self.ax.transAxes, color='gray')
        self.ax.set_axis_off()
        self.canvas.draw()
