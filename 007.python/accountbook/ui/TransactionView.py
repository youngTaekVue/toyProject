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

        self.style = ttk.Style()
        self.style.configure("Big.TLabel", font=("맑은 고딕", 20, "bold"))
        self.style.configure("Mid.TLabel", font=("맑은 고딕", 12))

        self.setup_ui()
        self.load_data_from_db()

    def setup_ui(self):
        # 1. 상단 바 (인스턴스 변수로 저장)
        self.top_bar = ttk.Frame(self, padding=10)
        self.top_bar.pack(fill=tk.X)

        ttk.Button(self.top_bar, text="엑셀 통합 업로드", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_bar, text="나에게 공유", command=self.share_to_kakao).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_bar, text="친구에게 공유", command=self.share_to_friend).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.top_bar, text="조회 월:").pack(side=tk.LEFT, padx=(30, 5))
        self.shared_month_var = tk.StringVar()
        self.cb_shared_month = ttk.Combobox(self.top_bar, textvariable=self.shared_month_var, width=12, state="readonly")
        self.cb_shared_month.pack(side=tk.LEFT, padx=5)
        self.cb_shared_month.bind("<<ComboboxSelected>>", self.on_month_change)

        # 2. 메인 영역
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=2)

        # --- [카드 1] 차트 영역 (인스턴스 변수로 저장) ---
        self.card_chart = ttk.LabelFrame(self.main_frame, text="지출 현황 상세")
        self.card_chart.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        chart_ctrl = ttk.Frame(self.card_chart); chart_ctrl.pack(fill=tk.X, padx=5, pady=2)
        self.btn_chart_back = ttk.Button(chart_ctrl, text="← 전체 보기", command=self.reset_chart_view, state=tk.DISABLED)
        self.btn_chart_back.pack(side=tk.LEFT)
        self.lbl_chart_title = ttk.Label(chart_ctrl, text="월간 카테고리별 지출", font=("맑은 고딕", 10, "bold"))
        self.lbl_chart_title.pack(side=tk.LEFT, padx=10)

        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.card_chart)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)

        # --- [카드 2] 요약 정보 ---
        self.card_summary = ttk.LabelFrame(self.main_frame, text="이달의 요약")
        self.card_summary.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        inner = ttk.Frame(self.card_summary); inner.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        ttk.Label(inner, text="총 수입", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_income = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#2196F3"); self.lbl_income.pack(anchor="w", pady=(0, 15))
        ttk.Label(inner, text="총 지출", style="Mid.TLabel", foreground="#888888").pack(anchor="w")
        self.lbl_expense = ttk.Label(inner, text="***,*** 원", style="Big.TLabel", foreground="#F44336"); self.lbl_expense.pack(anchor="w")

        # --- [카드 3] 리스트 내역 ---
        self.card_list = ttk.LabelFrame(self.main_frame)
        self.card_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.notebook = ttk.Notebook(self.card_list); self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tab_main = ttk.Frame(self.notebook); self.notebook.add(self.tab_main, text="가계부 내역")
        self.tab_dup = ttk.Frame(self.notebook); self.notebook.add(self.tab_dup, text="중복 의심 내역")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.setup_main_tab_ui(); self.setup_dup_tab_ui()

    def share_to_friend(self):
        """카카오톡 친구 목록을 가져와서 선택한 친구에게 전송합니다."""
        logger.log("INFO", "UI_Action", "친구에게 공유 버튼 클릭")
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
                logger.log("INFO", "KakaoShare", f"친구({nickname})에게 리포트 전송 성공")
                messagebox.showinfo("성공", f"{nickname}님에게 리포트를 보냈습니다.")
                win.destroy()
            else:
                logger.log("ERROR", "KakaoShare", f"친구 전송 실패: {err}")
                messagebox.showerror("실패", f"전송 실패: {err}")

        ttk.Button(win, text="전송", command=do_send).pack(pady=10)

    def share_to_kakao(self):
        """나에게 공유하기"""
        logger.log("INFO", "UI_Action", "나에게 공유 버튼 클릭")
        if self.df is None or self.df.empty:
            messagebox.showwarning("경고", "공유할 데이터가 없습니다.")
            return

        cur_m = self.shared_month_var.get()
        m_df = self.df[self.df["월"] == cur_m]
        inc, exp, cat_s = self.dashboard_util.get_summary_data(m_df)

        txt = (
            f"[{cur_m} 가계부 요약]\n"
            f"💰 총 수입: {inc:,}원\n"
            f"💸 총 지출: {exp:,}원\n"
            "--------------------\n"
            "[카테고리별 지출]\n"
        )
        if not cat_s:
            txt += "• 지출 내역 없음\n"
        else:
            for c, a in cat_s.items():
                txt += f"• {c}: {a:,}원\n"

        # 차트 이미지는 로컬 파일 첨부가 불가하므로 "공개 URL"이 있을 때만 카카오로 이미지 전송 가능
        export_dir = os.path.join(os.getcwd(), "exports", "kakao")
        os.makedirs(export_dir, exist_ok=True)

        # 캡처 저장 전, 기존 이미지 전부 삭제
        try:
            for name in os.listdir(export_dir):
                p = os.path.join(export_dir, name)
                if os.path.isfile(p):
                    os.remove(p)
        except Exception:
            traceback.print_exc()

        ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        paths = []

        # 1) 지출현황 상세(현재 화면 차트)
        p_main = os.path.join(export_dir, f"{ts}_지출현황_상세.png")
        try:
            self.fig.savefig(p_main, dpi=150, bbox_inches="tight")
            paths.append(p_main)
        except Exception:
            traceback.print_exc()

        public_base = os.getenv("KAKAO_PUBLIC_IMAGE_BASE_URL", "").strip().rstrip("/")
        image_urls = []
        if public_base and paths:
            image_urls = [f"{public_base}/{os.path.basename(p)}" for p in paths]

        if image_urls:
            succ, err = self.notifier.send_report_with_images(
                title=f"{cur_m} 지출 도표",
                description=txt,
                image_urls=image_urls,
            )
        else:
            succ, err = self.notifier.send_report(txt)

        if succ:
            logger.log("INFO", "KakaoShare", "나에게 보내기 성공")
            if image_urls:
                messagebox.showinfo("성공", f"카카오톡 전송 완료!\n(차트 이미지 {len(image_urls)}장 포함)")
            else:
                messagebox.showinfo("성공", "카카오톡 전송 완료!")
        else:
            logger.log("ERROR", "KakaoShare", f"나에게 보내기 실패: {err}")
            messagebox.showerror("실패", f"사유: {err}")

    # --- 차트 및 데이터 로드 로직 ---
    def update_dashboard_chart(self):
        self.ax.clear() # 항상 차트 내용 초기화
        self.ax.axis('off') # 기본적으로 축을 끈 상태로 시작

        if self.df is None or self.df.empty:
            self.ax.text(0.5, 0.5, '데이터가 없습니다', ha='center', va='center', fontsize=12, color='gray')
            self.canvas.draw()
            return

        selected_month = self.shared_month_var.get()
        m_df = self.df[self.df['월'] == selected_month]

        if m_df.empty:
            msg = f"{selected_month}월 데이터가 없습니다" if selected_month else "조회할 월을 선택하세요"
            self.ax.text(0.5, 0.5, msg, ha='center', va='center', fontsize=12, color='gray')
            self.canvas.draw()
            return

        if self.current_chart_category is None:
            _, _, data_dict = self.dashboard_util.get_summary_data(m_df)
        else:
            data_dict = self.dashboard_util.get_sub_category_summary(m_df, self.current_chart_category)

        if not data_dict:
            self.ax.text(0.5, 0.5, '내역 없음', ha='center', va='center', fontsize=12, color='gray')
            self.canvas.draw()
            return
        else:
            self.ax.axis('on')
            self.labels_in_chart = list(data_dict.keys())
            values = list(data_dict.values())
            total = sum(values)
            legend_labels = [
                f"{label} ({(val / total * 100.0):.1f}% / {val:,.0f}원)" if total else f"{label} (0.0% / {val:,.0f}원)"
                for label, val in zip(self.labels_in_chart, values)
            ]
            self.wedges, texts, autotexts = self.ax.pie(
                values,
                autopct='%1.1f%%',
                startangle=90,
                counterclock=False,
                wedgeprops={'width': 0.4, 'edgecolor': 'w'},
                pctdistance=0.75
            )
            self.ax.legend(self.wedges, legend_labels, title="지출 항목 (% / 금액)", loc="upper left", bbox_to_anchor=(1, 1), fontsize=8, frameon=False)
            plt.setp(autotexts, size=8, weight="bold", color="black")
            self.fig.subplots_adjust(left=0.05, right=0.65, top=0.9, bottom=0.1)
            self.canvas.draw()

    def reset_chart_view(self):
        logger.log("INFO", "UI_Action", "차트 전체 보기(초기화) 클릭")
        self.current_chart_category = None; self.btn_chart_back.config(state=tk.DISABLED); self.lbl_chart_title.config(text="월간 카테고리별 지출")
        self.cat_var.set("전체"); self.update_main_tab(); self.update_dashboard_chart()

    def on_chart_click(self, event):
        if event.inaxes != self.ax or not hasattr(self, 'wedges'): return
        for i, wedge in enumerate(self.wedges):
            if wedge.contains_point([event.x, event.y]):
                selected = self.labels_in_chart[i]
                if self.current_chart_category is None:
                    logger.log("INFO", "UI_Action", f"차트 카테고리 클릭: {selected}")
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

            if not res:
                self.df = pd.DataFrame()
                self.update_filter_options()
                self.on_month_change(None)
                return

            self.df = pd.DataFrame(res)
            self.df.rename(columns={'transaction_date': 'DT', 'transaction_type': '타입', 'description': '내용', 'amount': '금액', 'payment_method': '결제수단'}, inplace=True)
            self.df['DT'] = pd.to_datetime(self.df['DT'])
            self.df['일시'] = self.df['DT'].dt.strftime('%Y-%m-%d %H:%M'); self.df['월'] = self.df['DT'].dt.strftime('%Y-%m')

            classified_data = self.df.apply(lambda r: self.dashboard_util.auto_classify(r), axis=1)
            self.df['대분류'] = classified_data['대분류']
            self.df['소분류'] = classified_data['소분류']
            self.df['타입'] = classified_data['타입']

            self.df['abs_amt'] = self.df['금액'].abs()
            cancel_key_base = ['내용', 'abs_amt']
            cancel_key_strict = [self.df['DT'].dt.date] + cancel_key_base
            is_cancel_strict = self.df.groupby(cancel_key_strict)['금액'].transform('sum') == 0
            self.df['is_cancel'] = is_cancel_strict
            self.df['is_pre_auth'] = self.df['내용'].str.contains('선승인|가결제', na=False)
            
            is_dup_uploaded = self.df.duplicated(subset=['DT', '타입', '내용', '금액'], keep="first")
            self.df['is_double_count'] = self.df['내용'].str.contains('우리카드결제대금', na=False) | is_dup_uploaded

            self.update_filter_options(); self.on_month_change(None)
        except Exception: traceback.print_exc(); self.df = pd.DataFrame(); self.on_month_change(None)

    def update_summary_card(self):
        if self.df is None or self.df.empty:
            self.lbl_income.config(text="0 원"); self.lbl_expense.config(text="0 원")
            return

        cur_m = self.shared_month_var.get()
        m_df = self.df[self.df['월'] == cur_m]
        inc, exp, _ = self.dashboard_util.get_summary_data(m_df)
        self.lbl_income.config(text=f"{inc:,} 원")
        self.lbl_expense.config(text=f"{exp:,} 원")

    def on_month_change(self, event):
        selected = self.shared_month_var.get()
        logger.log("INFO", "UI_Action", f"조회 월 변경: {selected}")
        self.update_dashboard_chart()
        self.update_summary_card()
        self.on_tab_change(None)

    def on_tab_change(self, event):
        try:
            idx = self.notebook.index('current')
            if idx == 0: self.update_main_tab()
            else: self.update_dup_tab()
        except Exception: pass

    def update_main_tab(self):
        if self.df is None or self.df.empty:
            self.summary_label.config(text="데이터가 없습니다")
            self.filtered_summary_label.config(text="")
            self.tree_main.delete(*self.tree_main.get_children())
            return

        cur_m = self.shared_month_var.get(); m_df = self.df[self.df['월'] == cur_m]
        inc, exp, _ = self.dashboard_util.get_summary_data(m_df)
        self.summary_label.config(text=f"[{cur_m}] 실질 수입: {inc:,}원 | 실질 지출: {exp:,}원")

        f_df = m_df.copy()
        selected_type = self.type_var.get()
        selected_cat = self.cat_var.get()
        
        if selected_type != "전체": f_df = f_df[f_df['타입'] == selected_type]
        if selected_cat != "전체": f_df = f_df[f_df['대분류'] == selected_cat]

        f_inc, f_exp, _ = self.dashboard_util.get_summary_data(f_df)
        summary_text = f"조회된 내역: {len(f_df)}건"
        if selected_type == "수입": summary_text += f" | 실질 수입 합계: {f_inc:,}원"
        elif selected_type == "지출": summary_text += f" | 실질 지출 합계: {f_exp:,}원"
        else: summary_text += f" | 실질 수입: {f_inc:,}원 | 실질 지출: {f_exp:,}원"

        self.filtered_summary_label.config(text=summary_text)
        self.insert_data_to_tree(self.tree_main, f_df.sort_values(by=['DT', '내용']))

    def update_dup_tab(self):
        if self.df is None or self.df.empty:
            self.tree_dup.delete(*self.tree_dup.get_children())
            return
        mask = self.df.duplicated(subset=['DT', '금액', '내용', '타입'], keep=False)
        self.insert_data_to_tree(self.tree_dup, self.df[mask].sort_values(by=['DT', '내용']))

    def setup_main_tab_ui(self):
        self.summary_label = ttk.Label(self.tab_main, text="", font=("Malgun Gothic", 11, "bold")); self.summary_label.pack(pady=5, fill=tk.X, padx=10)
        filter_frame = ttk.LabelFrame(self.tab_main,  padding=5); filter_frame.pack(fill=tk.X, padx=10, pady=5)
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
        if self.df is None or self.df.empty:
            self.cb_shared_month['values'] = []
            self.shared_month_var.set("")
            self.cb_c['values'] = ["전체"]
            return
        months = sorted(self.df['월'].unique().tolist(), reverse=True)
        self.cb_shared_month['values'] = months
        if months and not self.shared_month_var.get():
            self.shared_month_var.set(months[0])
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

    def upload_file(self):
        logger.log("INFO", "UI_Action", "엑셀 통합 업로드 버튼 클릭")
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if not path: return
        try:
            excel_data = pd.read_excel(path, sheet_name=None, header=None)
            sheet_names = list(excel_data.keys())
            def get_sheet(kw): return next((s for s in sheet_names if kw in str(s).strip()), None)
            
            bs_sheet = get_sheet("뱅샐현황")
            if bs_sheet:
                full_df = excel_data[bs_sheet]
                assets = FinancialUtil.extract_section(full_df, "자산", 1, 4)
                debts = FinancialUtil.extract_section(full_df, "부채", 5, 7)
                FinancialUtil.save_financial_data([(assets, "자산"), (debts, "부채")])
                ins = FinancialUtil.extract_section(full_df, "보험현황")
                FinancialUtil.save_insurance_data(ins)
                inv = FinancialUtil.extract_section(full_df, "투자현황")
                FinancialUtil.save_investment_data(inv)

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
                            if not desc or pd.isna(row['DT']): continue
                            if (row['DT'].strftime('%Y-%m-%d %H:%M:%S'), int(row['금액']), desc, row['타입']) not in existing:
                                new_recs.append((row['DT'], row['타입'], desc, row['금액'], row.get('결제수단', '')))
                        if new_recs:
                            cursor.executemany("INSERT INTO transactions (transaction_date, transaction_type, description, amount, payment_method) VALUES (%s, %s, %s, %s, %s)", new_recs)
                            conn.commit()
                            logger.log("INFO", "TransactionDB", f"가계부 내역 {len(new_recs)}건 저장 완료")
            
            logger.log("INFO", "FileUpload", f"엑셀 파일 업로드 성공: {os.path.basename(path)}")
            self.load_data_from_db()
            messagebox.showinfo("완료", "데이터 업로드 및 DB 저장이 완료되었습니다.")
        except Exception as e:
            logger.log("ERROR", "FileUpload", f"업로드 실패: {str(e)}")
            traceback.print_exc(); messagebox.showerror("오류", str(e))

    def authenticate_kakao(self):
        logger.log("INFO", "UI_Action", "카카오 인증 시작")
        uri = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:5000")
        if not self.rest_api_key: return False
        webbrowser.open(f"https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={uri}&response_type=code")
        code = simpledialog.askstring("카카오 인증", "로그인 후 브라우저 주소창의 'code=' 뒷부분을 복사해서 입력하세요:")
        if not code: return False
        succ, msg = self.notifier.issue_token(code, uri)
        if succ: 
            logger.log("INFO", "KakaoAuth", "카카오 계정 인증 성공")
            messagebox.showinfo("성공", "카카오 인증 성공!"); return True
        else: 
            logger.log("ERROR", "KakaoAuth", f"카카오 인증 실패: {msg}")
            messagebox.showerror("오류", msg); return False
