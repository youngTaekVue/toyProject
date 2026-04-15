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
        # 상단 컨트롤 바
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="자산 및 계약 현황", font=("맑은 고딕", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(top_bar, text="새로고침", command=self.refresh_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(top_bar, text="Excel 업로드", command=self.upload_excel_data).pack(side=tk.RIGHT, padx=5)

        # 메인 탭 구성 (재무, 보험, 투자)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. 재무현황 탭
        self.tab_finance = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_finance, text="재무현황 (자산/부채)")
        self.tree_finance = self.create_treeview(self.tab_finance,
            ("항목", "구분", "금융기관", "금액", "비고"))

        # 2. 보험현황 탭
        self.tab_insurance = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_insurance, text="보험현황")
        self.tree_insurance = self.create_treeview(self.tab_insurance,
            ("보험사", "상품명", "피보험자", "보험료", "만기일", "상태"))

        # 3. 투자현황 탭
        self.tab_investment = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_investment, text="투자현황")
        self.tree_investment = self.create_treeview(self.tab_investment,
            ("종목명", "보유수량", "평균단가", "현재가", "평가손익", "수익률"))

    def create_treeview(self, parent, columns):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        # 스크롤바
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        return tree

    def refresh_data(self):
        """DB에서 데이터를 가져와 각 트리뷰를 업데이트합니다."""
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 재무현황 로드
                    cursor.execute("SELECT item_name, category, institution, amount, note FROM financial")
                    self.update_tree(self.tree_finance, cursor.fetchall())

                    # 보험현황 로드
                    cursor.execute("SELECT company, product_name, insured, premium, expiry_date, status FROM insurance")
                    self.update_tree(self.tree_insurance, cursor.fetchall())

                    # 투자현황 로드
                    cursor.execute("SELECT stock_name, quantity, avg_price, current_price, profit_loss, return_rate FROM investment")
                    self.update_tree(self.tree_investment, cursor.fetchall())
        except Exception as e:
            # 테이블이 아직 없는 경우 에러가 발생할 수 있으므로 간단히 출력만 함
            print(f"데이터 로드 중 오류 (테이블 확인 필요): {e}")

    def update_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            # 리스트나 딕셔너리 형태에 따라 처리
            values = list(row.values()) if isinstance(row, dict) else row
            
            # 금액 포맷팅 (숫자인 경우)
            formatted_values = []
            for v in values:
                if isinstance(v, (int, float)):
                    formatted_values.append(f"{v:,}")
                else:
                    formatted_values.append(v)

            tree.insert("", tk.END, values=formatted_values)

    def upload_excel_data(self):
        """뱅셀현황 엑셀 파일을 읽어 '재무현황' 데이터를 DB에 저장합니다."""
        file_path = filedialog.askopenfilename(
            title="뱅셀현황 엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )

        if not file_path:
            return

        try:
            # 엑셀 파일 읽기 (시트명: 뱅셀현황)
            # 사용자가 언급한 "뱅셀현황 시트 > 재무현황에 대한 엑셀 데이터"를 처리
            df = pd.read_excel(file_path, sheet_name='뱅셀현황')

            # 필요한 컬럼 매핑 (엑셀 컬럼명 -> DB 컬럼명)
            # 엑셀의 구조를 모르므로, 사용자가 제공한 DB 컬럼명에 맞춰 데이터를 추출하는 로직이 필요합니다.
            # 여기서는 엑셀의 컬럼명이 DB 컬럼명과 유사하다고 가정하거나, 
            # 특정 위치(index)의 데이터를 가져오는 방식으로 구현할 수 있습니다.
            
            # 예시: 엑셀 컬럼명이 '항목', '구분', '금융기관', '금액', '비고' 라고 가정
            # 만약 실제 엑셀 컬럼명이 다르다면 이 부분을 수정해야 합니다.
            required_columns = ['항목', '구분', '금융기관', '금액', '비고']
            
            # 엑셀 파일 내에 '재무현황' 섹션이 어디서 시작하는지 찾거나, 
            # 전체가 재무현황 데이터라면 그대로 사용합니다.
            # 여기서는 전체 시트 내용 중 필요한 컬럼만 추출한다고 가정합니다.
            
            # DB 연결 및 데이터 삽입
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 기존 데이터 삭제 (필요시)
                    # cursor.execute("DELETE FROM financial")

                    insert_sql = """
                        INSERT INTO financial (item_name, category, institution, amount, note, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    count = 0
                    for index, row in df.iterrows():
                        # NaN 처리 및 데이터 추출 (컬럼명은 실제 엑셀에 맞춰 조정 필요)
                        # 여기서는 df의 컬럼 순서대로 가져온다고 가정하거나 이름을 지정합니다.
                        try:
                            item_name = str(row['항목']) if pd.notna(row['항목']) else ""
                            category = str(row['구분']) if pd.notna(row['구분']) else ""
                            institution = str(row['금융기관']) if pd.notna(row['금융기관']) else ""
                            amount = int(row['금액']) if pd.notna(row['금액']) else 0
                            note = str(row['비고']) if pd.notna(row['비고']) else ""
                            updated_at = datetime.now()

                            cursor.execute(insert_sql, (item_name, category, institution, amount, note, updated_at))
                            count += 1
                        except KeyError:
                            # 엑셀 컬럼명이 일치하지 않는 경우 skip하거나 에러 처리
                            continue

                    conn.commit()
            
            messagebox.showinfo("완료", f"{count}건의 재무현황 데이터가 업로드되었습니다.")
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("오류", f"엑셀 업로드 중 오류가 발생했습니다: {e}")
