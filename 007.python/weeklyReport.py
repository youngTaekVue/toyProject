import os
import json
import re
import time
import calendar
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# 1. python-dotenv 임포트 및 환경변수 로드 (.env 탐색)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Gemini API 공식 SDK Import
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ----------------------------------------
# 데이터 저장 디렉토리 설정 및 설정 상수
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 사용자의 주간 계산 오프셋 (+8주)
WEEK_OFFSET = 8

def get_report_filepath(year, week):
    return os.path.join(DATA_DIR, f"report_{year}_W{week:02d}.json")

def load_report_data(year, week):
    filepath = get_report_filepath(year, week)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_report_data(year, week, tasks, formatted_text):
    json_path = get_report_filepath(year, week)

    try:
        # 구조화된 JSON 데이터만 저장
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "year": year,
                "week": week,
                "tasks": tasks
            }, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {e}")
        return False

def get_week_range_str(year, week):
    iso_week = week - WEEK_OFFSET
    first_day = datetime(year, 1, 4)
    start_of_year = first_day - timedelta(days=first_day.weekday())
    target_monday = start_of_year + timedelta(weeks=iso_week-1)
    target_friday = target_monday + timedelta(days=4)
    return f"{target_monday.strftime('%m.%d')} ~ {target_friday.strftime('%m.%d')}"

def get_monday_from_year_week(year, week):
    iso_week = week - WEEK_OFFSET
    first_day = datetime(year, 1, 4)
    start_of_year = first_day - timedelta(days=first_day.weekday())
    return start_of_year + timedelta(weeks=iso_week-1)

def parse_legacy_text(raw_text):
    if not raw_text.strip():
        return []

    blocks_raw = raw_text.split("\n\n")
    tasks = []

    for block in blocks_raw:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        first_line = lines[0]
        first_line = re.sub(r"^[✔⏳💤⏸]\s*", "", first_line)

        status = "작업대기"
        status_match = re.search(r"\[(작업대기|작업중|완료|콜요청|요청|청구\s*실패|Done|Doing|WIP|Pending|To Do|Hold)\]", first_line, re.IGNORECASE)

        title = first_line
        if status_match:
            raw_status = status_match.group(1)
            if raw_status in ["완료", "Done"]:
                status = "완료"
            elif raw_status in ["작업중", "진행중", "Doing", "WIP"]:
                status = "작업중"
            else:
                status = "작업대기"

            title = first_line.replace(status_match.group(0), "").strip()

        details_list = []
        for line in lines[1:]:
            cleaned_detail = re.sub(r"^[-*•]\s*", "", line)
            details_list.append(cleaned_detail)

        details = "\n".join(details_list)
        tasks.append({
            "title": title,
            "requester": "선택안함",
            "status": status,
            "details": details,
            "start_time": "",
            "end_date": ""
        })

    return tasks

# ----------------------------------------
# 콤팩트 달력 팝업 창
# ----------------------------------------
class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, target_entry):
        super().__init__(parent)
        self.withdraw()
        self.target_entry = target_entry
        self.title("날짜 선택")

        popup_w = 250
        popup_h = 240

        top_parent = parent.winfo_toplevel()
        top_parent.update_idletasks()

        p_x = top_parent.winfo_x()
        p_y = top_parent.winfo_y()
        p_w = top_parent.winfo_width()
        p_h = top_parent.winfo_height()

        center_x = p_x + (p_w - popup_w) // 2
        center_y = p_y + (p_h - popup_h) // 2

        self.geometry(f"{popup_w}x{popup_h}+{center_x}+{center_y}")
        self.resizable(False, False)
        self.transient(top_parent)
        self.grab_set()

        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month

        self._setup_ui()
        self.deiconify()

    def _setup_ui(self):
        top_frame = ttk.Frame(self, padding=5)
        top_frame.pack(fill="x")

        ttk.Button(top_frame, text="◀", width=3, command=self.prev_month).pack(side="left")
        self.lbl_month = ttk.Label(top_frame, text="", font=("Malgun Gothic", 10, "bold"))
        self.lbl_month.pack(side="left", expand=True)
        ttk.Button(top_frame, text="▶", width=3, command=self.next_month).pack(side="right")

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=2)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for d in days:
            lbl = ttk.Label(header_frame, text=d, width=4, anchor="center")
            lbl.pack(side="left", fill="x", expand=True)

        self.grid_frame = ttk.Frame(self, padding=5)
        self.grid_frame.pack(fill="both", expand=True)

        self.draw_calendar()

    def draw_calendar(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.lbl_month.config(text=f"{self.current_year}년 {self.current_month}월")

        cal_obj = calendar.Calendar(firstweekday=calendar.SUNDAY)
        cal = cal_obj.monthdayscalendar(self.current_year, self.current_month)

        for r_idx, week in enumerate(cal):
            for c_idx, day in enumerate(week):
                if day == 0:
                    lbl = ttk.Label(self.grid_frame, text="", width=4)
                    lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2)
                else:
                    fg_color = "black"
                    if c_idx == 0: fg_color = "red"
                    elif c_idx == 6: fg_color = "blue"

                    style_name = f"CalBtn_{r_idx}_{c_idx}.TButton"
                    style = ttk.Style()
                    style.configure(style_name, font=("Malgun Gothic", 9), foreground=fg_color)

                    btn = ttk.Button(
                        self.grid_frame,
                        text=str(day),
                        width=3,
                        style=style_name,
                        command=lambda d=day: self.select_date(d)
                    )
                    btn.grid(row=r_idx, column=c_idx, padx=2, pady=2)

    def prev_month(self):
        if self.current_month == 1:
            self.current_year -= 1
            self.current_month = 12
        else:
            self.current_month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_year += 1
            self.current_month = 1
        else:
            self.current_month += 1
        self.draw_calendar()

    def select_date(self, day):
        date_str = f"{self.current_month:02d}.{day:02d}"
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, date_str)
        self.target_entry.event_generate("<KeyRelease>")
        self.destroy()

# ----------------------------------------
# 개별 업무 입력 카드 (TaskCard)
# ----------------------------------------
class TaskCard(ttk.LabelFrame):
    def __init__(self, parent, container, on_change_callback, on_delete_callback,
                 title="", requester="선택안함", status="작업대기", details="", start_time="", end_date=""):
        super().__init__(container, text=" 📋 업무 ")
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback

        self._setup_ui(title, requester, status, details, start_time, end_date)

    def _setup_ui(self, title, requester, status, details, start_time, end_date):
        inner_frame = ttk.Frame(self, padding=8)
        inner_frame.pack(fill="both", expand=True)

        row1 = ttk.Frame(inner_frame)
        row1.pack(fill="x", pady=(0, 5))

        ttk.Label(row1, text="요양기관명").pack(side="left", padx=(0, 4))
        self.ent_title = ttk.Entry(row1)
        self.ent_title.pack(side="left", padx=3, fill="x", expand=True)
        self.ent_title.insert(0, title)
        self.ent_title.bind("<KeyRelease>", self.on_key_release)

        ttk.Label(row1, text="요청자").pack(side="left", padx=(8, 4))
        self.combo_requester = ttk.Combobox(
            row1,
            values=["선택안함", "내부부서", "내부전화", "송수신"],
            width=8,
            state="readonly",
            justify="center"
        )
        self.combo_requester.pack(side="left", padx=2)
        self.combo_requester.set(requester if requester else "선택안함")
        self.combo_requester.bind("<<ComboboxSelected>>", self.on_combo_change)

        ttk.Label(row1, text="진행상태").pack(side="left", padx=(8, 4))
        self.combo_status = ttk.Combobox(
            row1,
            values=["작업대기", "작업중", "완료"],
            width=8,
            state="readonly",
            justify="center"
        )
        self.combo_status.pack(side="left", padx=2)
        self.combo_status.set(status if status else "작업대기")
        self.combo_status.bind("<<ComboboxSelected>>", self.on_combo_change)

        row2 = ttk.Frame(inner_frame)
        row2.pack(fill="x", pady=(0, 6))

        ttk.Label(row2, text="시작일자").pack(side="left", padx=(0, 4))
        self.start_frame = ttk.Frame(row2)
        self.start_frame.pack(side="left", padx=3)

        self.ent_start_time = ttk.Entry(self.start_frame, width=7, justify="center")
        self.ent_start_time.pack(side="left", fill="y")
        self.ent_start_time.insert(0, start_time)
        self.ent_start_time.bind("<KeyRelease>", self.on_key_release)

        self.btn_start_cal = tk.Button(
            self.start_frame,
            text="📅",
            width=3,
            command=lambda: CalendarPopup(self.parent, self.ent_start_time),
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0"
        )
        self.btn_start_cal.pack(side="left", padx=(1, 0))

        ttk.Label(row2, text="종료일자").pack(side="left", padx=(20, 4))
        self.end_frame = ttk.Frame(row2)
        self.end_frame.pack(side="left", padx=3)

        self.ent_end_date = ttk.Entry(self.end_frame, width=7, justify="center")
        self.ent_end_date.pack(side="left", fill="y")
        self.ent_end_date.insert(0, end_date)
        self.ent_end_date.bind("<KeyRelease>", self.on_key_release)

        self.btn_end_cal = tk.Button(
            self.end_frame,
            text="📅",
            width=3,
            command=lambda: CalendarPopup(self.parent, self.ent_end_date),
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0"
        )
        self.btn_end_cal.pack(side="left", padx=(1, 0))

        self.op_frame = ttk.Frame(row2)
        self.op_frame.pack(side="right", padx=(10, 0))

        self.btn_up = tk.Button(
            self.op_frame, text="🔼", width=3, height=1,
            command=self.move_up,
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0"
        )
        self.btn_up.pack(side="left", padx=1)

        self.btn_down = tk.Button(
            self.op_frame, text="🔽", width=3, height=1,
            command=self.move_down,
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0"
        )
        self.btn_down.pack(side="left", padx=1)

        self.btn_delete = tk.Button(
            self.op_frame, text="❌", width=3, height=1,
            command=self.delete_row,
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0"
        )
        self.btn_delete.pack(side="left", padx=1)

        row3 = ttk.Frame(inner_frame)
        row3.pack(fill="x")

        ttk.Label(row3, text="상세 업무 내용 (줄바꿈 가능)").pack(anchor="w", pady=(0, 2))

        self.txt_details = tk.Text(row3, height=4, font=("Malgun Gothic", 9), relief="solid", bd=1)
        self.txt_details.pack(fill="x", expand=True, padx=2)
        self.txt_details.insert("1.0", details)
        self.txt_details.bind("<KeyRelease>", self.on_key_release)

    def update_label(self, idx):
        self.config(text=f" 📋 업무 #{idx} ")

    def get_data(self):
        title = self.ent_title.get().strip()
        requester = self.combo_requester.get()
        status = self.combo_status.get()
        details = self.txt_details.get("1.0", tk.END).strip()
        start_time = self.ent_start_time.get().strip()
        end_date = self.ent_end_date.get().strip()
        return {
            "title": title,
            "requester": requester,
            "status": status,
            "details": details,
            "start_time": start_time,
            "end_date": end_date
        }

    def on_key_release(self, event=None):
        self.on_change_callback()

    def on_combo_change(self, event=None):
        self.on_change_callback()

    def delete_row(self):
        self.on_delete_callback(self)

    def move_up(self):
        self.parent.move_row_up(self)

    def move_down(self):
        self.parent.move_row_down(self)

# ----------------------------------------
# 메인 애플리케이션
# ----------------------------------------
class NativeWeeklyReportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("주간보고 작성기 📝 (Gemini AI 연동)")
        self.geometry("1300x720")
        self.minsize(1100, 550)

        today = datetime.now()
        self.current_monday = today - timedelta(days=today.weekday())
        self.update_year_week_from_monday()

        self.rows = []

        # Gemini Client 초기화
        self.gemini_client = None
        api_key = os.getenv("GEMINI_API_KEY")

        if GEMINI_AVAILABLE and api_key:
            try:
                self.gemini_client = genai.Client()
                print("✅ Gemini API 연결 성공")
            except Exception as e:
                print(f"❌ Gemini Client 초기화 실패: {e}")
        else:
            print(f"⚠️ API Key 미인식 (SDK가용성: {GEMINI_AVAILABLE}, Key존재: {bool(api_key)})")

        self._setup_ui()
        self.load_week_data()

    def _setup_ui(self):
        top_bar = ttk.Frame(self, padding=8, relief="groove")
        top_bar.pack(fill="x", side="top")

        self.btn_add = tk.Button(
            top_bar, text="➕ 업무 추가",
            command=self.add_empty_row,
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0",
            font=("Malgun Gothic", 9, "bold"), padx=5, pady=2
        )
        self.btn_add.pack(side="right", padx=5)

        center_frame = ttk.Frame(top_bar)
        center_frame.pack(side="top", anchor="center")

        ttk.Button(center_frame, text="◀ 이전주", command=self.go_prev_week).pack(side="left", padx=3)

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 3, current_year + 3)]
        self.combo_year = ttk.Combobox(center_frame, values=years, width=6, state="readonly", justify="center")
        self.combo_year.pack(side="left", padx=3)
        ttk.Label(center_frame, text="년").pack(side="left")

        weeks = [f"{w:02d}" for w in range(1, 61)]
        self.combo_week = ttk.Combobox(center_frame, values=weeks, width=4, state="readonly", justify="center")
        self.combo_week.pack(side="left", padx=3)
        ttk.Label(center_frame, text="주차").pack(side="left", padx=(0, 15))

        self.lbl_week_title = ttk.Label(center_frame, text="", font=("Malgun Gothic", 11, "bold"))
        self.lbl_week_title.pack(side="left", padx=10)

        self.combo_year.bind("<<ComboboxSelected>>", self.on_date_combo_changed)
        self.combo_week.bind("<<ComboboxSelected>>", self.on_date_combo_changed)

        ttk.Button(center_frame, text="다음주 ▶", command=self.go_next_week).pack(side="left", padx=3)
        ttk.Button(center_frame, text="이번주", command=self.go_today).pack(side="left", padx=10)

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_box = ttk.Labelframe(main_frame, text=" 📋 업무 등록 및 편집 ", padding=10)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.canvas = tk.Canvas(left_box, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left_box, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- 우측: 정제 결과 및 Gemini AI 컨트롤 ---
        right_box = ttk.Labelframe(main_frame, text=" 📋 업무 보고서 정제 결과 ", padding=10)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # AI 연동 옵션 컨트롤 바
        ai_control_bar = ttk.Frame(right_box)
        ai_control_bar.pack(fill="x", pady=(0, 5))

        # ✨ [AI 정제 생성] 수동 실행 버튼
        self.btn_run_ai = ttk.Button(
            ai_control_bar,
            text="✨ AI 정제 생성",
            command=self.request_ai_refinement
        )
        self.btn_run_ai.pack(side="left")

        if not self.gemini_client:
            self.btn_run_ai.config(state="disabled")

        self.combo_ai_mode = ttk.Combobox(
            ai_control_bar,
            values=["핵심 요약형", "정통 보고서형"],
            width=12,
            state="readonly"
        )
        self.combo_ai_mode.set("핵심 요약형")
        self.combo_ai_mode.pack(side="right")

        self.txt_output = tk.Text(
            right_box,
            font=("Malgun Gothic", 10),
            bg="#F8F9FA",
            wrap="word",
            relief="solid",
            bd=1
        )
        self.txt_output.pack(fill="both", expand=True)

        bottom_bar = ttk.Frame(self, padding=10)
        bottom_bar.pack(fill="x", side="bottom")

        ttk.Button(bottom_bar, text="💾 주간보고 저장", command=self.save_week_data).pack(side="left", padx=5)
        self.lbl_status = ttk.Label(bottom_bar, text="준비 완료", foreground="gray")
        self.lbl_status.pack(side="left", padx=10)

        ttk.Button(bottom_bar, text="📋 텍스트 복사", command=self.copy_to_clipboard).pack(side="right", padx=5)

    def _on_canvas_configure(self, event):
        if hasattr(self, 'canvas_window') and self.canvas_window is not None:
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    def add_empty_row(self):
        self.add_row()
        self.render_basic_text()

    def add_row(self, title="", requester="선택안함", status="작업대기", details="", start_time="", end_date=""):
        card = TaskCard(
            self,
            self.scrollable_frame,
            on_change_callback=self.render_basic_text,
            on_delete_callback=self.remove_row,
            title=title,
            requester=requester,
            status=status,
            details=details,
            start_time=start_time,
            end_date=end_date
        )
        self.rows.append(card)
        self.repack_cards()

    def remove_row(self, row_obj):
        if len(self.rows) <= 1:
            messagebox.showwarning("주의", "최소 한 개의 업무 카드는 유지해야 합니다.")
            return
        row_obj.destroy()
        self.rows.remove(row_obj)
        self.repack_cards()
        self.render_basic_text()

    def clear_rows(self):
        for row in self.rows:
            row.destroy()
        self.rows = []

    def repack_cards(self):
        for card in self.rows:
            card.pack_forget()
        for idx, card in enumerate(self.rows, 1):
            card.pack(fill="x", pady=6, padx=5)
            card.update_label(idx)

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def move_row_up(self, row_obj):
        idx = self.rows.index(row_obj)
        if idx > 0:
            self.rows[idx], self.rows[idx-1] = self.rows[idx-1], self.rows[idx]
            self.repack_cards()
            self.render_basic_text()

    def move_row_down(self, row_obj):
        idx = self.rows.index(row_obj)
        if idx < len(self.rows) - 1:
            self.rows[idx], self.rows[idx+1] = self.rows[idx+1], self.rows[idx]
            self.repack_cards()
            self.render_basic_text()

    # 입력 중에는 기본 포맷 텍스트만 실시간으로 즉시 출력
    def render_basic_text(self):
        raw_text = self._build_raw_text()
        self._update_output_text(raw_text)
        self.lbl_status.config(text="기본 텍스트 조합 완료 (AI 정제 필요 시 버튼 클릭)")

    def _build_raw_text(self):
        formatted_lines = []

        for idx, row in enumerate(self.rows, 1):
            data = row.get_data()
            title = data["title"]
            status = data["status"]
            details = data["details"]

            if not title and not status and not details:
                continue

            cleaned_title = re.sub(r"^(\d+[\.\)]\s*)", "", title.strip())
            line_title = f"{idx}. {cleaned_title}"
            formatted_lines.append(line_title)

            if details:
                detail_lines = details.splitlines()
                for d_line in detail_lines:
                    if d_line.strip():
                        formatted_lines.append(f"        - {d_line.strip()}")

            formatted_lines.append("")

        if formatted_lines and formatted_lines[-1] == "":
            formatted_lines.pop()

        return "\n".join(formatted_lines)

    # 버튼 클릭 시에만 Gemini API 연동 호출
    def request_ai_refinement(self):
        raw_text = self._build_raw_text()

        if not raw_text.strip():
            messagebox.showwarning("주의", "정제할 업무 내용이 없습니다.")
            return

        if not self.gemini_client:
            messagebox.showerror("오류", "Gemini API가 연동되지 않았습니다. .env 파일의 API Key를 확인해 주세요.")
            return

        self.btn_run_ai.config(state="disabled")
        self.lbl_status.config(text="✨ Gemini AI 정제 요청 중...")
        mode = self.combo_ai_mode.get()

        threading.Thread(
            target=self._run_gemini_refine_thread,
            args=(raw_text, mode),
            daemon=True
        ).start()

    # --- Gemini API 호출 스레드 메서드 ---
    def _run_gemini_refine_thread(self, raw_text, mode):
        style_instruction = "핵심 요약 형태(불렛포인트)" if mode == "핵심 요약형" else "격식 있는 정통 보고서 형태(줄글/명확한 문장)"
        sys_instruction = (
            f"너는 의료/시스템 업무 주간보고서 정제 전문가이다. "
            f"입력된 업무 항목들을 읽고, 가독성이 높고 명확한 {style_instruction}로 정제하라. "
            f"원문의 요양기관명, 작업 내용, 통신 체크 및 완료 여부 등의 중요한 핵심 정보는 절대로 누락하지 마라."
        )

        max_retries = 3
        refined_result = None

        for attempt in range(max_retries):
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=raw_text,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruction,
                        temperature=0.2,
                    )
                )
                refined_result = response.text
                break
            except APIError as e:
                if e.code == 429:
                    time.sleep((attempt + 1) * 1.5)
                else:
                    break
            except Exception as e:
                print(f"API Error: {e}")
                break

        # UI 업데이트는 메인 스레드에서 처리
        def update_ui():
            self.btn_run_ai.config(state="normal")
            if refined_result:
                self._update_output_text(refined_result)
                self.lbl_status.config(text="✨ Gemini AI 정제 완료!")
            else:
                self.lbl_status.config(text="AI 정제 실패 (기본 텍스트 유지)")

        self.after(0, update_ui)

    def _update_output_text(self, text):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, text)

    def load_week_data(self):
        week_str = get_week_range_str(self.year, self.week)
        self.lbl_week_title.config(text=f"🗓️ {self.year}년 {self.week}주차 ({week_str})")

        if hasattr(self, 'combo_year') and hasattr(self, 'combo_week'):
            self.combo_year.set(str(self.year))
            self.combo_week.set(f"{self.week:02d}")

        self.clear_rows()
        data = load_report_data(self.year, self.week)

        if data:
            if "tasks" in data:
                tasks = data["tasks"]
                for task in tasks:
                    self.add_row(
                        title=task.get("title", ""),
                        requester=task.get("requester", "선택안함"),
                        status=task.get("status", "작업대기"),
                        details=task.get("details", ""),
                        start_time=task.get("start_time", ""),
                        end_date=task.get("end_date", "")
                    )
            elif "raw_text" in data:
                tasks = parse_legacy_text(data["raw_text"])
                for task in tasks:
                    self.add_row(
                        title=task.get("title", ""),
                        requester=task.get("requester", "선택안함"),
                        status=task.get("status", "작업대기"),
                        details=task.get("details", ""),
                        start_time="",
                        end_date=""
                    )

        if not self.rows:
            self.add_row()

        self.render_basic_text()
        self.lbl_status.config(text="데이터를 불러왔습니다.")

    def save_week_data(self):
        tasks = []
        for row in self.rows:
            data = row.get_data()
            if not data["title"] and not data["details"] and not data["start_time"] and not data["end_date"]:
                continue
            tasks.append(data)

        formatted_text = self.txt_output.get("1.0", tk.END).strip()

        if save_report_data(self.year, self.week, tasks, formatted_text):
            self.lbl_status.config(text="주간보고가 저장되었습니다.")
            messagebox.showinfo("저장 완료", "주간보고가 정상적으로 저장되었습니다.")

    def update_year_week_from_monday(self):
        iso_year, iso_week, _ = self.current_monday.isocalendar()
        self.year = iso_year
        self.week = iso_week + WEEK_OFFSET

    def go_prev_week(self):
        self.current_monday -= timedelta(weeks=1)
        self.update_year_week_from_monday()
        self.load_week_data()

    def go_next_week(self):
        self.current_monday += timedelta(weeks=1)
        self.update_year_week_from_monday()
        self.load_week_data()

    def go_today(self):
        today = datetime.now()
        self.current_monday = today - timedelta(days=today.weekday())
        self.update_year_week_from_monday()
        self.load_week_data()

    def copy_to_clipboard(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("복사 완료", "정제 결과가 클립보드에 복사되었습니다.")

    def on_date_combo_changed(self, event=None):
        try:
            year = int(self.combo_year.get())
            week = int(self.combo_week.get())
        except ValueError:
            return

        self.current_monday = get_monday_from_year_week(year, week)
        self.year = year
        self.week = week
        self.load_week_data()

    def jump_to_week(self, year, week):
        self.current_monday = get_monday_from_year_week(year, week)
        self.year = year
        self.week = week
        self.load_week_data()

    def _bind_mousewheel(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    app = NativeWeeklyReportApp()
    app.mainloop()