import os
import io
import requests
import webbrowser
import json
import pandas as pd
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# main.py에서 실행 시 프로젝트 루트가 sys.path에 있으므로 바로 임포트 가능
from utils.KakaoNotifier import KakaoNotifier
import database

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.df = None
        self.mapping_rules = []
        self.selected_column = None

        # 스타일 설정
        self.style = ttk.Style()
        self.style.configure("Big.TLabel", font=("맑은 고딕", 20, "bold"))
        self.style.configure("Mid.TLabel", font=("맑은 고딕", 12))

        # UI 초기화
        self.setup_ui()

        # 앱 시작 시 DB에서 데이터 로드
        self.load_data_from_db()

    def load_rules(self):
        """DB에서 카테고리 분류 규칙을 불러옵니다."""
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT merchant, category, sub_category FROM category"
                    cursor.execute(sql)
                    self.mapping_rules = [(r['merchant'], r['category'], r['sub_category']) for r in cursor.fetchall()]
        except Exception as e:
            self.mapping_rules = []

    def setup_ui(self):
        # 1. 최상단 컨트롤 바
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Button(top_bar, text="엑셀 업로드", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="공유 (카카오톡)", command=self.share_to_kakao).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="카카오 인증", command=self.authenticate_kakao).pack(side=tk.LEFT, padx=5)

        ttk.Label(top_bar, text="조회 월:").pack(side=tk.LEFT, padx=(30, 5))
        self.shared_month_var = tk.StringVar()
        self.cb_shared_month = ttk.Combobox(top_bar, textvariable=self.shared_month_var, width=12, state="readonly")
        self.cb_shared_month.pack(side=tk.LEFT, padx=5)
        self.cb_shared_month.bind("<<ComboboxSelected>>", self.on_month_change)

        # 2. 메인 콘텐츠 프레임 (Grid 레이아웃)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)

        # --- [카드 1: 좌측 상단] 지출 차트 ---
        card_chart = ttk.LabelFrame(main_frame, text="월별 지출 현황")
        card_chart.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=card_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- [카드 2: 우측 상단] 이달의 요약 ---
        card_summary = ttk.LabelFrame(main_frame, text="이달의 요약")
        card_summary.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        summary_inner = ttk.Frame(card_summary)
        summary_inner.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(summary_inner, text="총 수입", style="Mid.TLabel", foreground="gray").pack(anchor="w")
        self.lbl_income = ttk.Label(summary_inner, text="0 원", style="Big.TLabel", foreground="blue")
        # self.lbl_income.pack(anchor="w", pady=(0, 20))

        ttk.Label(summary_inner, text="총 지출", style="Mid.TLabel", foreground="gray").pack(anchor="w")
        self.lbl_expense = ttk.Label(summary_inner, text="0 원", style="Big.TLabel", foreground="red")
        # self.lbl_expense.pack(anchor="w")

        # --- [카드 3: 하단 전체] 상세 내역 ---
        card_list = ttk.LabelFrame(main_frame, text="상세 내역")
        card_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.notebook = ttk.Notebook(card_list)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_main = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text="가계부 내역")
        self.tab_dup = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dup, text="중복 의심 내역")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.setup_main_tab_ui()
        self.setup_dup_tab_ui()

    def setup_main_tab_ui(self):
        # 상단 요약 (실질 수입/지출)
        self.summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 11, "bold"))
        self.summary_label.pack(pady=5, fill=tk.X, padx=10)

        # 상세 필터
        filter_frame = ttk.LabelFrame(self.tab_main, text="상세 필터", padding=5)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        self.type_var, self.cat_var = tk.StringVar(), tk.StringVar()
        ttk.Label(filter_frame, text="타입:").pack(side=tk.LEFT, padx=5)
        self.cb_t = ttk.Combobox(filter_frame, textvariable=self.type_var, values=["전체", "지출", "수입", "이체"], width=8, state="readonly")
        self.cb_t.set("전체")
        self.cb_t.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="대분류:").pack(side=tk.LEFT, padx=5)
        self.cb_c = ttk.Combobox(filter_frame, textvariable=self.cat_var, width=12, state="readonly")
        self.cb_c.pack(side=tk.LEFT, padx=5)

        for cb in [self.cb_t, self.cb_c]:
            cb.bind("<<ComboboxSelected>>", lambda e: self.update_main_tab())

        # 필터링된 결과 요약
        self.filtered_summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 10))
        self.filtered_summary_label.pack(pady=(5,0), fill=tk.X, padx=10)

        # 트리뷰
        self.tree_main = self.create_treeview(self.tab_main)
        self.tree_main.bind("<Button-1>", self.on_tree_click)
        self.tree_main.bind("<Control-c>", self.copy_selection_to_clipboard)

    def setup_dup_tab_ui(self):
        lbl_info = ttk.Label(self.tab_dup, text="※ 날짜, 금액, 내용, 타입이 모두 동일한 내역을 표시합니다.", foreground="gray")
        lbl_info.pack(pady=5)
        self.tree_dup = self.create_treeview(self.tab_dup)
        self.tree_dup.bind("<Button-1>", self.on_tree_click)
        self.tree_dup.bind("<Control-c>", self.copy_selection_to_clipboard)

    def create_treeview(self, parent_frame):
        cols = ("ID", "일시", "상태", "타입", "대분류", "소분류", "내용", "금액", "결제수단")
        tree = ttk.Treeview(parent_frame, columns=cols, show='headings', height=10)
        tree.column("ID", width=0, stretch=tk.NO)

        for c in cols:
            if c == "ID": continue
            width = {'내용': 250, '일시': 140, '상태': 80}.get(c, 90)
            anchor_pos = "e" if c in ['내용', '금액'] else "center"
            tree.column(c, width=width, anchor=anchor_pos)
            tree.heading(c, text=c, anchor="center")

        tree.tag_configure('income', foreground='blue')
        tree.tag_configure('expense', foreground='red')
        tree.tag_configure('muted', foreground='#888888', background='#f2f2f2')

        sc = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=sc.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(5,10))
        sc.pack(side=tk.RIGHT, fill=tk.Y, pady=(5,10))
        return tree

    def on_tree_click(self, event):
        tree = event.widget
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            col_id = tree.identify_column(event.x)
            col_idx = int(col_id.replace('#', '')) - 1
            columns = tree['columns']
            if 0 <= col_idx < len(columns):
                self.selected_column = columns[col_idx]
            else:
                self.selected_column = None
        else:
            self.selected_column = None

    def copy_selection_to_clipboard(self, event):
        tree = event.widget
        selection = tree.selection()
        if not selection: return

        if not self.selected_column:
            rows_text = []
            for item in selection:
                values = tree.item(item, 'values')[1:]
                rows_text.append("\t".join(map(str, values)))
            clipboard_text = "\n".join(rows_text)
        else:
            col_idx = list(tree['columns']).index(self.selected_column)
            col_values = []
            for item in selection:
                values = tree.item(item, 'values')
                if col_idx < len(values):
                    col_values.append(str(values[col_idx]))
            clipboard_text = "\n".join(col_values)

        self.clipboard_clear()
        self.clipboard_append(clipboard_text)

    def show_loading_window(self, title="처리 중..."):
        loading_win = tk.Toplevel(self)
        loading_win.title(title)
        loading_win.geometry("300x100")
        loading_win.resizable(False, False)
        loading_win.transient(self)
        loading_win.grab_set()

        x = self.winfo_rootx() + (self.winfo_width() // 2) - 150
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 50
        loading_win.geometry(f"+{x}+{y}")

        ttk.Label(loading_win, text="데이터를 처리하고 있습니다.\n잠시만 기다려주세요...", anchor="center").pack(pady=10)
        progress = ttk.Progressbar(loading_win, mode='determinate', length=250)
        progress.pack(pady=5)
        return loading_win, progress

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if not path: return

        loading_win, progress = self.show_loading_window("파일 업로드 중")
        self.update_idletasks()

        try:
            self.load_rules()
            progress['value'] = 10
            loading_win.update()

            df_dict = pd.read_excel(path, sheet_name=None)
            target_df = next((df_dict[s] for s in df_dict if '가계부' in s), list(df_dict.values())[0])

            progress['value'] = 30
            loading_win.update()

            processed_df = self.process_data(target_df)

            def update_progress(val):
                current = 30 + (val * 0.6)
                progress['value'] = current
                loading_win.update()

            self.save_df_to_db(processed_df, progress_callback=update_progress)

            progress['value'] = 95
            loading_win.update()
            self.load_data_from_db()
            progress['value'] = 100
            loading_win.update()

            loading_win.destroy()
            messagebox.showinfo("성공", f"총 {len(processed_df)}개의 데이터를 성공적으로 업로드했습니다.")

        except Exception as e:
            if loading_win.winfo_exists(): loading_win.destroy()
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"파일 처리 중 에러 발생:\n{e}")

    def process_data(self, df):
        header_row_idx = -1
        current_columns = [str(c).replace(" ", "") for c in df.columns]
        if not any("날짜" in c or "일자" in c for c in current_columns):
            for idx, row in df.iterrows():
                row_values = [str(val).replace(" ", "") for val in row.values if pd.notna(val)]
                if any("날짜" in val or "일자" in val for val in row_values):
                    header_row_idx = idx
                    break

        if header_row_idx is None and header_row_idx != -1:
            raise ValueError("엑셀 시트에서 '날짜' 또는 '일자' 컬럼을 찾을 수 없습니다.")

        if header_row_idx != -1:
            df.columns = df.iloc[header_row_idx]
            df = df.iloc[header_row_idx + 1:].copy().reset_index(drop=True)

        df.columns = [str(col).strip().replace(" ", "") for col in df.columns]

        col_map = {
            'date': next((c for c in df.columns if '날짜' in c or '일자' in c), None),
            'time': next((c for c in df.columns if '시간' in c), None),
            'amount': next((c for c in df.columns if '금액' in c), None),
            'desc': next((c for c in df.columns if '내용' in c or '사용내역' in c), None),
            'payment': next((c for c in df.columns if '결제수단' in c), None),
            'type': next((c for c in df.columns if '타입' in c), None),
            'cat': next((c for c in df.columns if '대분류' in c), None),
            'subcat': next((c for c in df.columns if '소분류' in c), None),
        }
        if not col_map['date'] or not col_map['amount']:
            raise ValueError("'날짜'와 '금액' 컬럼은 필수입니다.")

        df['temp_dt'] = df[col_map['date']].astype(str).str.strip()
        if col_map['time']:
            df['temp_dt'] += " " + df[col_map['time']].astype(str).str.strip()

        df['DT'] = pd.to_datetime(df['temp_dt'], errors='coerce')
        df.dropna(subset=['DT'], inplace=True)

        def clean_amount(val):
            cleaned = "".join(c for c in str(val) if c.isdigit() or c == '-')
            return cleaned if cleaned else '0'
        df['금액'] = pd.to_numeric(df[col_map['amount']].apply(clean_amount), errors='coerce').fillna(0)

        final_df = pd.DataFrame()
        final_df['DT'] = df['DT']
        final_df['금액'] = df['금액'].astype(int)
        final_df['내용'] = df[col_map['desc']] if col_map['desc'] else ""
        final_df['결제수단'] = df[col_map['payment']] if col_map['payment'] else ""
        final_df['타입'] = df[col_map['type']] if col_map['type'] else ""
        final_df['대분류'] = df[col_map['cat']] if col_map['cat'] else ""
        final_df['소분류'] = df[col_map['subcat']] if col_map['subcat'] else ""

        temp_cat = final_df.apply(self.auto_classify, axis=1)
        final_df['대분류'] = temp_cat['대분류']
        final_df['소분류'] = temp_cat['소분류']

        return final_df

    def auto_classify(self, row):
        content = str(row.get('내용', ''))
        for merchant_kw, db_cat, db_sub in self.mapping_rules:
            if str(merchant_kw) in content:
                return pd.Series({'대분류': db_cat, '소분류': db_sub})
        if row.get('대분류') and pd.notna(row.get('대분류')):
            return pd.Series({'대분류': row['대분류'], '소분류': row.get('소분류', '미분류')})
        return pd.Series({'대분류': '기타', '소분류': '미분류'})

    def save_df_to_db(self, df_to_save, progress_callback=None):
        try:
            df_to_save = df_to_save.where(pd.notnull(df_to_save), None)
            total_rows = len(df_to_save)

            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE transactions")
                    sql = "INSERT INTO transactions (transaction_date, transaction_type, description, amount, payment_method) VALUES (%s, %s, %s, %s, %s)"

                    batch_size = 100
                    for i in range(0, total_rows, batch_size):
                        batch = df_to_save.iloc[i:i+batch_size]
                        for _, row in batch.iterrows():
                            trans_type = row['타입']
                            if not trans_type:
                                trans_type = '수입' if row['금액'] > 0 else '지출'
                            cursor.execute(sql, (row['DT'], trans_type, row['내용'], row['금액'], row['결제수단']))

                        if progress_callback:
                            percent = min(100, int((i + batch_size) / total_rows * 100))
                            progress_callback(percent)
                conn.commit()
        except Exception as e:
            raise e

    def load_data_from_db(self):
        """DB에서 거래 내역을 불러오고 카테고리 및 제외(이중지출) 처리를 수행합니다."""
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM transactions")
                    trans_result = cursor.fetchall()
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules_result = cursor.fetchall()

                if not trans_result:
                    self.df = pd.DataFrame()
                    return

                self.df = pd.DataFrame(trans_result)
                self.df.rename(columns={
                    'transaction_date': 'DT', 'transaction_type': '타입',
                    'description': '내용', 'amount': '금액', 'payment_method': '결제수단'
                }, inplace=True)

                self.df['DT'] = pd.to_datetime(self.df['DT'])
                self.df['일시'] = self.df['DT'].dt.strftime('%Y-%m-%d %H:%M')
                self.df['월'] = self.df['DT'].dt.strftime('%Y-%m')
                self.df['금액'] = self.df['금액'].astype(int)

                # [중요] '우리카드결제대금' 이중지출 감지 로직
                self.df['is_double_count'] = self.df['내용'].str.contains('우리카드결제대금', na=False)

                # 카테고리 매칭 (긴 키워드 우선)
                sorted_rules = sorted(rules_result, key=lambda x: len(x['merchant']), reverse=True)
                def match_category(description):
                    for rule in sorted_rules:
                        if rule['merchant'] in str(description):
                            return pd.Series({'대분류': rule['category'], '소분류': rule['sub_category']})
                    return pd.Series({'대분류': '기타', '소분류': '미분류'})

                cats = self.df['내용'].apply(match_category)
                self.df['대분류'], self.df['소분류'] = cats['대분류'], cats['소분류']

                # 취소/선승인/가결제 로직
                self.df['abs_amt'] = self.df['금액'].abs()
                self.df['is_cancel'] = self.df.groupby([self.df['DT'].dt.date, '내용', 'abs_amt'])['금액'].transform('sum') == 0
                self.df['is_pre_auth'] = self.df['내용'].str.contains('선승인|가결제', na=False)

                self.update_filter_options()
                self.on_month_change(None)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("DB 로드 오류", f"데이터를 불러오는 중 오류가 발생했습니다.\n{e}")
            self.df = pd.DataFrame()

    def update_filter_options(self):
        if self.df is None or self.df.empty: return
        months = sorted(self.df['월'].unique().tolist(), reverse=True)
        self.cb_shared_month['values'] = months
        if months: self.shared_month_var.set(months[0])
        self.cb_c['values'] = ["전체"] + sorted(self.df['대분류'].unique().tolist())
        self.cb_c.set("전체")

    def on_month_change(self, event):
        if self.df is None or self.df.empty: return
        self.update_dashboard_chart()
        self.update_summary_card()
        self.on_tab_change(None)

    def on_tab_change(self, event):
        if self.df is None or self.df.empty: return
        try:
            if self.notebook.index('current') == 0: self.update_main_tab()
            else: self.update_dup_tab()
        except tk.TclError:
            pass

    def insert_data_to_tree(self, tree, data_df):
        tree.delete(*tree.get_children())
        for _, r in data_df.iterrows():
            # [중요] 상태 및 태그 결정 로직 (이중지출 우선 적용)
            if r.get('is_double_count', False):
                status, tag = ("이중지출", 'muted')
            elif r.get('is_cancel', False):
                status, tag = ("취소됨", 'muted')
            elif r.get('is_pre_auth', False):
                status, tag = ("선승인", 'muted')
            else:
                status, tag = ("정상", 'income' if r['금액'] > 0 else 'expense')

            tree.insert("", tk.END, values=(
                r['id'], r['일시'], status, r['타입'], r['대분류'], r['소분류'],
                r['내용'], f"{r['금액']:,}원", r.get('결제수단', '')
            ), tags=(tag,))

    def update_summary_card(self):
        if self.df is None or self.df.empty:
            self.lbl_income.config(text="0 원")
            self.lbl_expense.config(text="0 원")
            return

        month_df = self.df[self.df['월'] == self.shared_month_var.get()]

        # [중요] 실질 지출 계산 시 이중지출(카드대금) 제외
        valid_trans = month_df[
            ~month_df.get('is_cancel', False) &
            ~month_df.get('is_pre_auth', False) &
            ~month_df.get('is_double_count', False)
            ]

        pure_income = valid_trans[valid_trans['타입'] == '수입']['금액'].sum()
        pure_expense = valid_trans[valid_trans['타입'] == '지출']['금액'].sum()
        self.lbl_income.config(text=f"{pure_income:,} 원")
        self.lbl_expense.config(text=f"{abs(pure_expense):,} 원")

    def update_main_tab(self):
        if self.df is None or self.df.empty: return

        month_df = self.df[self.df['월'] == self.shared_month_var.get()]

        # 실질 수입/지출 합계 (이중지출 제외)
        valid_trans = month_df[
            ~month_df.get('is_cancel', False) &
            ~month_df.get('is_pre_auth', False) &
            ~month_df.get('is_double_count', False)
            ]
        pure_income = valid_trans[valid_trans['타입'] == '수입']['금액'].sum()
        pure_expense = valid_trans[valid_trans['타입'] == '지출']['금액'].sum()
        self.summary_label.config(text=f"[{self.shared_month_var.get()}]  실질 수입: {pure_income:,}원  |  실질 지출: {abs(pure_expense):,}원")

        # 필터링 적용
        f_df = month_df.copy()
        if self.type_var.get() != "전체": f_df = f_df[f_df['타입'] == self.type_var.get()]
        if self.cat_var.get() != "전체": f_df = f_df[f_df['대분류'] == self.cat_var.get()]

        # [중요] 필터 결과 합계 (이중지출을 포함하여 현재 보이는 그대로의 합계 표시)
        filtered_sum = f_df['금액'].sum()
        filtered_count = len(f_df)
        self.filtered_summary_label.config(text=f"조회된 내역: {filtered_count}건  |  합계: {filtered_sum:,}원")

        self.insert_data_to_tree(self.tree_main, f_df.sort_values(by=['DT', '내용']))

    def update_dup_tab(self):
        if self.df is None or self.df.empty: return
        dup_mask = self.df.duplicated(subset=['DT', '금액', '내용', '타입'], keep=False)
        self.insert_data_to_tree(self.tree_dup, self.df[dup_mask].sort_values(by=['DT', '내용']))

    def update_dashboard_chart(self):
        if self.df is None or self.df.empty:
            self.ax.clear()
            self.ax.text(0.5, 0.5, '데이터 없음', ha='center', va='center')
            self.canvas.draw()
            return

        self.ax.clear()
        # [중요] 차트에서도 이중지출 제외
        expense_df = self.df[
            (self.df['월'] == self.shared_month_var.get()) &
            (self.df['타입'] == '지출') &
            ~self.df.get('is_cancel', False) &
            ~self.df.get('is_pre_auth', False) &
            ~self.df.get('is_double_count', False)
            ]

        if expense_df.empty:
            self.ax.text(0.5, 0.5, '지출 내역 없음', ha='center', va='center')
        else:
            category_expenses = expense_df.groupby('대분류')['금액'].sum().abs().sort_values(ascending=False)
            wedges, texts, autotexts = self.ax.pie(category_expenses, labels=category_expenses.index, autopct='%1.1f%%', startangle=90, counterclock=False, wedgeprops={'width': 0.5, 'edgecolor': 'w', 'linewidth': 1}, pctdistance=0.85)
            for t in texts: t.set_fontsize(9)
            for t in autotexts: t.set_fontsize(8)
            self.ax.set_title(f'{self.shared_month_var.get()} 지출 비율', fontsize=12)
        self.canvas.draw()

    def authenticate_kakao(self):
        """test.py의 기능을 대체하여 브라우저를 통해 카카오 토큰을 갱신합니다."""
        rest_api_key = os.getenv("KAKAO_REST_API_KEY")
        redirect_uri = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:5000")

        if not rest_api_key:
            messagebox.showerror("오류", ".env 파일에 KAKAO_REST_API_KEY가 없습니다.")
            return

        # 1. 카카오 로그인 페이지 오픈
        auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
        webbrowser.open(auth_url)

        # 2. 사용자로부터 인증 코드 입력 받기 (브라우저 주소창의 code=... 부분)
        code = simpledialog.askstring("카카오 인증", "로그인 후 브라우저 주소창의 'code=' 뒷부분을 복사해서 입력하세요:")
        if not code: return

        # 3. 토큰 발급 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": rest_api_key,
            "redirect_uri": redirect_uri,
            "code": code
        }

        try:
            response = requests.post(token_url, data=data)
            tokens = response.json()
            
            if 'access_token' in tokens:
                new_access_token = tokens['access_token']
                # 메모리 내 환경변수 업데이트
                os.environ["DB_ACCOUNT_KAKAO_ACCESS_TOKEN"] = new_access_token
                
                # 공유 버튼 클릭 시 바로 반영되도록 설정
                messagebox.showinfo("성공", "카카오 인증에 성공했습니다!\n이제 '공유' 버튼을 사용할 수 있습니다.")
                print(f"DEBUG: 새 토큰 발급 완료: {new_access_token[:10]}...")
            else:
                messagebox.showerror("오류", f"토큰 발급 실패: {tokens.get('error_description', '알 수 없는 오류')}")
        except Exception as e:
            messagebox.showerror("오류", f"인증 처리 중 에러 발생: {e}")

    def share_to_kakao(self):
        """현재 대시보드 요약 내용과 차트를 카카오톡으로 공유합니다."""
        if self.df is None or self.df.empty:
            messagebox.showwarning("경고", "공유할 데이터가 없습니다.")
            return

        current_month = self.shared_month_var.get()
        month_df = self.df[self.df['월'] == current_month]
        
        # 1. 텍스트 내역 정리
        valid_trans = month_df[
            ~month_df.get('is_cancel', False) &
            ~month_df.get('is_pre_auth', False) &
            ~month_df.get('is_double_count', False)
        ]
        
        pure_income = valid_trans[valid_trans['타입'] == '수입']['금액'].sum()
        pure_expense = valid_trans[valid_trans['타입'] == '지출']['금액'].sum()
        
        category_summary = valid_trans[valid_trans['타입'] == '지출'].groupby('대분류')['금액'].sum().abs()
        
        summary_text = f"[{current_month} 가계부 요약]\n"
        summary_text += f"💰 총 수입: {pure_income:,}원\n"
        summary_text += f"💸 총 지출: {abs(pure_expense):,}원\n"
        summary_text += "--------------------\n"
        summary_text += "[카테고리별 지출]\n"
        for cat, amt in category_summary.items():
            summary_text += f"• {cat}: {amt:,}원\n"

        # 2. 이미지 캡처 (텍스트 테스트 시 무시)
        image_path = "temp_chart.png"
        try:
            if os.path.exists(image_path): os.remove(image_path)
        except:
            pass

        load_dotenv()
        access_token = os.getenv("DB_ACCOUNT_KAKAO_ACCESS_TOKEN")
        
        # 디버깅을 위해 토큰 상태를 출력합니다 (보안을 위해 앞 5자리만 출력)
        if access_token:
            print(f"DEBUG: 토큰 로드 성공 (길이: {len(access_token)}, 시작값: {access_token[:5]}...)")
        else:
            print("DEBUG: .env 파일에서 토큰을 찾을 수 없습니다.")

        if not access_token or access_token.strip() == "":
            self.clipboard_clear()
            self.clipboard_append(summary_text)
            messagebox.showinfo("안내", "API 토큰이 설정되지 않았습니다.\n요약 텍스트를 클립보드에 복사했습니다.\n카카오톡에 붙여넣기(Ctrl+V) 하세요.")
            return

        # 외부 모듈을 사용하여 전송
        notifier = KakaoNotifier(access_token)
        
        # [테스트 모드] 이미지 없이 텍스트만 전송
        image_url = None
        success, error_msg = notifier.send_report(summary_text, image_url)
        
        if success:
            messagebox.showinfo("성공", "카카오톡으로 리포트를 성공적으로 보냈습니다.")
            # 전송 성공 후 임시 이미지 삭제 (선택 사항)
            if os.path.exists(image_path):
                try: os.remove(image_path)
                except: pass
        else:
            # 에러 메시지를 사용자에게 알림
            messagebox.showerror("전송 실패", f"카카오톡 전송에 실패했습니다.\n상태 코드: {error_msg}")