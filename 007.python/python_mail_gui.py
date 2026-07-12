import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import time
import threading

class MailDispatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Naver Mail Automation Controller")
        self.root.geometry("680x640")
        self.root.configure(bg="#f8fafc")
        
        self.json_filename = "hospitals_data.json"
        self.json_path = os.path.join(os.path.dirname(__file__), self.json_filename)
        self.hospitals_list = []
        
        # UI 스타일 지정
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#f8fafc", foreground="#334155", font=("맑은 고딕", 10))
        self.style.configure("TButton", font=("맑은 고딕", 10, "bold"), padding=6)
        
        self.setup_ui()
        self.load_json_data()

    def setup_ui(self):
        # 1. 상단 타이틀 영역
        title_frame = tk.Frame(self.root, bg="#1e3a8a", height=50)
        title_frame.pack(fill="x")
        title_label = tk.Label(title_frame, text="🏥 Naver Mail Automation Controller (Tkinter)", bg="#1e3a8a", fg="white", font=("맑은 고딕", 13, "bold"))
        title_label.pack(pady=10)

        # 2. 데이터 상태 표시 영역
        status_frame = ttk.LabelFrame(self.root, text=" 데이터 로드 현황 ")
        status_frame.pack(fill="x", padx=15, pady=10)
        
        self.lbl_status = ttk.Label(status_frame, text="로드된 병원 수: 0개 (대기 상태)", font=("맑은 고딕", 10, "bold"))
        self.lbl_status.pack(anchor="w", padx=10, pady=8)
        
        # 3. 갯수 및 범위 조절 프레임
        control_frame = ttk.LabelFrame(self.root, text=" 발송 범위 및 제한 설정 ")
        control_frame.pack(fill="x", padx=15, pady=5)

        # 그리드 레이아웃 구성
        control_grid = tk.Frame(control_frame, bg="#f8fafc")
        control_grid.pack(padx=10, pady=10, fill="x")

        # 시작 순번
        ttk.Label(control_grid, text="시작 병원 번호:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_start = ttk.Entry(control_grid, width=12)
        self.ent_start.insert(0, "1")
        self.ent_start.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # 띄울 개수
        ttk.Label(control_grid, text="한 번에 띄울 창 개수:").grid(row=0, column=2, sticky="w", pady=5)
        self.ent_limit = ttk.Entry(control_grid, width=12)
        self.ent_limit.insert(0, "5")
        self.ent_limit.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # 새로고침 버튼
        btn_refresh = ttk.Button(control_grid, text="🔄 데이터 새로고침", command=self.load_json_data)
        btn_refresh.grid(row=0, column=4, padx=15, pady=5, sticky="e")
        
        control_grid.columnconfigure(4, weight=1)

        # 4. 선택된 대상 정보 및 로그 뷰어
        log_frame = ttk.LabelFrame(self.root, text=" 실시간 실행 진행 로그 ")
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_log = tk.Text(log_frame, bg="#0f172a", fg="#38bdf8", insertbackground="white", font=("Consolas", 9), wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=8)

        # 5. 하단 액션 버튼 영역
        action_frame = tk.Frame(self.root, bg="#f8fafc")
        action_frame.pack(fill="x", pady=10)

        # 핵심 실행 버튼
        self.btn_run = tk.Button(
            action_frame, 
            text="🚀 선택한 범위 크롬 팝업창 열기 & 주입 시작", 
            bg="#0284c7", 
            fg="white", 
            activebackground="#0369a1",
            activeforeground="white",
            font=("맑은 고딕", 11, "bold"), 
            relief="flat",
            command=self.start_automation_thread
        )
        self.btn_run.pack(fill="x", padx=15, ipady=8)

    def log(self, message):
        """실시간 실행 상태 로그 뷰어 출력"""
        self.txt_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.txt_log.see(tk.END)

    def load_json_data(self):
        """hospitals_data.json 파일 읽기"""
        self.txt_log.delete("1.0", tk.END)
        if not os.path.exists(self.json_path):
            self.lbl_status.config(text="로드 실패: 'hospitals_data.json' 파일이 존재하지 않습니다.", foreground="#ef4444")
            self.log("❌ 'hospitals_data.json'을 찾을 수 없습니다. generate_mail_json.py를 먼저 실행해 주세요.")
            self.hospitals_list = []
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.hospitals_list = json.load(f)
            count = len(self.hospitals_list)
            self.lbl_status.config(text=f"로드 성공: 총 {count}개 병원 이메일 대기 중", foreground="#16a34a")
            self.log(f"✅ 'hospitals_data.json' 읽기 완료. 총 {count}개 병원 데이터 로드됨.")
        except Exception as e:
            self.lbl_status.config(text="로드 에러: JSON 파싱 도중 에러가 발생했습니다.", foreground="#ef4444")
            self.log(f"❌ JSON 파싱 에러: {e}")
            self.hospitals_list = []

    def start_automation_thread(self):
        """UI 프리징(멈춤 현상) 방지를 위해 백그라운드 스레드로 크롬 주입 작업을 시작합니다."""
        if not self.hospitals_list:
            messagebox.showwarning("경고", "먼저 로드된 병원 데이터가 있어야 합니다.")
            return

        # 입력값 확인
        try:
            start_num = int(self.ent_start.get().strip())
            limit = int(self.ent_limit.get().strip())
        except ValueError:
            messagebox.showerror("오류", "시작 번호와 창 개수는 정수 숫자로만 입력해 주세요.")
            return

        total = len(self.hospitals_list)
        start_idx = start_num - 1

        if start_idx < 0 or start_idx >= total:
            messagebox.showerror("오류", f"시작 번호는 1부터 {total} 사이의 숫자여야 합니다.")
            return
        
        if limit <= 0:
            messagebox.showerror("오류", "한 번에 띄울 창 개수는 1개 이상이어야 합니다.")
            return

        # 백그라운드 크롬 제어 스레드 구동
        self.btn_run.config(state="disabled", text="⏳ 크롬 브라우저 자동 제어 중...")
        automation_thread = threading.Thread(
            target=self.run_chrome_automation, 
            args=(start_idx, limit), 
            daemon=True
        )
        automation_thread.start()

    def run_chrome_automation(self, start_idx, limit):
        """실제 Selenium 브라우저 컨트롤 로직"""
        selected_data = self.hospitals_list[start_idx : start_idx + limit]
        self.log(f"🚀 {start_idx + 1}번부터 최대 {len(selected_data)}개 병원 팝업 주입 프로세스 시작")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            self.log("❌ 패키지 누락: selenium이 없습니다. 'pip install selenium'을 터미널에 쳐주세요.")
            self.root.after(0, self.reset_run_button)
            return

        # 이미 켜진 포트 8080 크롬 연동
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:8080")
        
        try:
            self.log("🔌 Port 8080 디버깅 크롬 브라우저와 통신 중...")
            driver = webdriver.Chrome(options=options)
        except Exception as conn_err:
            self.log(f"❌ 크롬 연결 실패: {conn_err}")
            self.log("💡 크롬창이 '--remote-debugging-port=8080' 설정으로 열려있는지 다시 체크바랍니다.")
            self.root.after(0, self.reset_run_button)
            return

        write_url = "https://mail.naver.com/v2/popup/new"
        open_script = f"window.open('{write_url}', '_blank', 'width=1100,height=750,scrollbars=yes,resizable=yes');"

        for idx, hosp in enumerate(selected_data):
            current_num = start_idx + idx + 1
            self.log(f"[{current_num}/{len(self.hospitals_list)}] {hosp['hospital']} 팝업 띄우기 요청")
            
            try:
                driver.execute_script(open_script)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(1.2) # 새 창 주소창 렌더링 대기
                
                # [받는사람 입력]
                to_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='recipient_input_element'] | //textarea[contains(@placeholder, '받는 사람')] | //input[contains(@placeholder, '받는 사람')] | //textarea[contains(@placeholder, '받는사람')]"))
                )
                to_input.clear()
                to_input.send_keys(hosp['to'])
                to_input.send_keys("\n")
                
                # [제목 입력]
                subject_input = driver.find_element(By.XPATH, "//*[@id='subject_title'] | //input[contains(@placeholder, '제목')]")
                subject_input.clear()
                subject_input.send_keys(hosp['subject'])
                
                # [에디터 본문 HTML 주입]
                html_btn_clicked = False
                try:
                    # 메인 페이지 검색
                    html_btn = driver.find_element(By.XPATH, "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]")
                    html_btn.click()
                    html_btn_clicked = True
                    self.log(f"   ㄴ [HTML] 탭 클릭완료 (메인)")
                except Exception:
                    pass
                
                if not html_btn_clicked:
                    try:
                        # iframe 내부 검색
                        editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                        driver.switch_to.frame(editor_iframe)
                        html_btn = driver.find_element(By.XPATH, "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]")
                        html_btn.click()
                        html_btn_clicked = True
                        self.log(f"   ㄴ [HTML] 탭 클릭완료 (iframe)")
                    except Exception as e:
                        self.log(f"   ㄴ ⚠️ [HTML] 버튼 클릭 실패: {e}")
                        driver.switch_to.default_content()
                        raise e
                
                time.sleep(0.5)

                # 소스 에리어 텍스트 주입
                source_input_filled = False
                try:
                    source_area = driver.find_element(By.XPATH, "//textarea[contains(@class, 'source')] | //textarea[contains(@class, 'editor')] | //textarea[@id='ir1'] | //textarea")
                    driver.execute_script("arguments[0].value = arguments[1];", source_area, hosp['html_body'])
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", source_area)
                    source_input_filled = True
                    self.log(f"   ㄴ 소스 코드 복사 성공")
                except Exception:
                    pass
                
                if not source_input_filled:
                    try:
                        editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                        driver.switch_to.frame(editor_iframe)
                        source_area = driver.find_element(By.XPATH, "//textarea[contains(@class, 'source')] | //textarea[contains(@class, 'editor')] | //textarea[@id='ir1'] | //textarea")
                        driver.execute_script("arguments[0].value = arguments[1];", source_area, hosp['html_body'])
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", source_area)
                        source_input_filled = True
                        self.log(f"   ㄴ 소스 코드 복사 성공 (iframe)")
                    except Exception as e:
                        self.log(f"   ㄴ ❌ 소스 코드 주입 최종 실패: {e}")
                        driver.switch_to.default_content()
                        raise e

                time.sleep(0.5)
                
                # [Editor] 복귀 클릭
                editor_btn_clicked = False
                try:
                    editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                    editor_btn.click()
                    editor_btn_clicked = True
                    self.log(f"   ㄴ [Editor] 전환 완료")
                except Exception:
                    pass
                
                if not editor_btn_clicked:
                    try:
                        driver.switch_to.default_content()
                        editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                        editor_btn.click()
                        editor_btn_clicked = True
                        self.log(f"   ㄴ [Editor] 전환 완료 (메인)")
                    except Exception:
                        try:
                            editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                            driver.switch_to.frame(editor_iframe)
                            editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                            editor_btn.click()
                            editor_btn_clicked = True
                            self.log(f"   ㄴ [Editor] 전환 완료 (iframe)")
                        except Exception as e:
                            self.log(f"   ㄴ ⚠️ [Editor] 버튼 클릭 실패: {e}")

                driver.switch_to.default_content()
                self.log(f"✅ {hosp['hospital']} 데이터 입력 성공!")
                
            except Exception as e:
                self.log(f"❌ {hosp['hospital']} 주입 실패: {e}")
                driver.switch_to.default_content()
            
            # 다음 팝업 생성 전 딜레이
            time.sleep(1.5)

        self.log("🎉 선택한 배치의 팝업 제어가 끝났습니다!")
        self.root.after(0, self.reset_run_button)

    def reset_run_button(self):
        """동작 완료 후 UI 활성화"""
        self.btn_run.config(state="normal", text="🚀 선택한 범위 크롬 팝업창 열기 & 주입 시작")

if __name__ == "__main__":
    root = tk.Tk()
    app = MailDispatcherApp(root)
    root.mainloop()
