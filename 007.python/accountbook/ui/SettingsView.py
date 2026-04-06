import tkinter as tk
from tkinter import ttk, messagebox
import database
import os
from dotenv import load_dotenv

class SettingsView(ttk.Frame):
    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app # 메인 애플리케이션 인스턴스 참조

        # 탭 컨트롤 생성
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 탭 1: 자동 분류 규칙 설정
        self.category_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.category_tab, text="자동 분류 규칙")
        self.setup_category_ui()

        # 탭 2: 시스템 환경 설정
        self.system_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.system_tab, text="시스템 환경 설정")
        self.setup_system_ui()

        self.load_categories()
        self.load_system_settings()

    def setup_category_ui(self):
        # (기존 코드와 동일)
        self.category_tab.columnconfigure(0, weight=1)
        self.category_tab.columnconfigure(1, weight=3)
        self.category_tab.rowconfigure(0, weight=1)

        form_frame = ttk.LabelFrame(self.category_tab, text="규칙 추가/수정", padding=15)
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

        list_frame = ttk.LabelFrame(self.category_tab, text="등록된 자동 분류 규칙", padding=10)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        cols = ("ID", "키워드", "대분류", "소분류")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.column("ID", width=50, anchor="center")
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        bottom_btn_frame = ttk.Frame(list_frame)
        bottom_btn_frame.pack(side="bottom", fill="x", pady=(10, 0))
        ttk.Button(bottom_btn_frame, text="선택 삭제", command=self.delete_rule).pack(side="right", padx=5)
        ttk.Button(bottom_btn_frame, text="새로고침", command=self.load_categories).pack(side="right", padx=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def setup_system_ui(self):
        container = ttk.Frame(self.system_tab, padding=20)
        container.pack(fill="both", expand=True)

        app_frame = ttk.LabelFrame(container, text="애플리케이션 기본 설정", padding=15)
        app_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(app_frame, text="사용자 이름:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_username = ttk.Entry(app_frame)
        self.ent_username.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        ttk.Label(app_frame, text="폰트 크기:").grid(row=1, column=0, sticky="w", pady=5)
        self.font_size_var = tk.StringVar()
        self.font_size_combo = ttk.Combobox(app_frame, textvariable=self.font_size_var,
                                            values=["9", "10", "11", "12", "14", "16"], state="readonly")
        self.font_size_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        ttk.Label(app_frame, text="테마:").grid(row=2, column=0, sticky="w", pady=5)
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(app_frame, textvariable=self.theme_var,
                                        values=["clam", "alt", "default", "classic"], state="readonly")
        self.theme_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        app_frame.columnconfigure(1, weight=1)

        btn_save_sys = ttk.Button(container, text="설정 즉시 적용 및 저장", command=self.save_system_settings)
        btn_save_sys.pack(pady=20, side="bottom", anchor="e")

    def load_system_settings(self):
        load_dotenv(override=True)
        self.ent_username.insert(0, os.getenv("APP_USER_NAME", "User"))
        self.font_size_var.set(os.getenv("APP_FONT_SIZE", "10"))


    def save_system_settings(self):
        try:
            env_path = ".env"
            current_env_vars = {}
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            current_env_vars[key] = value

            current_env_vars["APP_USER_NAME"] = self.ent_username.get()
            current_env_vars["APP_FONT_SIZE"] = self.font_size_var.get()


            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in current_env_vars.items():
                    f.write(f"{key}={value}\n")
            
            # 메인 앱의 갱신 메서드 호출 (실시간 적용)
            if self.main_app:
                self.main_app.update_settings()
                messagebox.showinfo("성공", "설정이 즉시 적용되었습니다.")
            else:
                messagebox.showinfo("성공", "설정이 저장되었습니다. 적용을 위해 재시작이 필요할 수 있습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 에러 발생: {e}")

    def load_categories(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, merchant, category, sub_category FROM category ORDER BY category, merchant")
                    for row in cursor.fetchall():
                        self.tree.insert("", "end", values=(row['id'], row['merchant'], row['category'], row['sub_category']))
        except Exception as e: print(f"Error: {e}")

    def save_rule(self):
        merchant, category, sub_category = self.ent_merchant.get().strip(), self.ent_category.get().strip(), self.ent_sub_category.get().strip()
        if not merchant or not category: return
        selected = self.tree.selection()
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if selected:
                        rule_id = self.tree.item(selected[0], 'values')[0]
                        cursor.execute("UPDATE category SET merchant=%s, category=%s, sub_category=%s WHERE id=%s", (merchant, category, sub_category, rule_id))
                    else:
                        cursor.execute("INSERT INTO category (merchant, category, sub_category) VALUES (%s, %s, %s)", (merchant, category, sub_category))
                conn.commit()
            self.clear_form(); self.load_categories()
        except Exception as e: messagebox.showerror("오류", str(e))

    def delete_rule(self):
        selected = self.tree.selection()
        if not selected: return
        try:
            rule_id = self.tree.item(selected[0], 'values')[0]
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor: cursor.execute("DELETE FROM category WHERE id=%s", (rule_id,))
                conn.commit()
            self.load_categories(); self.clear_form()
        except Exception as e: messagebox.showerror("오류", str(e))

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0], 'values')
        self.ent_merchant.delete(0, "end"); self.ent_merchant.insert(0, values[1])
        self.ent_category.delete(0, "end"); self.ent_category.insert(0, values[2])
        self.ent_sub_category.delete(0, "end"); self.ent_sub_category.insert(0, values[3])

    def clear_form(self):
        self.ent_merchant.delete(0, "end"); self.ent_category.delete(0, "end"); self.ent_sub_category.delete(0, "end")
        self.tree.selection_remove(self.tree.selection())
