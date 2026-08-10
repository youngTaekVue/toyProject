import os
import json
import re
import time
import calendar
import threading
from concurrent.futures import ThreadPoolExecutor
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

# --- 상태 및 요청자 상수 ---
STATUS_PENDING = "작업대기"
STATUS_DOING = "작업중"
STATUS_DONE = "완료"
REQUESTER_NONE = "선택안함"
REQUESTER_INTERNAL_DEPT = "내부부서"
REQUESTER_INTERNAL_CALL = "내부전화"
REQUESTER_TRX = "송수신"

# 사용자의 주간 계산 오프셋 (+9주)
WEEK_OFFSET = 9

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
    txt_path = json_path.replace(".json", ".txt")

    try:
        # 1. 구조화된 JSON 데이터 저장
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "year": year,
                "week": week,
                "tasks": tasks
            }, f, ensure_ascii=False, indent=2)

        # 2. 바로 복사해 쓸 수 있는 TXT 텍스트 파일 저장
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(formatted_text)

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

        status = STATUS_PENDING
        status_match = re.search(r"\[(작업대기|작업중|완료|콜요청|요청|청구\s*실패|Done|Doing|WIP|Pending|To Do|Hold)\]", first_line, re.IGNORECASE)

        title = first_line
        if status_match:
            raw_status = status_match.group(1)
            if raw_status in ["완료", "Done"]:
                status = STATUS_DONE
            elif raw_status in ["작업중", "진행중", "Doing", "WIP"]:
                status = STATUS_DOING
            else:
                status = STATUS_PENDING

            title = first_line.replace(status_match.group(0), "").strip()

        details_list = []
        for line in lines[1:]:
            cleaned_detail = re.sub(r"^[-*•]\s*", "", line)
            details_list.append(cleaned_detail)

        details = "\n".join(details_list)
        tasks.append({
            "title": title,
            "requester": REQUESTER_NONE,
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
                 title="", requester=REQUESTER_NONE, status=STATUS_PENDING, details="", start_time="", end_date=""):
        super().__init__(container, text=" 📋 업무 ")
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback
        self.is_dirty = False  # AI 교정 필요 여부 플래그

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
            values=[REQUESTER_NONE, REQUESTER_INTERNAL_DEPT, REQUESTER_INTERNAL_CALL, REQUESTER_TRX],
            width=8,
            state="readonly",
            justify="center"
        )
        self.combo_requester.pack(side="left", padx=2)
        self.combo_requester.set(requester if requester else REQUESTER_NONE)
        self.combo_requester.bind("<<ComboboxSelected>>", self.on_combo_change)

        ttk.Label(row1, text="진행상태").pack(side="left", padx=(8, 4))
        self.combo_status = ttk.Combobox(
            row1,
            values=[STATUS_PENDING, STATUS_DOING, STATUS_DONE],
            width=8,
            state="readonly",
            justify="center"
        )
        self.combo_status.pack(side="left", padx=2)
        self.combo_status.set(status if status else STATUS_PENDING)
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

        # --- [신규] AI 제안 컨테이너 프레임 (처음에는 비노출) ---
        self.ai_proposal_frame = ttk.Frame(inner_frame, padding=(2, 4))
        
        # 1) 제안 헤더 바 (좌측 타이틀 + 우측 적용/거절 버튼)
        proposal_header = ttk.Frame(self.ai_proposal_frame)
        proposal_header.pack(fill="x", pady=(0, 2))
        
        self.lbl_proposal_tag = ttk.Label(
            proposal_header, text="✨ AI 추천 문장", 
            font=("Malgun Gothic", 9, "bold"), foreground="#137333"
        )
        self.lbl_proposal_tag.pack(side="left")
        
        self.btn_reject_proposal = tk.Button(
            proposal_header, text="❌ 거절",
            command=self.hide_ai_proposal,
            relief="flat", bd=0, cursor="hand2", bg="#FCE8E6", fg="#C5221F",
            font=("Malgun Gothic", 8, "bold"), padx=6, pady=1
        )
        self.btn_reject_proposal.pack(side="right", padx=2)

        self.btn_apply_proposal = tk.Button(
            proposal_header, text="✔️ 적용",
            command=self.apply_proposal,
            relief="flat", bd=0, cursor="hand2", bg="#E6F4EA", fg="#137333",
            font=("Malgun Gothic", 8, "bold"), padx=6, pady=1
        )
        self.btn_apply_proposal.pack(side="right", padx=2)

        # 2) 제안 본문 바 (다중 라인 자동 줄바꿈 라벨로 잘림 차단)
        proposal_body = ttk.Frame(self.ai_proposal_frame)
        proposal_body.pack(fill="x")
        
        self.lbl_proposal = ttk.Label(
            proposal_body, text="",
            font=("Malgun Gothic", 9, "italic"),
            foreground="#555555",
            justify="left",
            anchor="w",
            wraplength=480  # 480px 도달 시 자동 줄바꿈
        )
        self.lbl_proposal.pack(fill="x", expand=True, padx=5, pady=2)

    def show_ai_proposal(self, proposal_text):
        self.lbl_proposal.config(text=proposal_text)
        # 상세 업무 내용 바로 아래에 pack
        self.ai_proposal_frame.pack(fill="x", pady=(5, 0))
        self.parent.repack_cards()

    def hide_ai_proposal(self):
        self.ai_proposal_frame.pack_forget()
        self.parent.repack_cards()

    def apply_proposal(self):
        proposal_text = self.lbl_proposal.cget("text")
        self.txt_details.delete("1.0", tk.END)
        self.txt_details.insert("1.0", proposal_text)
        self.hide_ai_proposal()
        self.is_dirty = False  # AI 제안 적용 시, 'clean' 상태로 변경
        self.on_change_callback()

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
        self.is_dirty = True  # 내용 변경 시, 'dirty' 상태로 변경
        self.on_change_callback()

    def on_combo_change(self, event=None):
        self.is_dirty = True  # 내용 변경 시, 'dirty' 상태로 변경
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

        # ✨ [AI 문장 교정 제안] 수동 실행 버튼 (콤보 박스는 요구대로 제거)
        self.btn_run_ai = ttk.Button(
            ai_control_bar,
            text="✨ AI 문장 교정 제안",
            command=self.request_ai_refinement
        )
        self.btn_run_ai.pack(side="left")

        if not self.gemini_client:
            self.btn_run_ai.config(state="disabled")

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
        card = self.add_row()
        card.is_dirty = True  # 새로 추가된 빈 카드는 항상 'dirty' 상태
        self.render_basic_text()

    def add_row(self, title="", requester=REQUESTER_NONE, status=STATUS_PENDING, details="", start_time="", end_date=""):
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
        return card

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
        self.lbl_status.config(text="기본 텍스트 조합 완료 (AI 교정 제안 필요 시 버튼 클릭)")

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

    # 버튼 클릭 시에만 Gemini API 연동 호출 (단일 호출 통합 스레드 구동)
    def request_ai_refinement(self):
        if not self.gemini_client:
            messagebox.showerror("오류", "Gemini API가 연동되지 않았습니다. .env 파일의 API Key를 확인해 주세요.")
            return

        # AI 요청용 텍스트 빌드 (내용이 변경된 'dirty' 카드만 대상)
        ai_input_lines = []
        has_dirty_content = False
        for idx, card in enumerate(self.rows, 1):
            if card.is_dirty and card.get_data()["details"]:
                details = card.get_data()["details"].strip()
                ai_input_lines.append(f"===CARD_{idx}===\n{details}")
                has_dirty_content = True

        if not has_dirty_content:
            messagebox.showwarning("주의", "AI 교정을 요청할 변경된 내용이 없습니다.")
            return

        raw_input_text = "\n\n".join(ai_input_lines)

        self.btn_run_ai.config(state="disabled")
        self.lbl_status.config(text="✨ AI 문장 교정 제안 생성 중...")

        threading.Thread(
            target=self._run_single_call_refine_thread,
            args=(raw_input_text,),
            daemon=True
        ).start()

    # --- 단 1회의 API 호출로 전체 카드를 통합 교정 처리 (429 한도 초과 시 모델 자동 변경 및 대기 재시도) ---
    def _run_single_call_refine_thread(self, raw_input_text):
        sys_instruction = (
            "너는 주간보고서 상세 문장 교정 전문가이다.\n"
            "사용자가 전달한 본문은 여러 개의 카드 입력 정보이며, 각 카드 정보는 '===CARD_번호===' 마커로 구분되어 있다.\n"
            "네 역할은 각 마커 뒤에 오는 상세 문장을 읽고, 원래 의미를 절대 훼손하지 않으면서 격식 있고 전문적인 '보고서용 개조식 문체'로 매끄럽고 고급스럽게 교정하는 것이다.\n\n"
            "말투 규칙:\n"
            "1. '~하였습니다', '~했습니다', '~합니다', '~함' 등의 서술형 종결어미를 절대 쓰지 마라.\n"
            "2. 무조건 명사나 명사형 종결어미(예: '~ 완료', '~ 조치', '~ 분석', '~ 요청', '~ 확인', '~ 진행', '~ 파악')로 문장을 간결하게 끝맺어라.\n"
            "   - [잘못된 예] 원격 연결을 통해 SSL 인증서를 갱신하였습니다. -> [올바른 예] 원격 연결을 통한 SSL 인증서 수동 갱신 완료\n"
            "   - [잘못된 예] 에러가 나서 개발팀에 물어보고 조치했습니다. -> [올바른 예] 시스템 오류 발생에 따른 연동 부서 확인 및 조치 완료\n"
            "3. 출력 양식은 입력받은 마커 구조('===CARD_번호===')를 절대 지우거나 수정하지 말고 그대로 복사해서 각 결과의 헤더로 유지하라.\n"
            "   - 예시:\n"
            "     ===CARD_1===\n"
            "     원격 연결을 통한 SSL 인증서 수동 갱신 완료\n"
            "     ===CARD_2===\n"
            "     시스템 오류 발생에 따른 연동 부서 확인 및 조치 완료\n"
            "4. 없는 사실을 지어내거나 추정하여 새로운 작업 내용을 임의로 추가하지 마라."
        )

        refined_output = None

        # 순차적으로 시도할 대체 모델 리스트 (존재하는 모델명으로 수정)
        candidate_models = ["gemini-1.5-flash", "gemini-1.5-pro"]

        def make_api_call(target_model):
            response = self.gemini_client.models.generate_content(
                model=target_model,
                contents=raw_input_text,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=0.2,
                )
            )
            return response.text.strip()

        # 1. 모델 순회하며 호출 시도
        for model_name in candidate_models:
            try:
                print(f"🤖 [{model_name}] 모델로 AI 교정 호출 시도...")
                refined_output = make_api_call(model_name)
                print(f"✅ [{model_name}] 호출 성공!")
                break
            except APIError as e:
                if e.code == 429 or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"⚠️ [{model_name}] 한도 초과(429). 다음 모델로 전환합니다.")
                    self.after(0, lambda m=model_name: self.lbl_status.config(
                        text=f"⏳ {m} 한도 초과로 대체 모델 전환 중..."
                    ))
                    continue
                else:
                    print(f"❌ [{model_name}] API Error: {e}")
                    break
            except Exception as e:
                print(f"❌ [{model_name}] 일반 오류: {e}")
                break

        # 2. 후보 모델이 모두 429 한도 초과인 경우 60초 대기 후 최후 재시도
        if not refined_output:
            print("⚠️ 모든 후보 모델 한도 초과! 60초 대기 후 재시도합니다...")
            self.after(0, lambda: self.lbl_status.config(text="⏳ 모든 모델 한도 초과로 60초 대기 중..."))
            time.sleep(60)

            for model_name in candidate_models:
                try:
                    print(f"🔄 재시도: [{model_name}] 호출 시도...")
                    refined_output = make_api_call(model_name)
                    print(f"✅ [{model_name}] 재시도 성공!")
                    break
                except Exception as e:
                    print(f"❌ [{model_name}] 재시도 실패: {e}")

        # 3. UI 업데이트 (메인 스레드)
        def update_ui():
            self.btn_run_ai.config(state="normal")
            if not refined_output:
                self.lbl_status.config(text="AI 교정 제안 생성 실패 (모든 모델 한도 초과 또는 오류)")
                return

            pattern = r"===CARD_(\d+)===\s*(.*?)(?=\s*===CARD_\d+===|\s*$)"
            matches = re.findall(pattern, refined_output, re.DOTALL)
            proposal_map = {int(idx): text.strip() for idx, text in matches}

            success_count = 0
            for idx, card in enumerate(self.rows, 1):
                if idx in proposal_map and proposal_map[idx]:
                    card.show_ai_proposal(proposal_map[idx])
                    success_count += 1

            if success_count > 0:
                self.lbl_status.config(text=f"✨ {success_count}개 업무에 AI 교정 제안 완료!")
            else:
                self.lbl_status.config(text="AI 제안 파싱 실패 (양식 불일치)")

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
                        requester=task.get("requester", REQUESTER_NONE),
                        status=task.get("status", STATUS_PENDING),
                        details=task.get("details", ""),
                        start_time=task.get("start_time", ""),
                        end_date=task.get("end_date", "")
                    )
            elif "raw_text" in data:
                tasks = parse_legacy_text(data["raw_text"])
                for task in tasks:
                    self.add_row(
                        title=task.get("title", ""),
                        requester=task.get("requester", REQUESTER_NONE),
                        status=task.get("status", STATUS_PENDING),
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