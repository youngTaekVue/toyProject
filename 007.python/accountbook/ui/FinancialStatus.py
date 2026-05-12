import tkinter as tk
from tkinter import ttk
from utils.FinancialUtil import FinancialUtil


class FinancialStatus(ttk.Frame):
    TREE_COLS = ("항목", "구분", "금융기관", "이전 대비 증감", "금액", "비고")

    def __init__(self, parent):
        super().__init__(parent)

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        header = ttk.Frame(self, padding=20)
        header.pack(fill=tk.X)

        title_label = ttk.Label(header, text="💰 재무 상태 현황", font=("맑은 고딕", 18, "bold"))
        title_label.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🔄 새로고침", command=self.refresh_data).pack(side=tk.LEFT, padx=5)

        self.lbl_hint = ttk.Label(
            header,
            text="",
            font=("맑은 고딕", 9),
            foreground="#666666",
        )
        self.lbl_hint.pack(side=tk.LEFT, padx=(16, 0))

        summary_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        summary_frame.pack(fill=tk.X)

        style = ttk.Style()
        style.configure("Asset.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#007bff")
        style.configure("Liability.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#dc3545")
        style.configure("Net.TLabel", font=("맑은 고딕", 16, "bold"))
        style.configure("Finance.Treeview", font=("맑은 고딕", 10), rowheight=30)
        style.configure("Finance.Treeview.Heading", font=("맑은 고딕", 10, "bold"))

        self.asset_card = ttk.LabelFrame(summary_frame, text="총 자산", padding=15)
        self.asset_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_total_assets = ttk.Label(self.asset_card, text="0 원", style="Asset.TLabel")
        self.lbl_total_assets.pack()

        self.liability_card = ttk.LabelFrame(summary_frame, text="총 부채", padding=15)
        self.liability_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_total_liabilities = ttk.Label(self.liability_card, text="0 원", style="Liability.TLabel")
        self.lbl_total_liabilities.pack()

        self.net_card = ttk.LabelFrame(summary_frame, text="순자산 (자본)", padding=15)
        self.net_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_net_worth = ttk.Label(self.net_card, text="0 원", style="Net.TLabel")
        self.lbl_net_worth.pack()

        self.list_frame = ttk.LabelFrame(self, text="재무 상세 내역 (자산 및 부채)", padding=10)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree_finance = self.create_treeview(self.list_frame)

        self.tree_finance.tag_configure("asset", foreground="#007bff")
        self.tree_finance.tag_configure("liability", foreground="#dc3545")
        self.tree_finance.tag_configure("delta_asset_up", foreground="#28a745")
        self.tree_finance.tag_configure("delta_asset_down", foreground="#dc3545")
        self.tree_finance.tag_configure("delta_liab_up", foreground="#dc3545")
        self.tree_finance.tag_configure("delta_liab_down", foreground="#28a745")

    def create_treeview(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(
            frame,
            columns=self.TREE_COLS,
            show="headings",
            selectmode="browse",
            style="Finance.Treeview",
        )

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        col_width = {
            "항목": (280, 200),
            "구분": (80, 70),
            "금융기관": (160, 120),
            "이전 대비 증감": (140, 120),
            "금액": (140, 120),
            "비고": (200, 140),
        }
        for col in self.TREE_COLS:
            tree.heading(col, text=col)
            w, mw = col_width[col]
            anchor = "e" if col in ("이전 대비 증감", "금액") else ("w" if col in ("항목", "비고") else "center")
            tree.column(col, width=w, minwidth=mw, anchor=anchor, stretch=(col == "항목" or col == "비고"))

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, columnspan=2, sticky="ew")

        return tree

    def _configure_tree_columns(self, delta_mode):
        if delta_mode:
            self.tree_finance.column("이전 대비 증감", width=130, minwidth=80)
            self.tree_finance.column("금액", width=130, minwidth=100, stretch=False)
            self.tree_finance.column("비고", width=0, minwidth=0, stretch=False)
        else:
            self.tree_finance.column("이전 대비 증감", width=0, minwidth=0, stretch=False)
            self.tree_finance.column("금액", width=140, minwidth=120)
            self.tree_finance.column("비고", width=200, minwidth=140)

    @staticmethod
    def _fmt_signed_amount(n):
        if n == 0:
            return "변동 없음"
        sign = "+" if n > 0 else ""
        return f"{sign}{n:,}"

    @staticmethod
    def _row_tag_for_delta(category, delta):
        if delta == 0:
            return ""
        cat = str(category)
        if "자산" in cat:
            return "delta_asset_up" if delta > 0 else "delta_asset_down"
        if "부채" in cat:
            return "delta_liab_up" if delta > 0 else "delta_liab_down"
        return ""

    def _note_from_row(self, row):
        if isinstance(row, dict):
            return str(row.get("note", "") or "").strip()
        if row is not None and len(row) > 4:
            return str(row[4] or "").strip()
        return ""

    def refresh_data(self):
        try:
            curr_rows, prev_rows = FinancialUtil.get_current_and_previous_financial_rows()
            rows = curr_rows if curr_rows else FinancialUtil.get_financial_data_from_db()
            delta_bundle = (
                FinancialUtil.compute_financial_delta(prev_rows, curr_rows)
                if prev_rows is not None
                else None
            )

            if prev_rows is not None and delta_bundle is not None:
                self.lbl_hint.config(
                    text="상단: 최근 저장 스냅샷 기준 금액 · 목록: 직전 스냅샷 대비 증감(현재 금액 0인 행 제외)",
                )
                self.asset_card.configure(text="총 자산")
                self.liability_card.configure(text="총 부채")
                self.net_card.configure(text="순자산 (자본)")
                self.list_frame.configure(text="재무 상세 내역 (직전 스냅샷 대비 증감 · 현재 금액)")
                self._configure_tree_columns(delta_mode=True)
                self._apply_summary_latest_snapshot(delta_bundle)
                self._fill_tree_delta(delta_bundle["line_items"])
            else:
                self.lbl_hint.config(
                    text="증감은 스냅샷이 2회 이상 쌓인 뒤 표시됩니다. 「뱅샐현황」을 담은 엑셀을 다시 업로드해 보세요.",
                )
                self.asset_card.configure(text="총 자산")
                self.liability_card.configure(text="총 부채")
                self.net_card.configure(text="순자산 (자본)")
                self.list_frame.configure(text="재무 상세 내역 (자산 및 부채)")
                self._configure_tree_columns(delta_mode=False)
                self._apply_summary_absolute(rows)
                self._fill_tree_absolute(rows)

        except Exception as e:
            print(f"데이터 로드 중 오류: {e}")

    def _apply_summary_latest_snapshot(self, bundle):
        """증감 모드에서도 상단 카드는 최근 스냅샷의 총액(절대값)만 표시합니다."""
        ca = bundle["curr_assets"]
        cl = bundle["curr_liabilities"]
        cn = bundle["curr_net"]

        self.lbl_total_assets.config(text=f"{ca:,} 원", foreground="#007bff")
        self.lbl_total_liabilities.config(text=f"{cl:,} 원", foreground="#dc3545")
        self.lbl_net_worth.config(text=f"{cn:,} 원")
        if cn >= 0:
            self.lbl_net_worth.config(foreground="#28a745")
        else:
            self.lbl_net_worth.config(foreground="#dc3545")

    def _apply_summary_absolute(self, rows):
        total_assets, total_liabilities, net_worth = FinancialUtil.calculate_financial_summary(rows)

        self.lbl_total_assets.config(text=f"{total_assets:,} 원", foreground="#007bff")
        self.lbl_total_liabilities.config(text=f"{total_liabilities:,} 원", foreground="#dc3545")
        self.lbl_net_worth.config(text=f"{net_worth:,} 원")
        if net_worth >= 0:
            self.lbl_net_worth.config(foreground="#28a745")
        else:
            self.lbl_net_worth.config(foreground="#dc3545")

    def _fill_tree_delta(self, line_items):
        self.tree_finance.delete(*self.tree_finance.get_children())
        for it in line_items:
            if it.get("curr", 0) == 0:
                continue
            cat = it["category"]
            tag = ""
            if "자산" in str(cat):
                tag = "asset"
            elif "부채" in str(cat):
                tag = "liability"
            dtag = self._row_tag_for_delta(cat, it["delta"])
            tags = tuple(t for t in (tag, dtag) if t)

            delta_txt = self._fmt_signed_amount(it["delta"])
            amt_txt = f"{it['curr']:,}"
            self.tree_finance.insert(
                "",
                tk.END,
                values=(it["itemName"], cat, it["institution"], delta_txt, amt_txt, ""),
                tags=tags,
            )

    def _fill_tree_absolute(self, rows):
        self.tree_finance.delete(*self.tree_finance.get_children())
        for row in rows:
            d = FinancialUtil._normalize_financial_row(row)
            if d["amount"] == 0:
                continue
            category = d["category"]

            tag = ""
            if "자산" in str(category):
                tag = "asset"
            elif "부채" in str(category):
                tag = "liability"

            note = self._note_from_row(row)
            self.tree_finance.insert(
                "",
                tk.END,
                values=(
                    d["itemName"],
                    category,
                    d["institution"],
                    "—",
                    f"{d['amount']:,}",
                    note,
                ),
                tags=(tag,) if tag else (),
            )
