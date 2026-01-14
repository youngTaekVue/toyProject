import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

        # 메뉴 이름과 뷰 클래스 매핑
        self.menu_map = {
            "대시보드": DashboardView,
            "환자번호 관리": UserListView,
            "진료내역 조회": TreatListView,
            "시스템 설정": SettingsView,
            "로그 조회": LogsView
        }

        for title, view_cls in self.menu_map.items():
            btn = ttk.Button(self.sidebar, text=title, command=lambda t=title, v=view_cls: self.add_tab(t, v))
            btn.pack(fill="x", padx=10, pady=5)

        ttk.Frame(self.sidebar).pack(fill="both", expand=True)
        ttk.Label(self.sidebar, text="v1.0.0", foreground="gray").pack(side="bottom", pady=10)

    def create_main_content(self):
        self.notebook = ttk.Notebook(self.content_area)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 탭 우클릭 시 닫기 메뉴 활성화
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

        # 탭 드래그 앤 드롭(순서 변경) 활성화
        self.notebook.bind("<Button-1>", self.on_tab_drag_start)
        self.notebook.bind("<B1-Motion>", self.on_tab_drag_motion)
        self.notebook.bind("<ButtonRelease-1>", self.on_tab_drag_release)

        # 초기 화면으로 대시보드 열기
        self.add_tab("대시보드", DashboardView)

    def add_tab(self, title, view_cls):
        # 1. 이미 열려있는 탭인지 확인 (텍스트로 비교)
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text").strip() == title:
                self.notebook.select(tab)
                return

        # 2. 탭 개수 제한 확인 (최대 5개)
        if len(self.notebook.tabs()) >= 5:
            messagebox.showwarning("탭 제한", "탭은 최대 5개까지만 열 수 있습니다.\n기존 탭을 우클릭하여 닫고 다시 시도해주세요.")
            return

        # 3. 새 탭 생성 및 추가
        new_view = view_cls(self.notebook)
        self.notebook.add(new_view, text=f" {title} ")
        self.notebook.select(new_view)

    def on_tab_drag_start(self, event):
        """탭 드래그 시작"""
        try:
            # 클릭한 위치가 탭 영역(label)인지 확인
            if "label" in self.notebook.identify(event.x, event.y):
                index = self.notebook.index(f"@{event.x},{event.y}")
                self.drag_data = {"index": index}
            else:
                self.drag_data = None
        except tk.TclError:
            self.drag_data = None

    def on_tab_drag_motion(self, event):
        """탭 드래그 중 순서 변경"""
        if not getattr(self, "drag_data", None):
            return

        try:
            # 마우스 위치의 탭 인덱스 확인
            target_index = self.notebook.index(f"@{event.x},{event.y}")
            source_index = self.drag_data["index"]

            # 위치가 달라졌으면 탭 이동
            if target_index != source_index:
                tab_id = self.notebook.tabs()[source_index]
                self.notebook.insert(target_index, tab_id)
                self.drag_data["index"] = target_index
        except tk.TclError:
            pass

    def on_tab_drag_release(self, event):
        """드래그 종료"""
        self.drag_data = None

    def on_tab_right_click(self, event):
        """탭 우클릭 시 닫기 메뉴 표시"""
        try:
            # 클릭한 위치의 탭 인덱스 찾기
            index = self.notebook.index(f"@{event.x},{event.y}")
            
            # 팝업 메뉴 생성
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="닫기", command=lambda: self.notebook.forget(index))
            menu.post(event.x_root, event.y_root)
        except tk.TclError:
            # 탭이 아닌 영역을 클릭했을 때는 무시
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ComplexLayoutApp(root)
    root.mainloop()