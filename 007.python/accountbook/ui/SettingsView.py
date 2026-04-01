import tkinter as tk
from tkinter import ttk, messagebox
import database

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        # 전체 레이아웃 (좌우 분할)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # --- [좌측: 입력 폼] ---
        form_frame = ttk.LabelFrame(self, text="규칙 추가/수정", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(form_frame, text="내용 키워드:").pack(anchor="w", pady=(0, 5))
        self.ent_merchant = ttk.Entry(form_frame)
        self.ent_merchant.pack(fill="x", pady=(0, 15))

        ttk.Label(form_frame, text="대분류:").pack(anchor="w", pady=(0, 5))
        self.ent_category = ttk.Entry(form_frame)
        self.ent_category.pack(fill="x", pady=(0, 15))

        ttk.Label(form_frame, text="소분류:").pack(anchor="w", pady=(0, 5))
        self.ent_sub_category = ttk.Entry(form_frame)
        self.ent_sub_category.pack(fill="x", pady=(0, 15))

        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="저장", command=self.save_rule).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(btn_frame, text="초기화", command=self.clear_form).pack(side="left", expand=True, fill="x", padx=2)

        ttk.Label(form_frame, text="※ 내용에 키워드가 포함되면\n해당 카테고리로 자동 분류됩니다.", 
                  foreground="gray", font=("맑은 고딕", 9)).pack(side="bottom", pady=10)

        # --- [우측: 규칙 목록] ---
        list_frame = ttk.LabelFrame(self, text="등록된 자동 분류 규칙", padding=10)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 트리뷰 (목록)
        cols = ("ID", "키워드", "대분류", "소분류")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("키워드", text="키워드 (내용 포함)")
        self.tree.heading("대분류", text="대분류")
        self.tree.heading("소분류", text="소분류")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("키워드", width=150)
        self.tree.column("대분류", width=100, anchor="center")
        self.tree.column("소분류", width=100, anchor="center")

        # 스크롤바
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # 하단 버튼
        bottom_btn_frame = ttk.Frame(list_frame)
        bottom_btn_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        ttk.Button(bottom_btn_frame, text="선택 삭제", command=self.delete_rule).pack(side="right", padx=5)
        ttk.Button(bottom_btn_frame, text="새로고침", command=self.load_categories).pack(side="right", padx=5)

        # 선택 시 폼에 채우기
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_categories(self):
        """DB에서 규칙 목록을 불러와 트리뷰를 갱신합니다."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, merchant, category, sub_category FROM category ORDER BY category, merchant")
                    for row in cursor.fetchall():
                        self.tree.insert("", "end", values=(row['id'], row['merchant'], row['category'], row['sub_category']))
        except Exception as e:
            print(f"Error loading categories: {e}")

    def save_rule(self):
        """입력된 내용을 DB에 저장(추가/수정)합니다."""
        merchant = self.ent_merchant.get().strip()
        category = self.ent_category.get().strip()
        sub_category = self.ent_sub_category.get().strip()

        if not merchant or not category:
            messagebox.showwarning("경고", "키워드와 대분류는 필수 입력 사항입니다.")
            return

        selected = self.tree.selection()
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if selected:
                        # 수정
                        rule_id = self.tree.item(selected[0], 'values')[0]
                        sql = "UPDATE category SET merchant=%s, category=%s, sub_category=%s WHERE id=%s"
                        cursor.execute(sql, (merchant, category, sub_category, rule_id))
                    else:
                        # 신규 추가
                        sql = "INSERT INTO category (merchant, category, sub_category) VALUES (%s, %s, %s)"
                        cursor.execute(sql, (merchant, category, sub_category))
                conn.commit()
            
            messagebox.showinfo("성공", "규칙이 저장되었습니다.")
            self.clear_form()
            self.load_categories()
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 에러 발생: {e}")

    def delete_rule(self):
        """선택된 규칙을 삭제합니다."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 항목을 선택해주세요.")
            return

        if not messagebox.askyesno("삭제 확인", "선택한 규칙을 삭제하시겠습니까?"):
            return

        try:
            rule_id = self.tree.item(selected[0], 'values')[0]
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM category WHERE id=%s", (rule_id,))
                conn.commit()
            
            self.load_categories()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("오류", f"삭제 중 에러 발생: {e}")

    def on_tree_select(self, event):
        """목록 선택 시 폼에 데이터를 채웁니다."""
        selected = self.tree.selection()
        if not selected: return
        
        values = self.tree.item(selected[0], 'values')
        self.ent_merchant.delete(0, "end")
        self.ent_merchant.insert(0, values[1])
        self.ent_category.delete(0, "end")
        self.ent_category.insert(0, values[2])
        self.ent_sub_category.delete(0, "end")
        self.ent_sub_category.insert(0, values[3])

    def clear_form(self):
        """입력 폼을 초기화합니다."""
        self.ent_merchant.delete(0, "end")
        self.ent_category.delete(0, "end")
        self.ent_sub_category.delete(0, "end")
        self.tree.selection_remove(self.tree.selection())
