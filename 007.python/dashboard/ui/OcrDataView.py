import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import easyocr
from PIL import Image
import numpy as np
import ssl
import re
import cv2

class OcrDataView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.reader = None  # Lazy loading for OCR reader
        self.extracted_data = []
        self.setup_ui()

    def setup_ui(self):
        # 상단 컨트롤 영역
        ctrl_frame = ttk.LabelFrame(self, text="OCR 작업 제어", padding=10)
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        btn_upload = ttk.Button(ctrl_frame, text="이미지 업로드 및 분석", command=self.start_ocr_thread)
        btn_upload.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(ctrl_frame, orient="horizontal", mode="indeterminate", length=200)
        self.lbl_status = ttk.Label(ctrl_frame, text="대기 중...")
        self.lbl_status.pack(side="right", padx=5)

        # 1. 추출된 텍스트 확인 영역 (OCR 엔진의 성능을 확인하는 곳)
        raw_text_frame = ttk.LabelFrame(self, text="[Step 1] OCR 분석 결과 (Raw Text)", padding=10)
        raw_text_frame.pack(fill="x", padx=10, pady=5)

        self.txt_raw_output = tk.Text(raw_text_frame, height=8, font=("나눔고딕코딩", 11), bg="#f8f9fa")
        self.txt_raw_output.pack(side="left", fill="x", expand=True)
        
        raw_scroll = ttk.Scrollbar(raw_text_frame, orient="vertical", command=self.txt_raw_output.yview)
        self.txt_raw_output.configure(yscroll=raw_scroll.set)
        raw_scroll.pack(side="right", fill="y")

        # 데이터 표시 영역 (Treeview)
        table_frame = ttk.LabelFrame(self, text="[Step 2] 정형 데이터 확인 및 수정 (4개 단위 자동 분류)", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("inst_code", "base_id", "name", "rrn")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("inst_code", text="요양기관")
        self.tree.heading("base_id", text="환자번호(기준)")
        self.tree.heading("name", text="성함")
        self.tree.heading("rrn", text="주민등록번호")
        
        self.tree.column("inst_code", width=100)
        self.tree.column("base_id", width=120)
        self.tree.column("name", width=80)
        self.tree.column("rrn", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_item_double_click) # 더블클릭 수정 기능

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 하단 번호 생성 및 등록 영역
        action_frame = ttk.LabelFrame(self, text="[Step 3] 환자번호 자동 생성 및 전송", padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(action_frame, text="등록할 인원수:").pack(side="left", padx=5)
        self.ent_count = ttk.Entry(action_frame, width=5)
        self.ent_count.insert(0, "1")
        self.ent_count.pack(side="left", padx=5)

        btn_generate = ttk.Button(action_frame, text="번호 미리보기/생성", command=self.preview_ids)
        btn_generate.pack(side="left", padx=5)

        btn_submit = ttk.Button(action_frame, text="서버 일괄 등록", command=self.batch_submit)
        btn_submit.pack(side="right", padx=5)

    def start_ocr_thread(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return

        self.progress.pack(side="right", padx=10)
        self.progress.start()
        self.lbl_status.config(text="텍스트 분석 중...")
        
        # OCR은 무거운 작업이므로 스레드에서 실행
        threading.Thread(target=self.run_ocr, args=(file_path,), daemon=True).start()

    def run_ocr(self, file_path):
        try:
            # Reader 초기화 시 다운로드 상황을 알림
            if self.reader is None:
                # SSL 인증서 검증 오류 해결을 위한 코드 추가
                ssl._create_default_https_context = ssl._create_unverified_context
                
                print("INFO: OCR 모델을 초기화 중입니다. (첫 실행 시 다운로드로 인해 시간이 소요될 수 있습니다...)")
                self.reader = easyocr.Reader(['ko', 'en'])
                print("INFO: OCR 모델 초기화 완료.")
            
            # 1. 이미지 로드 (PIL -> Numpy)
            img = Image.open(file_path)
            img_np = np.array(img)
            
            # 한글 경로 및 채널 문제 방지를 위해 RGB -> BGR 변환 (OpenCV 표준)
            if len(img_np.shape) == 3:
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_np

            # 2. 정확도 향상을 위한 OpenCV 전처리
            # [A] 이미지 크기 확대 (해상도가 낮을 경우 인식률 저하의 주원인)
            h, w = img_cv.shape[:2]
            img_resized = cv2.resize(img_cv, (w*2, h*2), interpolation=cv2.INTER_CUBIC)

            # [B] 그레이스케일 변환
            gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

            # [C] 대비 강화 (CLAHE - 대비가 낮은 문서에서 매우 효과적)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast = clahe.apply(gray)

            # [D] 노이즈 제거 (엣지는 보존하면서 디테일 노이즈 제거)
            denoised = cv2.fastNlMeansDenoising(contrast, h=10)

            # 3. OCR 실행 (detail=0은 텍스트만, 1은 좌표와 신뢰도 포함)
            # 딥러닝 기반 모델은 너무 강한 이진화보다 선명한 그레이스케일을 선호합니다.
            results = self.reader.readtext(denoised, detail=0)
            
            # UI 업데이트는 메인 스레드에서 수행
            self.after(0, self.process_ocr_results, results)
        except Exception as e:
            print(f"ERROR: OCR 처리 중 오류 발생: {e}")
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: messagebox.showerror("OCR 오류", msg))
        finally:
            self.after(0, self.stop_loading)

    def stop_loading(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.lbl_status.config(text="분석 완료")

    def process_ocr_results(self, text_list):
        """
        앵커 키워드(성함/이름)를 기준으로 주변 인덱스에서 데이터를 Get 하는 로직
        """
        print(f"DEBUG: OCR Raw Result -> {text_list}")

        # 1. 원본 텍스트 영역 업데이트
        self.txt_raw_output.delete("1.0", tk.END)
        if text_list:
            header = f"--- OCR 분석 결과 (총 {len(text_list)}개 블록) ---\n"
            display_text = "\n".join([f"Line {i+1}: {text}" for i, text in enumerate(text_list)])
            self.txt_raw_output.insert(tk.END, header + display_text)
            self.txt_raw_output.see(tk.END)
        else:
            self.txt_raw_output.insert(tk.END, "추출된 텍스트가 없습니다.")

        # 2. 테이블 데이터 업데이트
        self.tree.delete(*self.tree.get_children())

        # 추출 설정 및 패턴
        anchors = ["성함", "이름", "내 용", "성명", "Name", "고객명"]
        rrn_pattern = re.compile(r'\d{6}-?\d{7}')
        # 환자번호 또는 휴대폰 번호 패턴 (8~11자리 숫자)
        id_pattern = re.compile(r'(?:010-?\d{3,4}-?\d{4}|\d{8,11})')
        found_count = 0

        i = 0
        while i < len(text_list):
            line_raw = text_list[i].strip()
            line_clean = line_raw.replace(" ", "")

            # 1. 앵커(기준점) 찾기
            match_anchor = next((a for a in anchors if a in line_clean), None)
            
            if match_anchor:
                name, pid, rrn = "", "", ""
                
                # [필드 1: 성함 추출]
                # '성함:홍길동' 처럼 붙어있는 경우 처리
                name_part = line_raw.split(match_anchor)[-1].replace(":", "").strip()
                
                if len(name_part) >= 2:
                    name = name_part
                    next_search_idx = i + 1
                elif i + 1 < len(text_list):
                    # 다음 인덱스 자체가 이름인 경우
                    name = text_list[i+1].strip()
                    next_search_idx = i + 2
                else:
                    next_search_idx = i + 1

                # 성함 정제 (기호 제거)
                name = re.sub(r'[^가-힣a-zA-Z]', '', name)

                # [필드 2 & 3: 성함 이후 인덱스들에서 PID와 RRN 추출]
                # 이름이 나온 이후의 인덱스들을 하나씩 검사하며 필드에 할당
                for j in range(next_search_idx, min(next_search_idx + 3, len(text_list))):
                    val = text_list[j].strip().replace('O', '0').replace('o', '0').replace('D', '0').replace('I', '1').replace('l', '1')
                    
                    # 이미 찾지 못한 필드에 대해서만 패턴 매칭 시도
                    if not rrn and rrn_pattern.search(val):
                        rrn = rrn_pattern.search(val).group()
                    elif not pid and id_pattern.search(val):
                        pid = id_pattern.search(val).group()

                # 추출된 필드가 하나라도 있다면 테이블에 추가
                if name or pid or rrn:
                    self.tree.insert("", "end", values=("", pid, name, rrn))
                    found_count += 1
                    # 이름 이후에 검사한 필드만큼 인덱스 건너뛰기 (중복 방지)
                    i = next_search_idx + 1
                    continue

            i += 1

        if found_count == 0:
            self.lbl_status.config(text="데이터 자동 분류 실패 (수동 수정 필요)")
        else:
            self.lbl_status.config(text=f"분석 완료: {found_count}건 추출됨")

    def advanced_data_get(self, text_list):
        """
        추가적인 팁: 데이터 유효성 검사 및 정교한 GET 방식
        """
        results = []
        # 텍스트 리스트를 순회하며 각 줄에 대한 가중치 부여
        for line in text_list:
            entry = {"pid": "", "name": "", "rrn": ""}
            
            # 1. 주민번호 GET (가장 확실한 패턴)
            rrn_match = re.search(r'\d{6}-?\d{7}', line.replace('O', '0'))
            if rrn_match:
                entry["rrn"] = rrn_match.group()
                line = line.replace(entry["rrn"], "") # 찾은건 지움
            
            # 2. 성함 GET (주민번호를 지우고 남은 한글 중 가장 긴 것)
            names = re.findall(r'[가-힣]+', line)
            if names:
                entry["name"] = max(names, key=len)
                line = line.replace(entry["name"], "")
            
            # 3. 환자번호 GET (나머지 숫자 중 8자리 이상)
            id_match = re.search(r'\d{8,}', line.replace('O', '0'))
            if id_match:
                entry["pid"] = id_match.group()
            
            if entry["rrn"] or entry["pid"]: # 최소한 정보가 하나라도 있으면 추가
                results.append(entry)
        return results

    def on_item_double_click(self, event):
        """테이블 셀 더블 클릭 시 해당 위치에 입력창 표시 (인라인 수정)"""
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item_id or not column:
            return

        # 셀의 좌표 및 크기 계산 (x, y, width, height)
        bbox = self.tree.bbox(item_id, column)
        if not bbox:
            return
        x, y, w, h = bbox

        # 열 인덱스 추출 (#1, #2... -> 0, 1...)
        col_idx = int(column.replace('#', '')) - 1
        current_values = list(self.tree.item(item_id, "values"))

        # 인라인 수정을 위한 Entry 생성
        # Treeview를 부모로 하여 정확한 좌표에 배치
        entry = ttk.Entry(self.tree)
        entry.insert(0, current_values[col_idx])
        entry.select_range(0, tk.END) # 전체 선택 상태로 시작
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()

        def save_edit(event=None):
            # 위젯이 존재하는 경우에만 저장 로직 수행 (중복 실행 방지)
            if entry.winfo_exists():
                new_val = entry.get()
                current_values[col_idx] = new_val
                self.tree.item(item_id, values=current_values)
                entry.destroy()

        # 엔터키를 누르거나, 다른 곳을 클릭하여 포커스를 잃어도 저장되도록 설정
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        
        # ESC 키를 누를 때만 저장을 취소하고 닫기
        entry.bind("<Escape>", lambda e: entry.destroy())

    def preview_ids(self):
        """환자번호 증가 로직 적용 미리보기"""
        selected = self.tree.get_children()
        if not selected:
            messagebox.showwarning("경고", "분석된 데이터가 없습니다.")
            return

        try:
            count = int(self.ent_count.get())
            base_row = self.tree.item(selected[0], "values")
            base_id_str = base_row[1]
            
            # 번호 증가 로직
            start_val = int(base_id_str)
            id_length = len(base_id_str)
            
            generated = []
            for i in range(count):
                new_id = str(start_val + i).zfill(id_length)
                generated.append(new_id)
            
            messagebox.showinfo("생성 예시", f"시작번호: {base_id_str}\n끝번호: {generated[-1]}\n총 {count}건 생성 준비 완료")
            self.generated_ids = generated
        except ValueError:
            messagebox.showerror("오류", "인원수 또는 환자번호 형식이 올바르지 않습니다.")

    def batch_submit(self):
        """일괄 전송 로직"""
        selected = self.tree.get_children()
        if not selected: return
        
        if not hasattr(self, 'generated_ids'):
            messagebox.showwarning("알림", "번호 미리보기를 먼저 수행해주세요.")
            return

        # 최종 데이터 구성
        base_info = self.tree.item(selected[0], "values")
        final_payload = []
        
        for g_id in self.generated_ids:
            final_payload.append({
                "hosp_code": base_info[0],
                "pt_no": g_id,
                "name": base_info[2],
                "rrn": base_info[3]
            })

        # 실제 API 호출 로직 (Mock)
        print(f"--- API 호출 (총 {len(final_payload)}건) ---")
        for item in final_payload:
            print(f"등록 요청: {item}")
        
        messagebox.showinfo("완료", f"{len(final_payload)}건의 환자가 성공적으로 등록되었습니다.")
        # 등록 후 초기화
        self.tree.delete(*self.tree.get_children())
        delattr(self, 'generated_ids')