import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from utils.FinancialUtil import FinancialUtil

class FinancialStatus(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setup_ui()
        # 초기 데이터 로드
        self.refresh_data()

    def setup_ui(self):
        # 상단 타이틀 및 컨트롤 바
        header = ttk.Frame(self, padding=20)
        header.pack(fill=tk.X)

        title_label = ttk.Label(header, text="💰 재무 상태 현황", font=("맑은 고딕", 18, "bold"))
        title_label.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🔄 새로고침", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        # 엑셀 업로드 버튼 제거
        # ttk.Button(btn_frame, text="📊 Excel 업로드", command=self.upload_excel_data).pack(side=tk.LEFT, padx=5)

        # 요약 정보 카드 섹션
        summary_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        summary_frame.pack(fill=tk.X)

        # 스타일 설정
        style = ttk.Style()
        style.configure("Asset.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#007bff") # Blue
        style.configure("Liability.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#dc3545") # Red
        style.configure("Net.TLabel", font=("맑은 고딕", 16, "bold"))
        # 트리뷰 가독성 개선 (행 높이/폰트/헤더 폰트)
        style.configure("Finance.Treeview", font=("맑은 고딕", 10), rowheight=30) # Changed rowheight from 26 to 30
        style.configure("Finance.Treeview.Heading", font=("맑은 고딕", 10, "bold"))

        # 자산 요약
        asset_card = ttk.LabelFrame(summary_frame, text="총 자산", padding=15)
        asset_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_total_assets = ttk.Label(asset_card, text="0 원", style="Asset.TLabel")
        self.lbl_total_assets.pack()

        # 부채 요약
        liability_card = ttk.LabelFrame(summary_frame, text="총 부채", padding=15)
        liability_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_total_liabilities = ttk.Label(liability_card, text="0 원", style="Liability.TLabel")
        self.lbl_total_liabilities.pack()

        # 순자산 요약
        net_card = ttk.LabelFrame(summary_frame, text="순자산 (자본)", padding=15)
        net_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_net_worth = ttk.Label(net_card, text="0 원", style="Net.TLabel")
        self.lbl_net_worth.pack()

        # 상세 내역 트리뷰 섹션
        list_frame = ttk.LabelFrame(self, text="재무 상세 내역 (자산 및 부채)", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree_finance = self.create_treeview(list_frame,
            ("항목", "구분", "금융기관", "금액", "비고"))
        
        # 트리뷰 태그 설정 (색상 구분)
        self.tree_finance.tag_configure("asset", foreground="#007bff")
        self.tree_finance.tag_configure("liability", foreground="#dc3545")

    def create_treeview(self, parent, columns):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse", style="Finance.Treeview")

        # 스크롤바
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in columns:
            tree.heading(col, text=col)
            # 컬럼 폭/정렬 재조정 (깨져보이는 느낌 완화)
            if col == "항목":
                tree.column(col, width=280, minwidth=200, anchor="w", stretch=True)
            elif col == "구분":
                tree.column(col, width=80, minwidth=70, anchor="center", stretch=False)
            elif col == "금융기관":
                tree.column(col, width=160, minwidth=120, anchor="center", stretch=False)
            elif col == "금액":
                tree.column(col, width=140, minwidth=120, anchor="e", stretch=False)
            elif col == "비고":
                tree.column(col, width=200, minwidth=140, anchor="w", stretch=True)
            else:
                tree.column(col, width=120, anchor="center")

        # pack 대신 grid로 스크롤바/트리 배치 안정화
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, columnspan=2, sticky="ew")

        return tree

    def refresh_data(self):
        """DB에서 데이터를 가져와 재무현황을 업데이트합니다."""
        try:
            rows = FinancialUtil.get_financial_data_from_db()
            self.update_finance_tree(rows)
            self.calculate_summary(rows)

        except Exception as e:
            print(f"데이터 로드 중 오류: {e}")

    def update_finance_tree(self, rows):
        """트리뷰에 데이터를 채우고 자산/부채에 따라 색상을 입힙니다."""
        self.tree_finance.delete(*self.tree_finance.get_children())
        for row in rows:
            values = list(row.values()) if isinstance(row, dict) else row
            
            # 카테고리(구분) 추출
            category = row.get('category', '') if isinstance(row, dict) else row[1]
            
            # 태그 지정
            tag = ""
            if "자산" in str(category):
                tag = "asset"
            elif "부채" in str(category):
                tag = "liability"

            # 금액 포맷팅 및 값 리스트 구성
            formatted_values = []
            for i, v in enumerate(values):
                if isinstance(v, (int, float)):
                    formatted_values.append(f"{v:,}")
                else:
                    formatted_values.append(v)

            self.tree_finance.insert("", tk.END, values=formatted_values, tags=(tag,))

    def calculate_summary(self, rows):
        """총 자산, 총 부채, 순자산을 계산하여 화면에 표시합니다."""
        total_assets, total_liabilities, net_worth = FinancialUtil.calculate_financial_summary(rows)
        
        self.lbl_total_assets.config(text=f"{total_assets:,} 원")
        self.lbl_total_liabilities.config(text=f"{total_liabilities:,} 원")
        self.lbl_net_worth.config(text=f"{net_worth:,} 원")
        
        # 순자산 색상 처리
        if net_worth >= 0:
            self.lbl_net_worth.config(foreground="#28a745") # Green
        else:
            self.lbl_net_worth.config(foreground="#dc3545") # Red

    # upload_excel_data 함수 제거
    # def upload_excel_data(self):
    #     """뱅샐현황 엑셀 파일을 읽어 '재무현황' 데이터를 DB에 저장합니다."""
    #     file_path = filedialog.askopenfilename(
    #         title="뱅샐현황 엑셀 파일 선택",
    #         filetypes=[("Excel files", "*.xlsx *.xls")]
    #     )

    #     if not file_path:
    #         return

    #     try:
    #         # 템플릿(좌:자산/우:부채) 형태는 컬럼이 정리되어 있지 않아서 header=None으로 원본 형태를 유지
    #         df_raw = pd.read_excel(file_path, sheet_name='뱅샐현황', header=None)
    #         rows = FinancialUtil.parse_financial_status_table(df_raw)
    #         count = FinancialUtil.save_financial_rows(rows, truncate=True)
            
    #         messagebox.showinfo("완료", f"{count}건의 재무현황 데이터가 업로드되었습니다.")
    #         self.refresh_data()

    #     except Exception as e:
    #         messagebox.showerror("오류", f"엑셀 업로드 중 오류가 발생했습니다: {e}")
