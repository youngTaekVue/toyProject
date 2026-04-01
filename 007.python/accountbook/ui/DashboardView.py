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
from utils.DashboardUtil import DashboardUtil
from utils.FinancialUtil import FinancialUtil
import database

# 한글 폰트 설정
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'

class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        load_dotenv()
        self.rest_api_key = os.getenv("KAKAO_REST_API_KEY")
        
        self.notifier = KakaoNotifier(rest_api_key=self.rest_api_key)
        self.dashboard_util = DashboardUtil()

        self.df = None
        self.mapping_rules = []
        self.selected_column = None
        self.current_chart_category = None

        self.style = ttk.Style()
        self.style.configure("Big.TLabel", font=("맑은 고딕", 20, "bold"))
        self.style.configure("Mid.TLabel", font=("맑은 고딕", 12))

        self.setup_ui()
        self.load_data_from_db()

    def setup_ui(self):
        # 1. 상단 바
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Button(top_bar, text="엑셀 통합 업로드", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="나에게 공유", command=self.share_to_kakao).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="친구에게 공유", command=self.share_to_friend).pack(side=tk.LEFT, padx=5)

        ttk.Label(top_bar, text="조회 월:").pack(side=tk.LEFT, padx=(30, 5))
        self.shared_month_var = tk.StringVar()
        self.cb_shared_month = ttk.Combobox(top_bar, textvariable=self.shared_month_var, width=12, state="readonly")
        self.cb_shared_month.pack(side=tk.LEFT, padx=5)
        self.cb_shared_month.bind("<<ComboboxSelected>>", self.on_month_change)

        # 2. 메인 영역
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1); main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1); main_frame.rowconfigure(1, weight=2)

        # --- [카드 1] 차트 영역 ---
        self.card_chart = ttk.LabelFrame(main_frame, text="지출 현황 상세")
        self.card_chart.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        chart_ctrl = ttk.Frame(self.card_chart); chart_ctrl.pack(fill=tk.X, padx=5, pady=2)
        self.btn_chart_back = ttk.Button(chart_ctrl, text="← 전체 보기", command=self.reset_chart_view, state=tk.DISABLED)
        self.btn_chart_back.pack(side=tk.LEFT)
        self.lbl_chart_title = ttk.Label(chart_ctrl, text="월간 카테고리별 지출", font=("맑은 고딕", 10, "bold"))
        self.lbl_chart_title.pack(side=tk.LEFT, padx=10)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.card_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)

        # --- [카드 2] 요약 정보 ---
        card_summary = ttk.LabelFrame(main_frame, text="이달의 요약")
        card_summary.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        inner = ttk.Frame(card_summary); inner.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        ttk.Label(inner, text="총 수입", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_income = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#2196F3"); self.lbl_income.pack(anchor="w", pady=(0, 15))
        ttk.Label(inner, text="총 지출", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_expense = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#F44336"); self.lbl_expense.pack(anchor="w")

        # --- [카드 3] 리스트 내역 ---
        card_list = ttk.LabelFrame(main_frame, text="상세 내역")
        card_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.notebook = ttk.Notebook(card_list); self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tab_main = ttk.Frame(self.notebook); self.notebook.add(self.tab_main, text="가계부 내역")
        self.tab_dup = ttk.Frame(self.notebook); self.notebook.add(self.tab_dup, text="중복 의심 내역")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.setup_main_tab_ui(); self.setup_dup_tab_ui()

    def share_to_friend(self):
        """카카오톡 친구 목록을 가져와서 선택한 친구에게 전송합니다."""
        friends = self.notifier.get_friends()
        
        if friends is None:
            if messagebox.askyesno("권한 필요", "친구 목록을 가져올 수 없습니다. 다시 인증하시겠습니까? (friends 권한 필요)"):
                self.authenticate_kakao()
            return

        if not friends:
            messagebox.showinfo("안내", "메시지를 보낼 수 있는 친구가 없습니다.\n(팀원 등록 또는 권한 동의 필요)")
            return

        # 친구 선택 팝업 생성
        win = tk.Toplevel(self)
        win.title("친구 선택")
        win.geometry("300x400")
        win.transient(self); win.grab_set()

        ttk.Label(win, text="리포트를 보낼 친구를 선택하세요:", padding=10).pack()
        
        lb = tk.Listbox(win)
        lb.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 친구 이름 표시
        for f in friends:
            lb.insert("end", f.get('profile_nickname', '알 수 없음'))

        def do_send():
            idx = lb.curselection()
            if not idx: return
            
            uuid = friends[idx[0]]['uuid']
            nickname = friends[idx[0]]['profile_nickname']
            
            cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
            inc, exp, cat_s = self.dashboard_util.get_summary_data(m_df)
            
            txt = f"[{cur_m} 가계부 요약]\n💰 총 수입: {inc:,}원\n💸 총 지출: {exp:,}원\n--------------------\n[카테고리별 지출]\n"
            for c, a in cat_s.items(): txt += f"• {c}: {a:,}원\n"
            
            success, err = self.notifier.send_to_friend(uuid, txt)
            if success:
                messagebox.showinfo("성공", f"{nickname}님에게 리포트를 보냈습니다.")
                win.destroy()
            else:
                messagebox.showerror("실패", f"전송 실패: {err}")

        ttk.Button(win, text="전송", command=do_send).pack(pady=10)

    def share_to_kakao(self):
        """나에게 공유하기"""
        if self.df is None or self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        inc, exp, cat_s = self.dashboard_util.get_summary_data(m_df)
        txt = f"[{cur_m} 가계부 요약]\n💰 총 수입: {inc:,}원\n💸 총 지출: {exp:,}원\n--------------------\n[카테고리별 지출]\n"
        if not cat_s: txt += "• 지출 내역 없음\n"
        else:
            for c, a in cat_s.items(): txt += f"• {c}: {a:,}원\n"
        
        succ, err = self.notifier.send_report(txt)
        if not succ and ("유효한 토큰" in err or "인증" in err):
            if messagebox.askyesno("인증 필요", "카카오 인증 정보가 만료되었습니다. 인증하시겠습니까?"):
                if self.authenticate_kakao(): self.notifier.send_report(txt)
        elif succ: messagebox.showinfo("성공", "카카오톡 전송 완료!")
        else: messagebox.showerror("실패", f"사유: {err}")

    # --- 기존 차트 및 데이터 로드 로직 유지 ---
    def update_dashboard_chart(self):
        if self.df is None or self.df.empty:
            self.ax.clear(); self.ax.text(0.5, 0.5, '데이터 없음', ha='center', va='center'); self.canvas.draw(); return
        self.ax.clear()
        m_df = self.df[self.df['월'] == self.shared_month_var.get()]
        if self.current_chart_category is None:
            _, _, data_dict = self.dashboard_util.get_summary_data(m_df)
        else:
            data_dict = self.dashboard_util.get_sub_category_summary(m_df, self.current_chart_category)
        if not data_dict:
            self.ax.text(0.5, 0.5, '내역 없음', ha='center', va='center')
        else:
            self.labels_in_chart = list(data_dict.keys())
            values = list(data_dict.values())
            total = sum(values)
            legend_labels = [f"{label} ({val/total*100:.1f}%)" for label, val in zip(self.labels_in_chart, values)]
            self.wedges, texts, autotexts = self.ax.pie(values, autopct='%1.1f%%', startangle=90, counterclock=False, wedgeprops={'width': 0.4, 'edgecolor': 'w'}, pctdistance=0.75)
            self.ax.legend(self.wedges, legend_labels, title="지출 항목 (%)", loc="upper left", bbox_to_anchor=(1, 1), fontsize=8, frameon=False)
            plt.setp(autotexts, size=8, weight="bold", color="black")
        self.fig.subplots_adjust(left=0.05, right=0.65, top=0.9, bottom=0.1); self.canvas.draw()

    def reset_chart_view(self):
        self.current_chart_category = None; self.btn_chart_back.config(state=tk.DISABLED); self.lbl_chart_title.config(text="월간 카테고리별 지출")
        self.cat_var.set("전체"); self.update_main_tab(); self.update_dashboard_chart()

    def on_chart_click(self, event):
        if event.inaxes != self.ax or not hasattr(self, 'wedges'): return
        for i, wedge in enumerate(self.wedges):
            if wedge.contains_point([event.x, event.y]):
                selected = self.labels_in_chart[i]
                if self.current_chart_category is None:
                    self.current_chart_category = selected; self.btn_chart_back.config(state=tk.NORMAL)
                    self.lbl_chart_title.config(text=f"[{selected}] 소분류 지출 비율")
                    self.type_var.set("지출"); self.cat_var.set(selected)
                    self.update_main_tab(); self.update_dashboard_chart()
                break

    def load_data_from_db(self):
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT merchant, category, sub_category FROM category")
                    rules = cursor.fetchall()
                    cursor.execute("SELECT * FROM transactions")
                    res = cursor.fetchall()
            self.mapping_rules = rules; self.dashboard_util.mapping_rules = sorted(rules, key=lambda x: len(x['merchant']), reverse=True) if rules else []
            if not res: self.df = pd.DataFrame(); return
            self.df = pd.DataFrame(res)
            self.df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액', 'payment_method': '결제수단'}, inplace=True)
            self.df['DT'] = pd.to_datetime(self.df['DT'])
            self.df['일시'] = self.df['DT'].dt.strftime('%Y-%m-%d %H:%M'); self.df['월'] = self.df['DT'].dt.strftime('%Y-%m')
            cats = self.df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            self.df['대분류'], self.df['소분류'] = cats['대분류'], cats['소분류']
            self.df['abs_amt'] = self.df['금액'].abs()
            self.df['is_cancel'] = self.df.groupby([self.df['DT'].dt.date, '내용', 'abs_amt'])['금액'].transform('sum') == 0
            self.df['is_pre_auth'] = self.df['내용'].str.contains('선승인|가결제', na=False)
            self.df['is_double_count'] = self.df['내용'].str.contains('우리카드결제대금', na=False)
            self.update_filter_options(); self.on_month_change(None)
        except Exception: traceback.print_exc(); self.df = pd.DataFrame()

    def update_summary_card(self):
        self.lbl_income.config(text="***,*** 원"); self.lbl_expense.config(text="***,*** 원")

    def on_month_change(self, event):
        if self.df is None or self.df.empty: return
        self.update_dashboard_chart(); self.update_summary_card(); self.on_tab_change(None)

    def on_tab_change(self, event):
        if self.df is None or self.df.empty: return
        try:
            if self.notebook.index('current') == 0: self.update_main_tab()
            else: self.update_dup_tab()
        except Exception: pass

    def update_main_tab(self):
        if self.df is None or self.df.empty: return
        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        self.summary_label.config(text=f"[{cur_m}] 실질 수입: ***,***원 | 실질 지출: ***,***원")
        f_df = m_df.copy()
        if self.type_var.get() != "전체": f_df = f_df[f_df['타입'] == self.type_var.get()]
        if self.cat_var.get() != "전체": f_df = f_df[f_df['대분류'] == self.cat_var.get()]
        self.filtered_summary_label.config(text=f"조회된 내역: {len(f_df)}건 | 합계: ***,***원")
        self.insert_data_to_tree(self.tree_main, f_df.sort_values(by=['DT', '내용']))

    def update_dup_tab(self):
        if self.df is None or self.df.empty: return
        mask = self.df.duplicated(subset=['DT', '금액', '내용', '타입'], keep=False)
        self.insert_data_to_tree(self.tree_dup, self.df[mask].sort_values(by=['DT', '내용']))

    def setup_main_tab_ui(self):
        self.summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 11, "bold")); self.summary_label.pack(pady=5, fill=tk.X, padx=10)
        filter_frame = ttk.LabelFrame(self.tab_main, text="상세 필터", padding=5); filter_frame.pack(fill=tk.X, padx=10, pady=5)
        self.type_var, self.cat_var = tk.StringVar(), tk.StringVar()
        ttk.Label(filter_frame, text="타입:").pack(side=tk.LEFT, padx=5)
        self.cb_t = ttk.Combobox(filter_frame, textvariable=self.type_var, values=["전체", "지출", "수입", "이체"], width=8, state="readonly"); self.cb_t.set("전체"); self.cb_t.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="대분류:").pack(side=tk.LEFT, padx=5)
        self.cb_c = ttk.Combobox(filter_frame, textvariable=self.cat_var, width=12, state="readonly"); self.cb_c.pack(side=tk.LEFT, padx=5)
        for cb in [self.cb_t, self.cb_c]: cb.bind("<<ComboboxSelected>>", lambda e: self.update_main_tab())
        self.filtered_summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 10)); self.filtered_summary_label.pack(pady=(5,0), fill=tk.X, padx=10)
        self.tree_main = self.create_treeview(self.tab_main)
        self.tree_main.bind("<Button-1>", self.on_tree_click); self.tree_main.bind("<Control-c>", self.copy_selection_to_clipboard)

    def setup_dup_tab_ui(self):
        ttk.Label(self.tab_dup, text="※ 날짜, 금액, 내용, 타입이 모두 동일한 내역을 표시합니다.", foreground="gray").pack(pady=5)
        self.tree_dup = self.create_treeview(self.tab_dup)
        self.tree_dup.bind("<Button-1>", self.on_tree_click); self.tree_dup.bind("<Control-c>", self.copy_selection_to_clipboard)

    def create_treeview(self, parent):
        cols = ("ID", "일시", "상태", "타입", "대분류", "소분류", "내용", "금액", "결제수단")
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=10); tree.column("ID", width=0, stretch=tk.NO)
        for c in cols:
            if c == "ID": continue
            w = {'내용': 250, '일시': 140, '상태': 80}.get(c, 90)
            tree.column(c, width=w, anchor="e" if c in ['내용', '금액'] else "center"); tree.heading(c, text=c, anchor="center")
        tree.tag_configure('income', foreground='blue'); tree.tag_configure('expense', foreground='red'); tree.tag_configure('muted', foreground='#888888', background='#f2f2f2')
        sc = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscrollcommand=sc.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(5,10)); sc.pack(side=tk.RIGHT, fill=tk.Y, pady=(5,10))
        return tree

    def insert_data_to_tree(self, tree, data):
        tree.delete(*tree.get_children())
        for _, r in data.iterrows():
            if r.get('is_double_count'): s, t = "이중지출", 'muted'
            elif r.get('is_cancel'): s, t = "취소됨", 'muted'
            elif r.get('is_pre_auth'): s, t = "선승인", 'muted'
            else: s, t = "정상", ('income' if r['금액'] > 0 else 'expense')
            tree.insert("", tk.END, values=(r['id'], r['일시'], s, r['타입'], r['대분류'], r['소분류'], r['내용'], f"{r['금액']:,}원", r.get('결제수단', '')), tags=(t,))

    def on_tree_click(self, event):
        region = event.widget.identify("region", event.x, event.y)
        if region == "cell":
            col_id = event.widget.identify_column(event.x); col_idx = int(col_id.replace('#', '')) - 1
            if 0 <= col_idx < len(event.widget['columns']): self.selected_column = event.widget['columns'][col_idx]
            else: self.selected_column = None
        else: self.selected_column = None

    def update_filter_options(self):
        if self.df is None or self.df.empty: return
        months = sorted(self.df['월'].unique().tolist(), reverse=True)
        self.cb_shared_month['values'] = months
        if months: self.shared_month_var.set(months[0])
        self.cb_c['values'] = ["전체"] + sorted(self.df['대분류'].unique().tolist()); self.cb_c.set("전체")

    def copy_selection_to_clipboard(self, event):
        tree = event.widget; selection = tree.selection()
        if not selection: return
        rows = []
        for item in selection:
            values = tree.item(item, 'values')
            if self.selected_column:
                idx = list(tree['columns']).index(self.selected_column); rows.append(str(values[idx]))
            else: rows.append("\t".join(map(str, values[1:])))
        self.clipboard_clear(); self.clipboard_append("\n".join(rows))

    def show_loading_window(self, title="처리 중..."):
        win = tk.Toplevel(self); win.title(title); win.geometry("300x100"); win.resizable(False, False); win.transient(self); win.grab_set()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 150; y = self.winfo_rooty() + (self.winfo_height() // 2) - 50; win.geometry(f"+{x}+{y}")
        ttk.Label(win, text="데이터를 처리하고 있습니다.\n잠시만 기다려주세요...", anchor="center").pack(pady=10)
        progress = ttk.Progressbar(win, mode='determinate', length=250); progress.pack(pady=5)
        return win, progress

    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if not path: return
        loading_win, progress = self.show_loading_window("통합 업로드 중")
        self.update_idletasks()
        try:
            excel_data = pd.read_excel(path, sheet_name=None, header=None)
            sheet_names = list(excel_data.keys())
            summary_msgs = []
            def get_sheet(kw): return next((s for s in sheet_names if kw in str(s).strip()), None)
            bs_sheet = get_sheet('뱅크샐러드')
            if bs_sheet:
                full_df = excel_data[bs_sheet]
                assets = FinancialUtil.extract_section(full_df, '자산', 1, 4); debts = FinancialUtil.extract_section(full_df, '부채', 5, 7)
                FinancialUtil.save_financial_data([(assets, '자산'), (debts, '부채')])
                ins = FinancialUtil.extract_section(full_df, '보험현황'); FinancialUtil.save_insurance_data(ins)
                inv = FinancialUtil.extract_section(full_df, '투자현황'); FinancialUtil.save_investment_data(inv)
                summary_msgs.append("• 뱅크샐러드 현황 업로드 완료")
            acc_sheet = get_sheet('가계부')
            if acc_sheet:
                df = self.dashboard_util.process_excel_data(excel_data[acc_sheet]); self.save_df_to_db(df); summary_msgs.append(f"• 가계부: {len(df)}건")
            self.load_data_from_db(); progress['value'] = 100; loading_win.update(); loading_win.destroy()
            messagebox.showinfo("완료", "\n".join(summary_msgs) if summary_msgs else "인식된 데이터가 없습니다.")
        except Exception as e:
            if loading_win.winfo_exists(): loading_win.destroy()
            traceback.print_exc(); messagebox.showerror("오류", str(e))

    def authenticate_kakao(self):
        uri = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:5000")
        if not self.rest_api_key: return False
        webbrowser.open(f"https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={uri}&response_type=code")
        code = simpledialog.askstring("카카오 인증", "로그인 후 브라우저 주소창의 'code=' 뒷부분을 복사해서 입력하세요:")
        if not code: return False
        succ, msg = self.notifier.issue_token(code, uri)
        if succ: messagebox.showinfo("성공", "카카오 인증 성공!"); return True
        else: messagebox.showerror("오류", msg); return False
