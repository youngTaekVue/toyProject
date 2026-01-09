import tkinter as tk
from tkinter import ttk

from ui.DashboardView import DashboardView
from ui.LogsView import LogsView
from ui.SettingsView import SettingsView
from ui.TreatListView import TreatListView
from ui.UserListView import UserListView

class ComplexLayoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("고급 레이아웃 예제 시스템")
        self.root.geometry("1000x700")

        style = ttk.Style()
        style.theme_use('clam')

        self.setup_main_layout()

    def setup_main_layout(self):
        # 1. PanedWindow
        self.main_pane = ttk.PanedWindow(self.root, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        # 2. Sidebar
        self.sidebar = ttk.Frame(self.main_pane, width=200, relief="sunken")
        self.main_pane.add(self.sidebar, weight=1)

        # 3. Content Area
        self.content_area = ttk.Frame(self.main_pane, relief="flat")
        self.main_pane.add(self.content_area, weight=4)

        self.create_sidebar_content()
        self.create_main_content()

    def create_sidebar_content(self):
        lbl_title = ttk.Label(self.sidebar, text="시스템 메뉴", font=("맑은 고딕", 12, "bold"))
        lbl_title.pack(pady=20)

        menus = ["대시보드", "환자번호 관리", "진료내역 조회", "시스템 설정", "로그 조회"]
        for i, menu in enumerate(menus):
            btn = ttk.Button(self.sidebar, text=menu, command=lambda idx=i: self.notebook.select(idx))
            btn.pack(fill="x", padx=10, pady=5)

        ttk.Frame(self.sidebar).pack(fill="both", expand=True)
        ttk.Label(self.sidebar, text="v1.0.0", foreground="gray").pack(side="bottom", pady=10)

    def create_main_content(self):
        self.notebook = ttk.Notebook(self.content_area)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_dashboard = DashboardView(self.notebook)
        self.notebook.add(self.tab_dashboard, text=" 대시보드 ")

        self.tab_data = UserListView(self.notebook)
        self.notebook.add(self.tab_data, text=" 환자번호 관리 ")

        self.tab_treatments = TreatListView(self.notebook)
        self.notebook.add(self.tab_treatments, text=" 진료내역 조회 ")

        self.tab_settings = SettingsView(self.notebook)
        self.notebook.add(self.tab_settings, text=" 시스템 설정 ")

        self.tab_logs = LogsView(self.notebook)
        self.notebook.add(self.tab_logs, text=" 로그 조회 ")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComplexLayoutApp(root)
    root.mainloop()