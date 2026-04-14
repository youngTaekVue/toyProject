import os
import io
import requests
import webbrowser
import json
import pandas as pd
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback

# 유틸리티 임포트
from utils.KakaoNotifier import KakaoNotifier
from utils.TransactionUtil import TransactionUtil
from utils.FinancialUtil import FinancialUtil
from utils.Logger import logger
import database

# 한글 폰트 설정
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'

class TransactionView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        load_dotenv()
        self.rest_api_key = os.getenv("KAKAO_REST_API_KEY")

        self.notifier = KakaoNotifier(rest_api_key=self.rest_api_key)
        self.dashboard_util = TransactionUtil()

        self.df = pd.DataFrame() 
        self.mapping_rules = []
        self.selected_column = None
        self.current_chart_category = None
        self.legend_map = {}

        self.style = ttk.Style()
        self.style.configure("Big.TLabel", font=("맑은 고딕", 20, "bold"))
        self.style.configure("Mid.TLabel", font=("맑은 고딕", 12))

        self.setup_ui()
        self.load_data_from_db()

    def setup_ui(self):
        # 1. 상단 바
        self.top_bar = ttk.Frame(self, padding=10); self.top_bar.pack(fill=tk.X)
        ttk.Button(self.top_bar, text="엑셀 통합 업로드", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_bar, text="나에게 공유", command=self.share_to_kakao).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_bar, text="친구에게 공유", command=self.share_to_friend).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.top_bar, text="조회 월:").pack(side=tk.LEFT, padx=(30, 5))
        self.shared_month_var = tk.StringVar()
        self.cb_shared_month = ttk.Combobox(self.top_bar, textvariable=self.shared_month_var, width=12, state="readonly"); self.cb_shared_month.pack(side=tk.LEFT, padx=5)
        self.cb_shared_month.bind("<<ComboboxSelected>>", self.on_month_change)

        # 2. 메인 영역
        self.main_frame = ttk.Frame(self, padding=10); self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=2); self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.rowconfigure(0, weight=1); self.main_frame.rowconfigure(1, weight=2)

        # --- [카드 1] 차트 영역 ---
        self.card_chart = ttk.LabelFrame(self.main_frame, text="지출 현황 상세")
        self.card_chart.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        chart_ctrl = ttk.Frame(self.card_chart); chart_ctrl.pack(fill=tk.X, padx=5, pady=2)
        self.btn_chart_back = ttk.Button(chart_ctrl, text="← 전체 보기", command=self.reset_chart_view, state=tk.DISABLED); self.btn_chart_back.pack(side=tk.LEFT)
        self.lbl_chart_title = ttk.Label(chart_ctrl, text="월간 카테고리별 지출", font=("맑은 고딕", 10, "bold")); self.lbl_chart_title.pack(side=tk.LEFT, padx=10)
        self.fig = Figure(figsize=(4, 3), dpi=100); self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111); self.ax.axis('off')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.card_chart); self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        self.canvas.mpl_connect('pick_event', self.on_legend_pick)

        # --- [카드 2] 요약 정보 ---
        self.card_summary = ttk.LabelFrame(self.main_frame, text="이달의 요약")
        self.card_summary.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        inner = ttk.Frame(self.card_summary); inner.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        ttk.Label(inner, text="총 수입", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_income = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#2196F3"); self.lbl_income.pack(anchor="w", pady=(0, 15))
        ttk.Label(inner, text="총 지출", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_expense = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#F44336"); self.lbl_expense.pack(anchor="w")

        # --- [카드 3] 리스트 내역 ---
        self.card_list = ttk.LabelFrame(self.main_frame); self.card_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.notebook = ttk.Notebook(self.card_list); self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tab_main = ttk.Frame(self.notebook); self.notebook.add(self.tab_main, text="가계부 내역")
        self.tab_dup = ttk.Frame(self.notebook); self.notebook.add(self.tab_dup, text="중복 의심 내역")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.setup_main_tab_ui(); self.setup_dup_tab_ui()

    def share_to_friend(self):
        logger.log("INFO", "UI_Action", "친구에게 공유 클릭")
        friends = self.notifier.get_friends()
        if friends is None:
            if messagebox.askyesno("인증 필요", "친구 목록을 가져올 수 없습니다. 다시 인증하시겠습니까?"):
                self.authenticate_kakao()
            return
        if not friends:
            messagebox.showinfo("안내", "메시지를 보낼 수 있는 친구가 없습니다.")
            return
        win = tk.Toplevel(self); win.title("친구 선택"); win.geometry("300x400")
        win.transient(self); win.grab_set()
        lb = tk.Listbox(win); lb.pack(fill="both", expand=True, padx=10, pady=5)
        for f in friends: lb.insert("end", f.get('profile_nickname', '알 수 없음'))
        def do_send():
            idx = lb.curselection()
            if not idx: return
            uuid, nick = friends[idx[0]]['uuid'], friends[idx[0]]['profile_nickname']
            cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
            inc, exp, cat_s = self.dashboard_util.get_summary_data(m_df)
            txt = f"[{cur_m} 가계부 요약]\n💰 총 수입: {inc:,}원\n💸 총 지출: {exp:,}원\n--------------------\n[카테고리별 지출]\n"
            for c, a in cat_s.items(): txt += f"• {c}: {a:,}원\n"
            succ, err = self.notifier.send_to_friend(uuid, txt)
            if succ:
                logger.log("INFO", "KakaoShare", f"친구({nick}) 전송 성공")
                messagebox.showinfo("성공", f"{nick}님에게 전송 완료"); win.destroy()
            else:
                logger.log("ERROR", "KakaoShare", f"전송 실패: {err}")
                messagebox.showerror("실패", f"실패: {err}")
        ttk.Button(win, text="전송", command=do_send).pack(pady=10)

    def share_to_kakao(self):
        logger.log("INFO", "UI_Action", "나에게 공유 클릭")
        if self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df["월"] == cur_m]
        inc, exp, cat_s = self.dashboard_util.get_summary_data(m_df)
        txt = f"[{cur_m} 가계부 요약]\n💰 총 수입: {inc:,}원\n💸 총 지출: {exp:,}원\n--------------------\n[카테고리별 지출]\n"
        for c, a in cat_s.items(): txt += f"• {c}: {a:,}원\n"
        succ, err = self.notifier.send_report(txt)
        if succ:
            logger.log("INFO", "KakaoShare", "나에게 보내기 성공")
            messagebox.showinfo("성공", "카카오톡 전송 완료")
        else:
            logger.log("ERROR", "KakaoShare", f"전송 실패: {err}")
            messagebox.showerror("실패", f"사유: {err}")

    def update_dashboard_chart(self):
        self.ax.clear(); self.ax.axis('off'); self.legend_map = {}
        if self.df.empty: self.canvas.draw(); return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        if self.current_chart_category is None:
            _, _, data = self.dashboard_util.get_summary_data(m_df)
            self.lbl_chart_title.config(text="월간 카테고리별 지출")
        else:
            data = self.dashboard_util.get_sub_category_summary(m_df, self.current_chart_category)
            self.lbl_chart_title.config(text=f"[{self.current_chart_category}] 소분류 지출")
        if not data:
            self.ax.text(0.5, 0.5, '내역 없음', ha='center', va='center'); self.canvas.draw(); return
        self.ax.axis('on'); self.labels_in_chart = list(data.keys()); values = list(data.values())
        self.wedges, _, self.autotexts = self.ax.pie(values, autopct='%1.1f%%', startangle=90, counterclock=False, wedgeprops={'width': 0.4, 'edgecolor': 'w'}, pctdistance=0.75)
        legend_labels = [f"{l} ({v:,}원)" for l,v in data.items()]
        self.leg = self.ax.legend(self.wedges, legend_labels, loc="upper left", bbox_to_anchor=(1, 1), fontsize=8, frameon=False)
        for lp, w, t in zip(self.leg.get_patches(), self.wedges, self.autotexts):
            lp.set_picker(True); self.legend_map[lp] = (w, t)
        self.canvas.draw()

    def on_legend_pick(self, event):
        if event.artist in self.legend_map:
            w, t = self.legend_map[event.artist]; vis = not w.get_visible()
            w.set_visible(vis); t.set_visible(vis); event.artist.set_alpha(1.0 if vis else 0.2); self.canvas.draw()

    def on_chart_click(self, event):
        if event.inaxes != self.ax or not hasattr(self, 'wedges'): return
        for i, wedge in enumerate(self.wedges):
            cont, _ = wedge.contains(event)
            if cont and self.current_chart_category is None:
                sel = self.labels_in_chart[i]; logger.log("INFO", "UI_Action", f"차트 상세 진입: {sel}")
                self.current_chart_category = sel; self.btn_chart_back.config(state=tk.NORMAL)
                if hasattr(self, 'cat_var'): self.cat_var.set(sel); self.type_var.set("지출")
                self.update_main_tab(); self.update_dashboard_chart(); break

    def reset_chart_view(self):
        logger.log("INFO", "UI_Action", "차트 전체 보기 클릭")
        self.current_chart_category = None; self.btn_chart_back.config(state=tk.DISABLED)
        self.cat_var.set("전체"); self.update_main_tab(); self.update_dashboard_chart()

    def load_data_from_db(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules = cursor.fetchall(); cursor.execute("SELECT * FROM transactions"); res = cursor.fetchall()
            self.dashboard_util.mapping_rules = sorted(rules, key=lambda x: len(x['merchant']), reverse=True) if rules else []
            if not res: self.df = pd.DataFrame(); return
            self.df = pd.DataFrame(res); self.df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액', 'payment_method': '결제수단'}, inplace=True)
            self.df['DT'] = pd.to_datetime(self.df['DT']); self.df['일시'] = self.df['DT'].dt.strftime('%Y-%m-%d %H:%M'); self.df['월'] = self.df['DT'].dt.strftime('%Y-%m')
            cls_df = self.df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            self.df['대분류'], self.df['소분류'], self.df['타입'] = cls_df['대분류'], cls_df['소분류'], cls_df['타입']
            self.df['abs_amt'] = self.df['금액'].abs()
            self.df['is_cancel'] = self.df.groupby(['월', '내용', 'abs_amt'])['금액'].transform('sum') == 0
            self.df.loc[self.df['내용'].str.contains('취소|반품', na=False), 'is_cancel'] = True
            card_kws = '카드대금|결제대금|우리카드|신한카드|현대카드|삼성카드|국민카드|농협카드|하나카드'
            self.df['is_double_count'] = self.df['내용'].str.contains(card_kws, na=False) | self.df.duplicated(subset=['DT', '타입', '내용', '금액'], keep="first")
            self.update_filter_options(); self.on_month_change(None)
        except Exception: traceback.print_exc()

    def update_summary_card(self):
        if self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        inc, exp, _ = self.dashboard_util.get_summary_data(m_df)
        self.lbl_income.config(text=f"{inc:,} 원"); self.lbl_expense.config(text=f"{exp:,} 원")

    def analyze_transportation_category(self):
        if self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        trans_df = m_df[m_df['대분류'] == '교통'].copy()
        if trans_df.empty: return
        logger.log("INFO", "Analysis", f"--- [{cur_m}] 교통 카테고리 전수 조사 ---")
        for _, r in trans_df.sort_values(by='abs_amt', ascending=False).head(15).iterrows():
            f = "[취소됨]" if r['is_cancel'] else ("[이중지출]" if r['is_double_count'] else "[정상]")
            logger.log("INFO", "Analysis", f"{f} {r['일시']} | {r['내용']} | {r['금액']:,}원")

    def on_month_change(self, event):
        self.update_dashboard_chart(); self.update_summary_card(); self.analyze_transportation_category(); self.on_tab_change(None)

    def on_tab_change(self, event):
        try:
            idx = self.notebook.index('current')
            self.update_main_tab() if idx == 0 else self.update_dup_tab()
        except: pass

    def update_main_tab(self):
        if self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        f_df = m_df.copy()
        if hasattr(self, 'type_var') and self.type_var.get() != "전체": f_df = f_df[f_df['타입'] == self.type_var.get()]
        if hasattr(self, 'cat_var') and self.cat_var.get() != "전체": f_df = f_df[f_df['대분류'] == self.cat_var.get()]
        self.insert_data_to_tree(self.tree_main, f_df.sort_values(by=['DT', '내용']))

    def update_dup_tab(self):
        if self.df.empty: return
        mask = self.df.duplicated(subset=['DT', '금액', '내용', '타입'], keep=False)
        self.insert_data_to_tree(self.tree_dup, self.df[mask])

    def setup_main_tab_ui(self):
        self.summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 11, "bold")); self.summary_label.pack(pady=5)
        f_frame = ttk.Frame(self.tab_main); f_frame.pack(fill=tk.X, padx=10)
        self.type_var, self.cat_var = tk.StringVar(value="전체"), tk.StringVar(value="전체")
        ttk.Label(f_frame, text="타입:").pack(side=tk.LEFT, pady=10); ttk.Combobox(f_frame, textvariable=self.type_var, values=["전체", "지출", "수입"], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(f_frame, text="대분류:").pack(side=tk.LEFT, pady=10); self.cb_cat_filter = ttk.Combobox(f_frame, textvariable=self.cat_var, width=15); self.cb_cat_filter.pack(side=tk.LEFT, padx=5)
        self.type_var.trace_add("write", lambda *args: self.update_main_tab()); self.cat_var.trace_add("write", lambda *args: self.update_main_tab())
        self.tree_main = self.create_treeview(self.tab_main)

    def setup_dup_tab_ui(self): self.tree_dup = self.create_treeview(self.tab_dup)

    def create_treeview(self, parent):
        cols = ("ID", "일시", "상태", "타입", "대분류", "소분류", "내용", "금액", "결제수단")
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10); tree.column("ID", width=0, stretch=tk.NO)
        for c in cols:
            if c != "ID": tree.column(c, width=100, anchor="center"); tree.heading(c, text=c)
        tree.tag_configure('income', foreground='blue'); tree.tag_configure('expense', foreground='red'); tree.tag_configure('muted', foreground='#888888', background='#f2f2f2')
        tree.pack(fill=tk.BOTH, expand=True); return tree

    def insert_data_to_tree(self, tree, data):
        tree.delete(*tree.get_children())
        for _, r in data.iterrows():
            s, t = "정상", ('income' if r['금액'] > 0 else 'expense')
            if r['is_cancel']: s, t = "취소됨", 'muted'
            elif r['is_double_count']: s, t = "이중지출", 'muted'
            tree.insert("", tk.END, values=(r['id'], r['일시'], s, r['타입'], r['대분류'], r['소분류'], r['내용'], f"{r['금액']:,}원", r.get('결제수단', '')), tags=(t,))

    def update_filter_options(self):
        if self.df.empty: return
        months = sorted(self.df['월'].unique().tolist(), reverse=True); self.cb_shared_month['values'] = months
        if months and not self.shared_month_var.get(): self.shared_month_var.set(months[0])
        if hasattr(self, 'cb_cat_filter'): self.cb_cat_filter['values'] = ["전체"] + sorted(self.df['대분류'].unique().tolist())

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if not path: return
        try:
            excel_data = pd.read_excel(path, sheet_name=None, header=None)
            def get_sheet(kw): return next((s for s in excel_data.keys() if kw in str(s).strip()), None)
            bs_sheet = get_sheet("뱅샐현황")
            if bs_sheet:
                f_df = excel_data[bs_sheet]
                FinancialUtil.save_financial_data([(FinancialUtil.extract_section(f_df, "자산", 1, 4), "자산"), (FinancialUtil.extract_section(f_df, "부채", 5, 7), "부채")])
                FinancialUtil.save_insurance_data(FinancialUtil.extract_section(f_df, "보험현황"))
                FinancialUtil.save_investment_data(FinancialUtil.extract_section(f_df, "투자현황"))
            acc_sheet = get_sheet("가계부 내역")
            if acc_sheet:
                df = self.dashboard_util.process_excel_data(excel_data[acc_sheet])
                with database.get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT transaction_date, amount, description, transaction_type FROM transactions")
                        existing = {(r['transaction_date'].strftime('%Y-%m-%d %H:%M:%S'), int(r['amount']), str(r['description']).strip(), r['transaction_type']) for r in cursor.fetchall()}
                        new_recs = []
                        for _, row in df.iterrows():
                            desc = str(row['내용']).strip()
                            if desc and not pd.isna(row['DT']) and (row['DT'].strftime('%Y-%m-%d %H:%M:%S'), int(row['금액']), desc, row['타입']) not in existing:
                                new_recs.append((row['DT'], row['타입'], desc, row['금액'], row.get('결제수단', '')))
                        if new_recs:
                            cursor.executemany("INSERT INTO transactions (transaction_date, transaction_type, description, amount, payment_method) VALUES (%s, %s, %s, %s, %s)", new_recs)
                            conn.commit(); logger.log("INFO", "TransactionDB", f"가계부 내역 {len(new_recs)}건 저장 완료")
            logger.log("INFO", "FileUpload", f"엑셀 업로드 성공"); self.load_data_from_db(); messagebox.showinfo("완료", "데이터 업로드 완료")
        except Exception: traceback.print_exc()

    def authenticate_kakao(self):
        uri = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:5000")
        if not self.rest_api_key: return False
        webbrowser.open(f"https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={uri}&response_type=code")
        code = simpledialog.askstring("카카오 인증", "코드 입력:")
        if not code: return False
        succ, msg = self.notifier.issue_token(code, uri)
        if succ: messagebox.showinfo("성공", "인증 성공"); return True
        else: messagebox.showerror("오류", msg); return False

    def on_tree_click(self, event): pass
    def copy_selection_to_clipboard(self, event): pass
