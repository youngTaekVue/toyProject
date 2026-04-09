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
    def __init__(self, parent, display_sections=None, on_month_select=None):
        super().__init__(parent)
        self.dashboard_util = TransactionUtil()
        self.filtered_df = pd.DataFrame()
        self.all_months = []
        self.monthly_summary = pd.DataFrame()
        self.chart_y = []
        self.selected_month_idx = None 
        self.on_month_select = on_month_select # 월 선택 시 호출될 콜백 함수

        if display_sections is None:
            self.display_sections = ['kpi', 'chart', 'category_analysis', 'top_merchants']
        else:
            self.display_sections = display_sections

        self.setup_ui()
        self.load_and_plot_data()

    def setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.top_section = ttk.Frame(self.main_container)
        self.bottom_section = ttk.Frame(self.main_container, padding=20)

        if 'kpi' in self.display_sections or 'chart' in self.display_sections:
            self.top_section.pack(fill=tk.BOTH, expand=True)

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
        else:
            self.kpi_frame = None

        if 'chart' in self.display_sections:
            self.chart_frame = ttk.Frame(self.top_section, padding=(20, 0))
            self.chart_frame.pack(fill=tk.BOTH, expand=True)

            self.fig = Figure(figsize=(9, 4), dpi=100, facecolor='#ffffff')
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.canvas.mpl_connect('button_press_event', self.on_chart_click)
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        else:
            self.chart_frame = None; self.fig = None; self.ax = None; self.canvas = None

        if 'category_analysis' in self.display_sections or 'top_merchants' in self.display_sections:
            self.bottom_section.pack(fill=tk.BOTH, expand=True)

        if 'category_analysis' in self.display_sections:
            self.left_analysis = ttk.LabelFrame(self.bottom_section, text=" 전월 대비 카테고리별 증감 ", padding=10)
            self.left_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            self.tree_category = ttk.Treeview(self.left_analysis, columns=("category", "prev", "curr", "diff"), show="headings", height=6)
            self.tree_category.heading("category", text="카테고리"); self.tree_category.heading("prev", text="지난달")
            self.tree_category.heading("curr", text="선택달"); self.tree_category.heading("diff", text="증감")
            self.tree_category.column("category", width=100, anchor="center"); self.tree_category.column("prev", width=100, anchor="e")
            self.tree_category.column("curr", width=100, anchor="e"); self.tree_category.column("diff", width=120, anchor="center")
            self.tree_category.pack(fill=tk.BOTH, expand=True)
        else:
            self.left_analysis = None; self.tree_category = None

        if 'top_merchants' in self.display_sections:
            self.right_analysis = ttk.LabelFrame(self.bottom_section, text=" 선택 월 주요 소비처 Top 5 ", padding=10)
            self.right_analysis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            self.tree_merchants = ttk.Treeview(self.right_analysis, columns=("cat", "merchant", "amount"), show="headings", height=6)
            self.tree_merchants.heading("cat", text="카테고리"); self.tree_merchants.heading("merchant", text="상호명")
            self.tree_merchants.heading("amount", text="금액")
            self.tree_merchants.column("cat", width=80, anchor="center"); self.tree_merchants.column("merchant", width=120, anchor="w")
            self.tree_merchants.column("amount", width=80, anchor="e")
            self.tree_merchants.pack(fill=tk.BOTH, expand=True)
        else:
            self.right_analysis = None; self.tree_merchants = None

    def load_and_plot_data(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules = cursor.fetchall()
                    self.dashboard_util.mapping_rules = rules
                    cursor.execute("SELECT transaction_date, amount, transaction_type, description, payment_method FROM transactions")
                    res = cursor.fetchall()

            if not res:
                if 'chart' in self.display_sections: self.show_empty_state()
                return

            df = pd.DataFrame(res)
            df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액'}, inplace=True)
            df['DT'] = pd.to_datetime(df['DT'])
            
            self.dashboard_util.mapping_rules = sorted(rules, key=lambda x: len(x['merchant']), reverse=True) if rules else []
            classified = df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            df['category'] = classified['대분류']
            df['타입'] = classified['타입']
            df['abs_amt'] = df['금액'].abs()
            cancel_key = [df['DT'].dt.date, '내용', 'abs_amt']
            df['is_cancel'] = df.groupby(cancel_key)['금액'].transform('sum') == 0
            df['is_pre_auth'] = df['내용'].str.contains('선승인|가결제', na=False)
            is_dup_uploaded = df.duplicated(subset=['DT', '타입', '내용', '금액'], keep="first")
            df['is_double_count'] = df['내용'].str.contains('카드결제대금|카드대금|우리카드결제대금', na=False) | is_dup_uploaded
            
            self.filtered_df = df[(df['타입'] == '지출') & (~df['is_cancel']) & (~df['is_double_count']) & (~df['is_pre_auth'])].copy()
            
            if self.filtered_df.empty:
                if 'chart' in self.display_sections: self.show_empty_state()
                return

            self.filtered_df['month'] = self.filtered_df['DT'].dt.strftime('%Y-%m')
            self.filtered_df['amount'] = self.filtered_df['금액'].abs()

            # --- 월 데이터 보정 (누락된 월 0으로 채우기) ---
            min_date = self.filtered_df['DT'].min()
            max_date = self.filtered_df['DT'].max()
            if pd.isna(min_date) or pd.isna(max_date): return

            all_m_range = pd.date_range(start=min_date.replace(day=1), end=max_date.replace(day=1), freq='MS').strftime('%Y-%m').tolist()
            self.all_months = all_m_range

            # 월별 요약 데이터 미리 생성
            actual_monthly = self.filtered_df.groupby('month')['amount'].sum()
            self.monthly_summary = actual_monthly.reindex(self.all_months, fill_value=0.0).reset_index()

            if self.all_months:
                self.selected_month_idx = len(self.all_months) - 1
                self.update_analysis_by_month(self.all_months[self.selected_month_idx])

        except Exception:
            traceback.print_exc()

    def on_mouse_move(self, event):
        if self.ax and event.inaxes == self.ax and event.xdata is not None and event.ydata is not None:
            try:
                x_idx = int(round(event.xdata))
                if 0 <= x_idx < len(self.chart_y):
                    target_y = self.chart_y[x_idx]
                    y_min, y_max = self.ax.get_ylim()
                    tolerance = (y_max - y_min) * 0.05
                    if abs(event.xdata - x_idx) < 0.2 and abs(event.ydata - target_y) < tolerance:
                        self.canvas.get_tk_widget().config(cursor="hand2"); return
            except: pass
        if self.canvas: self.canvas.get_tk_widget().config(cursor="")

    def on_chart_click(self, event):
        if not self.ax or event.inaxes != self.ax: return
        try:
            x_idx = int(round(event.xdata))
            if 0 <= x_idx < len(self.all_months):
                selected_month = self.all_months[x_idx]
                # 내부 상태 업데이트 및 UI 갱신 (즉각적인 피드백)
                self.selected_month_idx = x_idx
                self.update_analysis_by_month(selected_month)

                # 외부 콜백이 설정되어 있으면 호출 (다른 뷰 연동 등)
                if self.on_month_select:
                    self.on_month_select(selected_month)
        except: pass

    def update_analysis_by_month(self, target_month):
        if self.filtered_df.empty or self.monthly_summary.empty: return
        
        if target_month in self.all_months:
            self.selected_month_idx = self.all_months.index(target_month)
        
        if 'kpi' in self.display_sections:
            curr_row = self.monthly_summary[self.monthly_summary['month'] == target_month]
            if not curr_row.empty:
                curr_val = curr_row.iloc[0]['amount']
                self.lbl_curr_val.config(text=f"{int(curr_val):,}원")
                try:
                    target_idx = self.all_months.index(target_month)
                    if target_idx > 0:
                        prev_month = self.all_months[target_idx - 1]
                        prev_val = self.monthly_summary[self.monthly_summary['month'] == prev_month].iloc[0]['amount']
                        diff = curr_val - prev_val
                        pct = (diff / prev_val) * 100 if prev_val != 0 else (100 if diff > 0 else 0)
                        if diff > 0: self.lbl_mom_change.config(text=f"▲ {int(diff):,}원 ({pct:.1f}%)", style="Increase.TLabel")
                        elif diff < 0: self.lbl_mom_change.config(text=f"▼ {abs(int(diff)):,}원 ({abs(pct):.1f}%)", style="Decrease.TLabel")
                        else: self.lbl_mom_change.config(text="변동 없음", style="KPI.TLabel")
                    else: self.lbl_mom_change.config(text="전월 데이터 없음", style="KPI.TLabel")
                except: self.lbl_mom_change.config(text="-", style="KPI.TLabel")

                self.lbl_avg_val.config(text=f"{int(self.monthly_summary['amount'].mean()):,}원")
                max_row = self.monthly_summary.loc[self.monthly_summary['amount'].idxmax()]
                self.lbl_max_month.config(text=f"{max_row['month']}")

        if 'category_analysis' in self.display_sections:
            self.update_category_analysis(target_month)
            if self.left_analysis: self.left_analysis.config(text=f" {target_month} 전월 대비 카테고리별 증감 ")

        if 'top_merchants' in self.display_sections:
            self.update_top_merchants(target_month)
            if self.right_analysis: self.right_analysis.config(text=f" {target_month} 주요 소비처 Top 5 ")
        
        if 'chart' in self.display_sections:
            self.draw_modern_chart(self.monthly_summary)

    def update_category_analysis(self, target_month):
        if not self.tree_category: return
        for item in self.tree_category.get_children(): self.tree_category.delete(item)
        try:
            target_idx = self.all_months.index(target_month)
            if target_idx < 1: return
            prev_month = self.all_months[target_idx - 1]
            cat_pivot = self.filtered_df.pivot_table(index='category', columns='month', values='amount', aggfunc='sum').fillna(0)

            if target_month not in cat_pivot.columns: cat_pivot[target_month] = 0.0
            if prev_month not in cat_pivot.columns: cat_pivot[prev_month] = 0.0

            diff_df = cat_pivot[[prev_month, target_month]].copy()
            diff_df['diff'] = diff_df[target_month] - diff_df[prev_month]
            diff_df = diff_df.sort_values('diff', ascending=False)
            for cat, row in diff_df.iterrows():
                if row[prev_month] == 0 and row[target_month] == 0: continue
                prev_val, curr_val, diff = f"{int(row[prev_month]):,}원", f"{int(row[target_month]):,}원", row['diff']
                if diff > 0: diff_str, tags = f"▲ {int(diff):,}원", ('increase',)
                elif diff < 0: diff_str, tags = f"▼ {abs(int(diff)):,}원", ('decrease',)
                else: diff_str, tags = "-", ()
                self.tree_category.insert("", tk.END, values=(cat, prev_val, curr_val, diff_str), tags=tags)
            self.tree_category.tag_configure('increase', foreground='#e53935')
            self.tree_category.tag_configure('decrease', foreground='#1e88e5')
        except: pass

    def update_top_merchants(self, target_month):
        if not self.tree_merchants: return
        for item in self.tree_merchants.get_children(): self.tree_merchants.delete(item)
        curr_df = self.filtered_df[self.filtered_df['month'] == target_month]
        if curr_df.empty: return
        top_m = curr_df.groupby(['category', '내용'])['amount'].sum().reset_index().sort_values('amount', ascending=False).head(5)
        for _, row in top_m.iterrows():
            self.tree_merchants.insert("", tk.END, values=(row['category'], row['내용'], f"{int(row['amount']):,}원"))

    def draw_modern_chart(self, monthly):
        if not self.ax or not self.canvas: return
        self.ax.clear()
        x, y = monthly['month'], monthly['amount']
        self.chart_y = y.tolist()
        x_indices = range(len(x))

        # 차트 기본 선 및 영역 채우기
        self.ax.fill_between(x_indices, y, color='#e3f2fd', alpha=0.5)
        self.ax.plot(x_indices, y, color='#1e88e5', marker='o', markersize=6, markerfacecolor='white', markeredgewidth=2, linewidth=2)
        self.ax.set_title("월별 총 지출 추이", fontsize=12, pad=15, fontweight='bold', color='#333333')

        # 축 및 그리드 설정
        for spine in self.ax.spines.values(): spine.set_visible(False)
        self.ax.grid(axis='y', linestyle='--', alpha=0.3)
        self.ax.tick_params(axis='both', which='both', length=0, labelsize=8, colors='#666666')

        # X축 레이블 (데이터 개수가 많을 때만 회전)
        self.ax.set_xticks(x_indices)
        if len(x) > 10:
            self.ax.set_xticklabels(x, rotation=45, ha='right')
        else:
            self.ax.set_xticklabels(x)

        # Y축 만원 단위 표시
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x/10000), ',') + '만' if x != 0 else '0'))

        # 최고점 및 선택월 강조
        max_y = max(y) if not y.empty else 0
        if max_y > 0:
            for i, val in enumerate(y):
                if i == self.selected_month_idx:
                    self.ax.plot(i, val, marker='o', markersize=10, color='#fbc02d', markeredgecolor='white', markeredgewidth=2)
                    self.ax.text(i, val + (max_y * 0.06), f'{int(val):,}원', ha='center', fontweight='bold', color='#333333', fontsize=9,
                                 bbox=dict(facecolor='#fff9c4', alpha=0.9, edgecolor='#fbc02d', boxstyle='round,pad=0.2'))
                elif val == max_y:
                    self.ax.text(i, val + (max_y * 0.03), 'Peak', ha='center', color='#fb8c00', fontsize=8, fontweight='bold')

        # 레이아웃 고정 (텍스트 길이에 따른 차트 점핑 방지)
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.2)
        self.canvas.draw()

    def show_empty_state(self):
        if not self.ax or not self.canvas: return
        self.ax.clear(); self.ax.text(0.5, 0.5, "데이터를 업로드하면 분석이 시작됩니다.", ha='center', va='center', transform=self.ax.transAxes, color='gray')
        self.ax.set_axis_off(); self.canvas.draw()
