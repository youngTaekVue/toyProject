import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
import seaborn as sns
import datetime

import database

# 한글 폰트 및 스타일 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font="Malgun Gothic")

class SpendingManagement(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.df = None

        self.setup_ui()
        self.load_data()

        self.bind("<Configure>", self.on_resize)
        self.last_size = (0, 0)

    def setup_ui(self):
        # 1. 상단 컨트롤 바 (연도/월 선택)
        ctrl_frame = ttk.Frame(self, padding=10)
        ctrl_frame.pack(fill=tk.X)

        ttk.Label(ctrl_frame, text="조회 연도:").pack(side=tk.LEFT, padx=5)

        self.year_var = tk.StringVar()
        current_year = datetime.datetime.now().year
        start_year = max(current_year, 2026)
        self.cb_year = ttk.Combobox(ctrl_frame, textvariable=self.year_var, width=8, state="readonly")
        self.cb_year['values'] = [str(y) for y in range(start_year, 2020, -1)]
        self.cb_year.set(str(start_year))
        self.cb_year.pack(side=tk.LEFT, padx=5)
        self.cb_year.bind("<<ComboboxSelected>>", self.draw_charts)

        ttk.Label(ctrl_frame, text="조회 월:").pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar()
        self.cb_month = ttk.Combobox(ctrl_frame, textvariable=self.month_var, width=5, state="readonly")
        self.cb_month['values'] = [f"{m:02d}" for m in range(1, 13)]
        self.cb_month.set(f"{datetime.datetime.now().month:02d}")
        self.cb_month.pack(side=tk.LEFT, padx=5)
        self.cb_month.bind("<<ComboboxSelected>>", self.draw_charts)

        ttk.Button(ctrl_frame, text="새로고침", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # 2. 차트 영역
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # [수정] 차트 레이아웃 재구성
        self.fig = plt.figure(figsize=(12, 8))
        gs = gridspec.GridSpec(2, 2, figure=self.fig)
        self.ax3 = self.fig.add_subplot(gs[0, :])  # 월별 지출 추이 (상단 전체)
        self.ax2 = self.fig.add_subplot(gs[1, 0])  # 카테고리별 지출 (월) (하단 좌측)
        self.ax4 = self.fig.add_subplot(gs[1, 1])  # 연간 최고 지출 (하단 우측)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_resize(self, event):
        if self.last_size != (event.width, event.height):
            self.draw_charts()
            self.last_size = (event.width, event.height)

    def load_data(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT transaction_date, transaction_type, description, amount FROM transactions")
                    trans_result = cursor.fetchall()
                    cursor.execute("SELECT merchant, category FROM category")
                    rules_result = cursor.fetchall()

            if not trans_result:
                messagebox.showinfo("알림", "데이터가 없습니다.")
                return

            self.df = pd.DataFrame(trans_result)

            self.df['DT'] = pd.to_datetime(self.df['transaction_date'])
            self.df['year'] = self.df['DT'].dt.year.astype(str)
            self.df['month'] = self.df['DT'].dt.month
            self.df['amount'] = self.df['amount'].astype(int)

            sorted_rules = sorted(rules_result, key=lambda x: len(x['merchant']), reverse=True)

            def match_category(description):
                for rule in sorted_rules:
                    if rule['merchant'] in str(description):
                        return rule['category']
                return '미분류'

            self.df['category'] = self.df['description'].apply(match_category)

            years = sorted(self.df['year'].unique(), reverse=True)
            if years:
                valid_years = [y for y in years if int(y) >= 2026]
                if not valid_years: valid_years = [str(datetime.datetime.now().year)]
                self.cb_year['values'] = valid_years
                if self.year_var.get() not in valid_years: self.year_var.set(valid_years[0])

            self.draw_charts()

        except Exception as e:
            messagebox.showerror("오류", f"데이터 로드 실패: {e}")

    def draw_charts(self, event=None):
        if self.df is None or self.df.empty: return

        selected_year = self.year_var.get()
        selected_month = int(self.month_var.get())

        df_year = self.df[self.df['year'] == selected_year].copy()

        # [수정] ax1 제거
        for ax in [self.ax2, self.ax3, self.ax4]: ax.clear()

        if df_year.empty:
            self.ax3.text(0.5, 0.5, f"{selected_year}년 데이터가 없습니다.", ha='center', va='center')
            self.canvas.draw()
            return

        # --- 1. (상단 전체) 월별 지출 추이 ---
        # [수정] 순수 지출만 필터링 (저축, 자산이동 등 비소비성 이체 제외)
        # 제외하고 싶은 카테고리명을 아래 리스트에 추가하세요.
        exclude_categories = ['저축', '자산이동', '이체', '투자']
        
        # transaction_type이 '지출'이면서, 카테고리가 제외 목록에 없는 것만 선택
        df_year_expense = df_year[(df_year['transaction_type'] == '지출') & 
                                  (~df_year['category'].isin(exclude_categories))]
                                  
        monthly_expense_sum = df_year_expense.groupby('month')['amount'].sum().abs().reindex(range(1, 13), fill_value=0)

        sns.lineplot(data=monthly_expense_sum, marker='o', ax=self.ax3)
        self.ax3.set_title(f"{selected_year}년 월별 지출 추이", fontsize=12)
        self.ax3.set_xlabel("월")
        self.ax3.set_ylabel("금액 (원)")
        self.ax3.set_xticks(range(1, 13))

        # --- 2. (하단 좌측) 카테고리별 지출 (월) ---
        df_month_expense = df_year[(df_year['month'] == selected_month) & (df_year['transaction_type'] == '지출')]

        if df_month_expense.empty:
            self.ax2.text(0.5, 0.5, f"{selected_month}월 지출 내역 없음", ha='center', va='center')
        else:
            cat_month_sum = df_month_expense.groupby('category')['amount'].sum().abs().sort_values(ascending=False)

            wedges, texts, autotexts = self.ax2.pie(cat_month_sum, autopct='%1.1f%%',
                                                    startangle=90, counterclock=False,
                                                    wedgeprops={'width': 0.4, 'edgecolor': 'w'},
                                                    pctdistance=0.85)

            self.ax2.legend(wedges, cat_month_sum.index,
                            title="카테고리",
                            loc="center left",
                            bbox_to_anchor=(1, 0, 0.5, 1),
                            fontsize=8,
                            title_fontsize=9)

            for autotext in autotexts:
                autotext.set_fontsize(8)

        self.ax2.set_title(f"{selected_year}년 {selected_month}월 지출 구성", fontsize=12)

        # --- 3. (하단 우측) 연간 최고 지출 카테고리 ---
        self.ax4.axis('off')
        self.ax4.set_title(f"{selected_year}년 지출 TOP 5", fontsize=12)

        if not df_year_expense.empty:
            top5_cat = df_year_expense.groupby('category')['amount'].sum().abs().nlargest(5)

            y_pos = 0.8
            for i, (cat, amount) in enumerate(top5_cat.items()):
                text = f"{i+1}. {cat}"
                amount_text = f"{amount:,.0f} 원"

                self.ax4.text(0.05, y_pos, text, fontsize=11, va='center')
                self.ax4.text(0.95, y_pos, amount_text, fontsize=11, va='center', ha='right')
                y_pos -= 0.15

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()