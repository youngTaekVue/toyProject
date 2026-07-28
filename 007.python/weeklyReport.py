import os
import json
import re
import calendar
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------
# 데이터 저장 디렉토리 설정 및 설정 상수
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 사용자의 주간 계산 오프셋 (+7주)
WEEK_OFFSET = 7

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
    # ISO 주차를 구하기 위해 사용자 주차에서 오프셋을 뺍니다.
    iso_week = week - WEEK_OFFSET
    first_day = datetime(year, 1, 4)
    start_of_year = first_day - timedelta(days=first_day.weekday())
    target_monday = start_of_year + timedelta(weeks=iso_week-1)
    # 평일만 주간 범위로 표시하기 위해 금요일(월요일 + 4일)을 구합니다.
    target_friday = target_monday + timedelta(days=4)
    return f"{target_monday.strftime('%m.%d')} ~ {target_friday.strftime('%m.%d')}"

def get_monday_from_year_week(year, week):
    iso_week = week - WEEK_OFFSET
    first_day = datetime(year, 1, 4)
    start_of_year = first_day - timedelta(days=first_day.weekday())
    return start_of_year + timedelta(weeks=iso_week-1)

def parse_legacy_text(raw_text):
    # 레거시 단순 텍스트 데이터를 구조화된 딕셔너리 리스트로 마이그레이션 파싱
    if not raw_text.strip():
        return []
        
    blocks_raw = raw_text.split("\n\n")
    tasks = []
    
    for block in blocks_raw:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
            
        first_line = lines[0]
        # 앞단에 있을 수 있는 이전 버전 이모지 클렌징
        first_line = re.sub(r"^[✔⏳💤⏸]\s*", "", first_line)
        
        status = "선택 안함"
        # 대괄호 상태 태그 추출 ([콜요청], [청구 실패] 등)
        status_match = re.search(r"\[(콜요청|요청|청구\s*실패|완료|Done|진행중?|Doing|WIP|대기|Pending|To Do|준비|보류|Hold)\]", first_line, re.IGNORECASE)
        
        title = first_line
        if status_match:
            raw_status = status_match.group(1)
            # 상태 변환 매핑
            if raw_status in ["완료", "Done", "진행", "진행중", "Doing", "WIP", "대기", "Pending", "To Do", "준비", "보류", "Hold"]:
                status = "선택 안함"
            elif raw_status in ["청구 실패", "청구실패"]:
                status = "청구 실패"
            elif raw_status in ["콜요청", "전화요청"]:
                status = "콜요청"
            
            # 대괄호 태그 제외한 부분을 타이틀로 지정
            title = first_line.replace(status_match.group(0), "").strip()
            
        # 세부 설명 행 복원
        details_list = []
        for line in lines[1:]:
            cleaned_detail = re.sub(r"^[-*•]\s*", "", line)
            details_list.append(cleaned_detail)
            
        details = "\n".join(details_list)
        tasks.append({
            "title": title,
            "status": status,
            "details": details,
            "start_time": "",
            "end_date": ""
        })
        
    return tasks

# ----------------------------------------
# 콤팩트 달력 팝업 창 (추가 라이브러리 불필요)
# ----------------------------------------
class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, target_entry):
        super().__init__(parent)
        self.withdraw()  # 창 생성 후 즉시 숨겨서 위치 잡는 동안의 번쩍임(깜빡임) 방지
        self.target_entry = target_entry
        self.title("날짜 선택")
        
        # 부모 창의 위치와 크기 정보를 받아 정중앙 좌표 계산
        popup_w = 250
        popup_h = 240
        
        top_parent = parent.winfo_toplevel()
        top_parent.update_idletasks()  # 정확한 지오메트리 정보 로드 보장
        
        p_x = top_parent.winfo_x()
        p_y = top_parent.winfo_y()
        p_w = top_parent.winfo_width()
        p_h = top_parent.winfo_height()
        
        center_x = p_x + (p_w - popup_w) // 2
        center_y = p_y + (p_h - popup_h) // 2
        
        self.geometry(f"{popup_w}x{popup_h}+{center_x}+{center_y}")
        self.resizable(False, False)
        self.transient(top_parent)  # 항상 부모 창 레이어 상단에 노출
        self.grab_set()             # 부모 창 포커스 잠금 (모달 창)
        
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        
        self._setup_ui()
        self.deiconify()  # 위치 세팅이 완벽히 끝난 후 깔끔하게 노출
        
    def _setup_ui(self):
        # 상단 월 이동 바
        top_frame = ttk.Frame(self, padding=5)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="◀", width=3, command=self.prev_month).pack(side="left")
        self.lbl_month = ttk.Label(top_frame, text="", font=("Malgun Gothic", 10, "bold"))
        self.lbl_month.pack(side="left", expand=True)
        ttk.Button(top_frame, text="▶", width=3, command=self.next_month).pack(side="right")
        
        # 요일 헤더 라벨
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=2)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for d in days:
            lbl = ttk.Label(header_frame, text=d, width=4, anchor="center")
            lbl.pack(side="left", fill="x", expand=True)
            
        # 날짜 그리드 프레임
        self.grid_frame = ttk.Frame(self, padding=5)
        self.grid_frame.pack(fill="both", expand=True)
        
        self.draw_calendar()
        
    def draw_calendar(self):
        # 기존 버튼들 초기화
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        self.lbl_month.config(text=f"{self.current_year}년 {self.current_month}월")
        
        # 월별 달력 데이터 매트릭스 획득 (0은 공백일)
        cal = calendar.monthcalendar(self.current_year, self.current_month)
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
        # 최종 입력될 날짜 포맷 (예: 07.29)
        date_str = f"{self.current_month:02d}.{day:02d}"
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, date_str)
        self.target_entry.event_generate("<KeyRelease>")  # 텍스트 변경 이벤트 통보
        self.destroy()

# ----------------------------------------
# 개별 업무 입력 카드 (TaskCard)
# ----------------------------------------
class TaskCard(ttk.LabelFrame):
    def __init__(self, parent, container, on_change_callback, on_delete_callback, title="", status="선택 안함", details="", start_time="", end_date=""):
        super().__init__(container, text=" 📋 업무 ")
        self.parent = parent
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback
        
        self._setup_ui(title, status, details, start_time, end_date)
        
    def _setup_ui(self, title, status, details, start_time, end_date):
        # 카드 내부 패딩 프레임
        inner_frame = ttk.Frame(self, padding=8)
        inner_frame.pack(fill="both", expand=True)

        # ----------------------------------------
        # 1행: 요양기관명 입력 + 진행 상태 + 조작 버튼들
        # ----------------------------------------
        row1 = ttk.Frame(inner_frame)
        row1.pack(fill="x", pady=(0, 5))
        
        # 1) 요양기관명
        ttk.Label(row1, text="요양기관명").pack(side="left", padx=(0, 4))
        self.ent_title = ttk.Entry(row1)
        self.ent_title.pack(side="left", padx=3, fill="x", expand=True)
        self.ent_title.insert(0, title)
        self.ent_title.bind("<KeyRelease>", self.on_key_release)
        
        # 2) 진행 상태
        ttk.Label(row1, text="진행 상태").pack(side="left", padx=(8, 4))
        self.combo_status = ttk.Combobox(
            row1, 
            values=["선택 안함", "청구 실패", "콜요청"], 
            width=8, 
            state="readonly",
            justify="center"
        )
        self.combo_status.pack(side="left", padx=3)
        self.combo_status.set(status)
        self.combo_status.bind("<<ComboboxSelected>>", self.on_status_change)
        
        # 3) 조작 버튼 프레임 (위/아래/삭제 순서)
        self.op_frame = ttk.Frame(row1)
        self.op_frame.pack(side="right", padx=(10, 0))
        
        # tk.Button을 사용하여 컬러 이모지 렌더링 활성화 및 단정한 Flat 스타일 제공
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
        
        # ----------------------------------------
        # 2행: 시작일자 + 종료일자 입력 프레임
        # ----------------------------------------
        row2 = ttk.Frame(inner_frame)
        row2.pack(fill="x", pady=(0, 6))
        
        # 시작일자
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

        # 종료일자
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

        # ----------------------------------------
        # 3행: 상세 업무 내용 입력란
        # ----------------------------------------
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
        status = self.combo_status.get()
        details = self.txt_details.get("1.0", tk.END).strip()
        start_time = self.ent_start_time.get().strip()
        end_date = self.ent_end_date.get().strip()
        return {
            "title": title,
            "status": status,
            "details": details,
            "start_time": start_time,
            "end_date": end_date
        }
        
    def on_key_release(self, event=None):
        self.on_change_callback()
        
    def on_status_change(self, event=None):
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
        self.title("주간보고 작성기 📝")
        self.geometry("1300x720")  # 가로 및 세로 영역 넉넉하게 밸런싱
        self.minsize(1100, 550)

        today = datetime.now()
        self.current_monday = today - timedelta(days=today.weekday())
        self.update_year_week_from_monday()

        self.debounce_timer = None  # 디바운스 타이머
        self.rows = []  # 동적 TaskCard 리스트

        self._setup_ui()
        self.load_week_data()

    def _setup_ui(self):
        # 1. 상단 주차 선택 및 기능 바
        top_bar = ttk.Frame(self, padding=8, relief="groove")
        top_bar.pack(fill="x", side="top")

        # ➕ 업무 추가 버튼을 상단바 우측에 배치 (tk.Button을 통해 컬러 활성화)
        self.btn_add = tk.Button(
            top_bar, text="➕ 업무 추가", 
            command=self.add_empty_row,
            relief="flat", bd=0, cursor="hand2", bg="#F0F0F0",
            font=("Malgun Gothic", 9, "bold"), padx=5, pady=2
        )
        self.btn_add.pack(side="right", padx=5)

        # 상단 날짜 및 주차 선택기 중앙 정렬 (가운데 배치용 서브 프레임)
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

        # 2. 메인 2분할 레이아웃
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)  # 좌측 업무 카드 영역 (1:1 비율)
        main_frame.columnconfigure(1, weight=1)  # 우측 보고서 결과창 영역 (1:1 비율)
        main_frame.rowconfigure(0, weight=1)

        # [좌측] 업무 카드 등록 뷰
        left_box = ttk.Labelframe(main_frame, text=" 📋 업무 등록 및 편집 ", padding=10)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # 스크롤 Canvas 설정
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
        
        # 마우스 휠 이벤트 바인딩 연동 (마우스가 올라갔을 때만 활성화)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # [우측] 자동 변환 결과창
        right_box = ttk.Labelframe(main_frame, text=" 📋 실시간 정제 결과 ", padding=10)
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

        # 3. 최하단 버튼 바
        bottom_bar = ttk.Frame(self, padding=10)
        bottom_bar.pack(fill="x", side="bottom")

        ttk.Button(bottom_bar, text="💾 주간보고 저장", command=self.save_week_data).pack(side="left", padx=5)
        self.lbl_status = ttk.Label(bottom_bar, text="준비 완료", foreground="gray")
        self.lbl_status.pack(side="left", padx=10)

        ttk.Button(bottom_bar, text="📋 텍스트 복사", command=self.copy_to_clipboard).pack(side="right", padx=5)

    def _on_canvas_configure(self, event):
        # canvas의 width에 맞춰 내부 frame의 가로 길이를 꽉 차게 조절
        if hasattr(self, 'canvas_window') and self.canvas_window is not None:
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    # ----------------------------------------
    # 동적 카드(Card) 조작 메서드들
    # ----------------------------------------
    def add_empty_row(self):
        self.add_row()
        self.debounced_convert()
        
    def add_row(self, title="", status="선택 안함", details="", start_time="", end_date=""):
        card = TaskCard(
            self,
            self.scrollable_frame,
            on_change_callback=self.debounced_convert,
            on_delete_callback=self.remove_row,
            title=title,
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
        self.debounced_convert()
        
    def clear_rows(self):
        for row in self.rows:
            row.destroy()
        self.rows = []

    def repack_cards(self):
        # 카드 팩 해제 후 리스트 순서에 맞게 순차 재팩킹 & 넘버 라벨링 동기화
        for card in self.rows:
            card.pack_forget()
        for idx, card in enumerate(self.rows, 1):
            card.pack(fill="x", pady=6, padx=5)
            card.update_label(idx)
            
        # 스크롤 영역 강제 갱신
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def move_row_up(self, row_obj):
        idx = self.rows.index(row_obj)
        if idx > 0:
            # 리스트 상에서 스왑
            self.rows[idx], self.rows[idx-1] = self.rows[idx-1], self.rows[idx]
            self.repack_cards()
            self.debounced_convert()
            
    def move_row_down(self, row_obj):
        idx = self.rows.index(row_obj)
        if idx < len(self.rows) - 1:
            # 리스트 상에서 스왑
            self.rows[idx], self.rows[idx+1] = self.rows[idx+1], self.rows[idx]
            self.repack_cards()
            self.debounced_convert()

    # ----------------------------------------
    # 자동 보고서 변환 로직 (자동 순차 넘버링 적용)
    # ----------------------------------------
    def debounced_convert(self):
        if self.debounce_timer:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(300, self.auto_convert)

    def auto_convert(self):
        formatted_lines = []
        
        for idx, row in enumerate(self.rows, 1):
            data = row.get_data()
            title = data["title"]
            status = data["status"]
            details = data["details"]
            
            # 타이틀, 상태, 세부사항 모두 없으면 변환 스킵
            if not title and (status == "선택 안함" or not status) and not details:
                continue
                
            # 사용자가 기존 타이틀에 적어둔 번호 패턴(예: "6.", "6)")을 정규식으로 안전하게 지움
            cleaned_title = re.sub(r"^(\d+[\.\)]\s*)", "", title.strip())
            
            # 자동으로 순차적 넘버링 적용 (idx.)
            line_title = f"{idx}. {cleaned_title}"
            if status and status != "선택 안함":
                line_title = f"{idx}. {cleaned_title}[{status}]"
                
            formatted_lines.append(line_title)
            
            # 하위 상세 사항 인덴트 포맷팅
            if details:
                detail_lines = details.splitlines()
                for d_line in detail_lines:
                    if d_line.strip():
                        formatted_lines.append(f"        - {d_line.strip()}")
                        
            # 가독성을 위해 개별 업무 사이에 한 줄의 공백 추가
            formatted_lines.append("")
            
        # 마지막 공백 한 줄 제거
        if formatted_lines and formatted_lines[-1] == "":
            formatted_lines.pop()
            
        final_text = "\n".join(formatted_lines)
        
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, final_text)

    # ----------------------------------------
    # 데이터 제어 (불러오기 / 저장)
    # ----------------------------------------
    def load_week_data(self):
        week_str = get_week_range_str(self.year, self.week)
        self.lbl_week_title.config(text=f"🗓️ {self.year}년 {self.week}주차 ({week_str})")

        if hasattr(self, 'combo_year') and hasattr(self, 'combo_week'):
            self.combo_year.set(str(self.year))
            self.combo_week.set(f"{self.week:02d}")

        self.clear_rows()
        data = load_report_data(self.year, self.week)
        
        if data:
            # 1. 신규 포맷(구조화 데이터) 복원
            if "tasks" in data:
                tasks = data["tasks"]
                for task in tasks:
                    self.add_row(
                        title=task.get("title", ""),
                        status=task.get("status", "선택 안함"),
                        details=task.get("details", ""),
                        start_time=task.get("start_time", ""),
                        end_date=task.get("end_date", "")
                    )
            # 2. 레거시 텍스트 로드 시 자동 마이그레이션 적용
            elif "raw_text" in data:
                tasks = parse_legacy_text(data["raw_text"])
                for task in tasks:
                    self.add_row(
                        title=task.get("title", ""),
                        status=task.get("status", "선택 안함"),
                        details=task.get("details", ""),
                        start_time="",
                        end_date=""
                    )
        
        # 저장된 데이터가 전혀 없으면 기본 빈 카드 1개 제공
        if not self.rows:
            self.add_row()
            
        self.debounced_convert()
        self.lbl_status.config(text="데이터를 불러왔습니다.")

    def save_week_data(self):
        # 구조화 리스트 추출
        tasks = []
        for row in self.rows:
            data = row.get_data()
            # 비어있는 카드 제외
            if not data["title"] and (data["status"] == "선택 안함") and not data["details"] and not data["start_time"] and not data["end_date"]:
                continue
            tasks.append(data)
            
        formatted_text = self.txt_output.get("1.0", tk.END).strip()
        
        # JSON 구조화 파일 및 복사용 TXT 파일 이중 저장
        if save_report_data(self.year, self.week, tasks, formatted_text):
            self.lbl_status.config(text="주간보고가 저장되었습니다.")
            messagebox.showinfo("저장 완료", "주간보고가 정상적으로 저장되었습니다.")

    # ----------------------------------------
    # 이벤트 핸들러 및 날짜 점프
    # ----------------------------------------
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
        # 마우스가 좌측 영역에 들어왔을 때만 휠 스크롤 바인딩 활성화
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbind_mousewheel(self, event=None):
        # 영역을 벗어나면 바인딩 해제
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        # 캔버스 휠 스크롤 제어
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":
    app = NativeWeeklyReportApp()
    app.mainloop()