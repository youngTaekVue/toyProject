import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import database
from datetime import datetime

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
        ttk.Button(btn_frame, text="📊 Excel 업로드", command=self.upload_excel_data).pack(side=tk.LEFT, padx=5)

        # 요약 정보 카드 섹션
        summary_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        summary_frame.pack(fill=tk.X)

        # 스타일 설정
        style = ttk.Style()
        style.configure("Asset.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#007bff") # Blue
        style.configure("Liability.TLabel", font=("맑은 고딕", 14, "bold"), foreground="#dc3545") # Red
        style.configure("Net.TLabel", font=("맑은 고딕", 16, "bold"))

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

        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")

        # 스크롤바
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in columns:
            tree.heading(col, text=col)
            # 금액 컬럼은 우측 정렬
            if col == "금액":
                tree.column(col, width=150, anchor="e")
            else:
                tree.column(col, width=120, anchor="center")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        return tree

    def refresh_data(self):
        """DB에서 데이터를 가져와 재무현황을 업데이트합니다."""
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 재무현황 로드 (보험/투자는 요청에 따라 제거)
                    # DB 테이블의 실제 컬럼명 확인 필요 (기존 코드 참고: itemName or item_name)
                    # 여기서는 기존 코드에 있던 itemName을 유지하되, 만약 오류 시 item_name 시도 가능
                    try:
                        cursor.execute("SELECT itemName, category, institution, amount, note FROM financial")
                    except:
                        cursor.execute("SELECT item_name as itemName, category, institution, amount, note FROM financial")
                    
                    rows = cursor.fetchall()
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
        total_assets = 0
        total_liabilities = 0
        
        for row in rows:
            category = str(row.get('category', '')) if isinstance(row, dict) else str(row[1])
            amount = row.get('amount', 0) if isinstance(row, dict) else row[3]
            
            try:
                amt_val = int(amount)
            except:
                amt_val = 0

            if "자산" in category:
                total_assets += amt_val
            elif "부채" in category:
                total_liabilities += amt_val
        
        net_worth = total_assets - total_liabilities
        
        self.lbl_total_assets.config(text=f"{total_assets:,} 원")
        self.lbl_total_liabilities.config(text=f"{total_liabilities:,} 원")
        self.lbl_net_worth.config(text=f"{net_worth:,} 원")
        
        # 순자산 색상 처리
        if net_worth >= 0:
            self.lbl_net_worth.config(foreground="#28a745") # Green
        else:
            self.lbl_net_worth.config(foreground="#dc3545") # Red

    def upload_excel_data(self):
        """뱅셀현황 엑셀 파일을 읽어 '재무현황' 데이터를 DB에 저장합니다."""
        file_path = filedialog.askopenfilename(
            title="뱅셀현황 엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )

        if not file_path:
            return

        try:
            df = pd.read_excel(file_path, sheet_name='뱅셀현황')

            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 기존 로직 유지 (필요 시 DELETE 추가 가능)
                    insert_sql = """
                        INSERT INTO financial (item_name, category, institution, amount, note, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    count = 0
                    for index, row in df.iterrows():
                        try:
                            # 엑셀 컬럼명은 사용자 환경에 맞춰 '항목', '구분', '금융기관', '금액', '비고'로 가정
                            item_name = str(row['항목']) if pd.notna(row['항목']) else ""
                            category = str(row['구분']) if pd.notna(row['구분']) else ""
                            institution = str(row['금융기관']) if pd.notna(row['금융기관']) else ""
                            amount = int(row['금액']) if pd.notna(row['금액']) else 0
                            note = str(row['비고']) if pd.notna(row['비고']) else ""
                            updated_at = datetime.now()

                            cursor.execute(insert_sql, (item_name, category, institution, amount, note, updated_at))
                            count += 1
                        except Exception:
                            continue

                    conn.commit()
            
            messagebox.showinfo("완료", f"{count}건의 재무현황 데이터가 업로드되었습니다.")
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("오류", f"엑셀 업로드 중 오류가 발생했습니다: {e}")
