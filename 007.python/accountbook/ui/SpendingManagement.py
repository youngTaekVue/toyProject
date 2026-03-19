import tkinter as tk
from tkinter import ttk, messagebox
import requests  # API 호출을 위한 requests 모듈
import database  # 공통 DB 모듈 임포트
# 월별 그래프를 그리기 위해 matplotlib와 numpy를 추가합니다.
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class SpendingManagement(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 한글 폰트가 깨지는 현상을 방지하기 위해 폰트를 설정합니다.
        # 시스템에 맞는 폰트로 변경해야 할 수 있습니다. (예: 'Malgun Gothic', 'AppleGothic')
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지
        except Exception as e:
            print(f"폰트 설정 오류: {e}. 다른 폰트를 시도해 보세요.")

        # 그래프를 표시할 프레임을 생성합니다.
        graph_frame = ttk.LabelFrame(self, text="월별 수입/지출 현황")
        graph_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Matplotlib Figure 및 Axes 객체를 생성합니다.
        self.fig, self.ax = plt.subplots(figsize=(10, 4), dpi=100)

        # Figure를 Tkinter에 임베드하기 위한 Canvas를 생성합니다.
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 초기 그래프를 그립니다.
        self.plot_monthly_summary()

    def fetch_monthly_summary_data(self):
        """
        API를 통해 월별 총 수입 및 지출 데이터를 가져옵니다.
        transactions 테이블에서 월별 수입/지출 합계를 집계하여 반환합니다.
        """
        data = []
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # MySQL 쿼리: DATE_FORMAT 함수 사용
                    query = """
                        SELECT DATE_FORMAT(transaction_date, '%Y-%m') as month,
                               SUM(CASE WHEN [수입/지출_구분_컬럼명] IN ('수입', 'income') THEN amount ELSE 0 END) as total_income,
                               SUM(CASE WHEN [수입/지출_구분_컬럼명] IN ('지출', 'expenditure') THEN amount ELSE 0 END) as total_expenditure
                        FROM transactions
                        GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
                        ORDER BY month ASC
                    """
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    # DictCursor를 사용하므로 딕셔너리 형태로 바로 접근
                    for row in rows:
                        if row['month']:
                            data.append(row)
        except Exception as e:
            print(f"데이터 조회 오류: {e}")

        return data

    def plot_monthly_summary(self):
        """가져온 데이터를 사용하여 월별 수입/지출 막대 그래프를 그립니다."""
        self.ax.clear()
        data = self.fetch_monthly_summary_data()

        if not data:
            self.ax.text(0.5, 0.5, "표시할 데이터가 없습니다.", ha='center', va='center')
            self.canvas.draw()
            return

        months = [item['month'].split('-')[1] + '월' for item in data]
        incomes = [item['total_income'] for item in data]
        expenditures = [item['total_expenditure'] for item in data]

        x = np.arange(len(months))
        width = 0.35

        self.ax.bar(x - width / 2, incomes, width, label='총 수입', color='cornflowerblue')
        self.ax.bar(x + width / 2, expenditures, width, label='총 지출', color='salmon')

        self.ax.set_ylabel('금액 (원)')
        self.ax.set_title('월별 총 수입 및 총 지출')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(months)
        self.ax.legend()

        # Y축 눈금에 쉼표(,)를 추가하여 가독성을 높입니다.
        self.ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda y, p: format(int(y), ','))
        )

        self.fig.tight_layout()
        self.canvas.draw()
