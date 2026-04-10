import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ui.DashboardView import DashboardView
from ui.TransactionView import TransactionView
from ui.LogsView import LogsView
from ui.SettingsView import SettingsView
from ui.FinancialStatus import FinancialStatus
from ui.SpendingManagement import SpendingManagement

class ComplexLayoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("시스템")
        self.root.geometry("1200x800")

        # 1. 스타일 초기화 (위젯 생성 전 필수 수행)
        load_dotenv(override=True)
        initial_theme = os.getenv("APP_THEME", "flatly")
        # Style 객체 생성 시 마스터 창(root)을 연결합니다.
        self.style = tb.Style(theme=initial_theme)
        
        # 2. 메인 레이아웃 구성
        self.setup_main_layout()
        
        # 3. 초기 시각 설정 적용 (폰트 등)
        self.apply_visual_settings()

    def apply_visual_settings(self):
        """환경 변수에서 설정을 읽어와 폰트를 적용합니다."""
        load_dotenv(override=True)
        font_size_str = os.getenv("APP_FONT_SIZE", "11")
        try:
            font_size = int(font_size_str)
        except ValueError:
            font_size = 11
        
        # 전역 폰트 설정
        self.style.configure(".", font=("맑은 고딕", font_size))
        self.style.configure("Treeview.Heading", font=("맑은 고딕", font_size, "bold"))

    def update_settings(self):
        """설정 변경 시 호출되어 UI를 갱신합니다."""
        self.apply_visual_settings()
        self.root.update_idletasks()

    def setup_main_layout(self):
        # ttkbootstrap은 표준 ttk 위젯을 스타일링하므로 ttk.PanedWinㅁㅁdow를 사용합니다.
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=tk.YES)

        # 사이드바와 콘텐츠 영역은 tb 위젯을 사용하여 테마를 직접 반영합니다.
        self.sidebar = tb.Frame(self.main_pane, width=220, bootstyle="light")
        self.main_pane.add(self.sidebar, weight=1)

        self.content_area = tb.Frame(self.main_pane)
        self.main_pane.add(self.content_area, weight=4)

        self.create_sidebar_content()
        self.create_main_content()

    def create_sidebar_content(self):
        lbl_title = tb.Label(self.sidebar, text="ACCOUNT", font=("Segoe UI", 16, "bold"), bootstyle="primary")
        lbl_title.pack(pady=30, padx=20)

        self.menu_buttons = []
        self.menu_map = {
            "대시보드": DashboardView,
            "가계": TransactionView,
            "월별 지출 관리": SpendingManagement,
            "자산 조회": FinancialStatus,
            "시스템 설정": SettingsView,
            "로그 조회": LogsView
        }

        for title, view_cls in self.menu_map.items():
            btn = tb.Button(self.sidebar, text=title, bootstyle="outline-primary")
            btn.pack(fill=tk.X, padx=20, pady=8)

            btn.view_info = (title, view_cls)
            btn.bind("<Button-1>", self.on_drag_start)
            btn.bind("<B1-Motion>", self.on_drag_motion)
            btn.bind("<ButtonRelease-1>", self.on_drag_release)
            self.menu_buttons.append(btn)

        tb.Label(self.sidebar, text="v2.1.1", foreground="gray").pack(side=tk.BOTTOM, pady=20)

    def create_main_content(self):
        # Notebook도 tb 위젯을 사용하여 부트스트랩 스타일을 적용합니다.
        self.notebook = tb.Notebook(self.content_area, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        
        # 탭 우클릭 메뉴 생성 및 확장
        self.tab_menu = tk.Menu(self.notebook, tearoff=0)
        self.tab_menu.add_command(label="이 탭 닫기", command=self.close_current_tab)
        self.tab_menu.add_command(label="다른 탭 모두 닫기", command=self.close_other_tabs)
        self.tab_menu.add_separator()
        self.tab_menu.add_command(label="모든 탭 닫기", command=self.close_all_tabs)
        
        # 탭 이벤트 바인딩
        self.notebook.bind("<Button-3>", self.on_tab_right_click)  # 우클릭
        self.notebook.bind("<Button-2>", self.on_tab_middle_click) # 휠 클릭 (Linux/Windows)
        
        self.add_tab("가계", TransactionView)

    def on_tab_middle_click(self, event):
        """마우스 휠 클릭 시 해당 탭 닫기"""
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab_by_index(index)
        except tk.TclError:
            pass

    def on_tab_right_click(self, event):
        """탭 위에서 우클릭 시 해당 탭을 선택하고 메뉴 표시"""
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
            self.notebook.select(index)
            self.tab_menu.post(event.x_root, event.y_root)
        except tk.TclError:
            pass

    def close_current_tab(self):
        """현재 선택된 탭을 닫음"""
        try:
            current_index = self.notebook.index("current")
            self.close_tab_by_index(current_index)
        except tk.TclError:
            pass

    def close_tab_by_index(self, index):
        """특정 인덱스의 탭을 닫음 (최소 1개 유지)"""
        if len(self.notebook.tabs()) > 1:
            self.notebook.forget(index)
        else:
            messagebox.showwarning("경고", "최소 하나 이상의 탭은 열려 있어야 합니다.")

    def close_other_tabs(self):
        """현재 선택된 탭을 제외한 모든 탭 닫기"""
        current_tab = self.notebook.select()
        for tab in self.notebook.tabs():
            if str(tab) != str(current_tab):
                self.notebook.forget(tab)

    def close_all_tabs(self):
        """모든 탭 닫기 시도 (최소 1개는 남김)"""
        tabs = self.notebook.tabs()
        if len(tabs) <= 1:
            self.close_tab_by_index(0)
            return
            
        # 마지막 하나만 남기고 모두 삭제
        for i in range(len(tabs) - 1):
            self.notebook.forget(tabs[i])
        messagebox.showinfo("알림", "최소 유지 조건에 따라 마지막 탭은 남겨두었습니다.")

    def add_tab(self, title, view_cls):
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text").strip() == title:
                self.notebook.select(tab)
                return

        if view_cls == SettingsView:
            new_view = view_cls(self.notebook, main_app=self)
        else:
            new_view = view_cls(self.notebook)
            
        self.notebook.add(new_view, text=f" {title} ")
        self.notebook.select(new_view)

    # --- 드래그 앤 드롭 로직 ---
    def on_drag_start(self, event):
        self.drag_source = event.widget
        self.drag_start_y = event.y
        self.is_dragging = False

    def on_drag_motion(self, event):
        if abs(event.y - self.drag_start_y) < 5 and not self.is_dragging: return
        self.is_dragging = True
        target = self.sidebar.winfo_containing(event.x_root, event.y_root)
        if target in self.menu_buttons and target != self.drag_source:
            src_idx = self.menu_buttons.index(self.drag_source)
            dst_idx = self.menu_buttons.index(target)
            self.menu_buttons.pop(src_idx)
            self.menu_buttons.insert(dst_idx, self.drag_source)
            if src_idx < dst_idx: self.drag_source.pack_configure(after=target)
            else: self.drag_source.pack_configure(before=target)

    def on_drag_release(self, event):
        if not self.is_dragging:
            title, view_cls = event.widget.view_info
            self.add_tab(title, view_cls)
        self.drag_source = None
        self.is_dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ComplexLayoutApp(root)
    root.mainloop()
