from tkinter import ttk

class LogsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="로그 조회 화면입니다.", font=("맑은 고딕", 15)).pack(expand=True)