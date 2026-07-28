import os
import json
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------
# 데이터 저장 디렉토리 설정
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_report_filepath(year, week):
    return os.path.join(DATA_DIR, f"report_{year}_W{week:02d}.json")

def load_report_text(year, week):
    filepath = get_report_filepath(year, week)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f).get("raw_text", "")
        except Exception:
            pass
    return ""

def save_report_text(year, week, text):
    filepath = get_report_filepath(year, week)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"year": year, "week": week, "raw_text": text}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("오류", f"저장 오류: {e}")
        return False

def get_week_range_str(year, week):
    first_day = datetime(year, 1, 4)
    start_of_year = first_day - timedelta(days=first_day.weekday())
    target_monday = start_of_year + timedelta(weeks=week-1)
    target_sunday = target_monday + timedelta(days=6)
    return f"{target_monday.strftime('%m.%d')} ~ {target_sunday.strftime('%m.%d')}"


# ----------------------------------------
# 한글 타자감 최적화 앱
# ----------------------------------------
class NativeWeeklyReportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("주간보고 간편 작성기 📝")
        self.geometry("1000x650")
        self.minsize(800, 500)

        today = datetime.now()
        self.year = today.year
        self.week = today.isocalendar()[1]

        self.debounce_timer = None  # 한글 입력 지연 처리용 타이머

        self._setup_ui()
        self.load_week_data()

    def _setup_ui(self):
        # 1. 상단 주차 선택
        top_bar = ttk.Frame(self, padding=8, relief="groove")
        top_bar.pack(fill="x", side="top")

        ttk.Button(top_bar, text="◀ 이전주", command=self.go_prev_week).pack(side="left", padx=3)
        self.lbl_week_title = ttk.Label(top_bar, text="", font=("Malgun Gothic", 11, "bold"))
        self.lbl_week_title.pack(side="left", padx=15)
        ttk.Button(top_bar, text="다음주 ▶", command=self.go_next_week).pack(side="left", padx=3)
        ttk.Button(top_bar, text="이번주", command=self.go_today).pack(side="left", padx=10)

        # 2. 메인 2분할
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # [좌측] 입력창 (한글 타자감 최적화 폰트 적용)
        left_box = ttk.Labelframe(main_frame, text=" ✏️ 원본 내용 입력 (엔터 두 번으로 구분) ", padding=10)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 맑은 고딕으로 폰트 지정 및 매끄러운 한글 처리
        self.txt_input = tk.Text(
            left_box,
            font=("Malgun Gothic", 10),
            undo=True,
            wrap="word",
            relief="solid",
            bd=1
        )
        self.txt_input.pack(fill="both", expand=True)

        # 🔥 핵심: KeyRelease 대신 타자가 멈췄을 때(0.3초 디바운스)만 변환을 실행하여 한글 씹힘 방지
        self.txt_input.bind("<KeyRelease>", self.on_key_release_debounced)

        # [우측] 자동 변환 결과창
        right_box = ttk.Labelframe(main_frame, text=" 📋 [샘플 응답결과] 자동 정제 결과 ", padding=10)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.txt_output = tk.Text(
            right_box,
            font=("Malgun Gothic", 10),
            bg="#F8F9FA",
            wrap="word",
            relief="solid",
            bd=1
        )
        self.txt_output.pack(fill="both", expand=True)

        # 3. 하단 버튼
        bottom_bar = ttk.Frame(self, padding=10)
        bottom_bar.pack(fill="x", side="bottom")

        ttk.Button(bottom_bar, text="💾 로컬 자동 저장", command=self.save_week_data).pack(side="left", padx=5)
        self.lbl_status = ttk.Label(bottom_bar, text="준비됨", foreground="gray")
        self.lbl_status.pack(side="left", padx=10)

        ttk.Button(bottom_bar, text="📋 결과 복사하기", command=self.copy_to_clipboard).pack(side="right", padx=5)

    # ----------------------------------------
    # 한글 입력 이질감 방지 엔진 (Debounce)
    # ----------------------------------------
    def on_key_release_debounced(self, event=None):
        # 한글 조합 중 방해받지 않도록 키 입력이 끝난 후 300ms(0.3초) 지났을 때만 변환 작동
        if self.debounce_timer:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(300, self.auto_convert)

    def auto_convert(self):
        raw_text = self.txt_input.get("1.0", tk.END).strip()
        if not raw_text:
            self.txt_output.delete("1.0", tk.END)
            return

        lines = raw_text.splitlines()
        blocks = []
        current_block = []

        for line in lines:
            cleaned = re.sub(r"^(\d+[\.\)]\s*|[\-\*\•]\s*)", "", line.strip())
            if not cleaned:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                current_block.append(cleaned)
        if current_block:
            blocks.append(current_block)

        formatted_lines = []
        for idx, block in enumerate(blocks, 1):
            if not block:
                continue
            formatted_lines.append(f"{idx}. {block[0]}")
            for detail in block[1:]:
                formatted_lines.append(f"        - {detail}")

        final_text = "\n".join(formatted_lines)

        # 오른쪽 창만 갱신 (왼쪽 입력창은 절대로 건드리지 않아 타자감 유지)
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, final_text)

    # ----------------------------------------
    # 데이터 제어
    # ----------------------------------------
    def load_week_data(self):
        week_str = get_week_range_str(self.year, self.week)
        self.lbl_week_title.config(text=f"🗓️ {self.year}년 {self.week}주차 ({week_str})")

        saved_text = load_report_text(self.year, self.week)
        self.txt_input.delete("1.0", tk.END)
        if saved_text:
            self.txt_input.insert(tk.END, saved_text)
        self.auto_convert()
        self.lbl_status.config(text="불러오기 완료")

    def save_week_data(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        if save_report_text(self.year, self.week, text):
            self.lbl_status.config(text="✅ 저장되었습니다.")
            messagebox.showinfo("성공", "주간보고가 저장되었습니다.")

    def go_prev_week(self):
        if self.week == 1: self.year -= 1; self.week = 52
        else: self.week -= 1
        self.load_week_data()

    def go_next_week(self):
        if self.week >= 52: self.year += 1; self.week = 1
        else: self.week += 1
        self.load_week_data()

    def go_today(self):
        today = datetime.now()
        self.year = today.year
        self.week = today.isocalendar()[1]
        self.load_week_data()

    def copy_to_clipboard(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("복사 완료", "클립보드에 복사되었습니다!")

if __name__ == "__main__":
    app = NativeWeeklyReportApp()
    app.mainloop()