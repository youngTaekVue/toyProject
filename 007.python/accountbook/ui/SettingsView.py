import tkinter as tk
from tkinter import ttk

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="시스템 설정 화면입니다.", font=("맑은 고딕", 15)).pack(expand=True)