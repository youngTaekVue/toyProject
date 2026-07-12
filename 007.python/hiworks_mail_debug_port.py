import time
import json
import os

# =========================================================================
# [디버깅 포트 모드] 이미 켜져 있는 크롬 브라우저를 파이썬으로 제어하기
# =========================================================================
# * 작동 원리: 
#   사용자가 디버깅 포트(8080)로 실행한 크롬 브라우저에 파이썬이 접속하여,
#   네이버 메일 쓰기 팝업 창(popup/new)을 병원 갯수만큼 "독립된 새 창"으로 직접 띄우고
#   각 창마다 데이터를 주입해 줍니다.
# =========================================================================

def open_and_fill_multiple_popup_windows(hospitals_data, service="naver", hiworks_domain="", other_domain=""):
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("❌ [패키지 누락] selenium 패키지가 설치되어 있지 않습니다.")
        print("💡 터미널에 'pip install selenium'을 실행해 주세요.")
        return

    # 이미 켜져 있는 크롬 디버깅 포트(8080)에 연결하기 위한 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:8080")
    
    try:
        print("[Python] 켜져 있는 크롬 브라우저(Port 8080)에 연결을 시도합니다...")
        driver = webdriver.Chrome(options=options)
        print("✅ 크롬 브라우저 연결 성공!")
    except Exception as e:
        print("❌ [연결 실패] 8080 포트로 켜진 크롬 브라우저를 찾을 수 없습니다.")
        print("💡 팁: 크롬을 완전히 종료한 후, 디버깅 명령어로 크롬을 먼저 실행해 주세요.")
        print(f"상세 에러: {e}")
        return

    # 하이웍스 도메인 동적 자동 감지 (사용자가 이미 열어둔 하이웍스 탭이 있다면 회사 오피스 도메인을 자동으로 감지해 옵니다)
    detected_hiworks_domain = hiworks_domain
    if not detected_hiworks_domain or "회사도메인" in detected_hiworks_domain:
        original_window = driver.current_window_handle
        for handle in driver.window_handles:
            try:
                driver.switch_to.window(handle)
                curr_url = driver.current_url
                if "mails.office.hiworks.com" in curr_url:
                    detected_hiworks_domain = "https://mails.office.hiworks.com"
                    print(f"🔍 [하이웍스 감지 성공] 신형 메일 플랫폼 감지: {detected_hiworks_domain}")
                    break
                elif "office.hiworks.com" in curr_url:
                    parts = curr_url.split('/')
                    if len(parts) >= 4:
                        detected_hiworks_domain = "/".join(parts[:4])
                        print(f"🔍 [하이웍스 감지 성공] 구형 오피스 플랫폼 감지: {detected_hiworks_domain}")
                        break
            except Exception:
                pass
        driver.switch_to.window(original_window)

    print(f"\n🚀 총 {len(hospitals_data)}개의 독립된 메일 작성 [팝업 창]을 생성하고 내용을 주입합니다.")
    
    for idx, hosp in enumerate(hospitals_data):
        # 1) 개별 데이터에 지정된 서비스('naver' 또는 'hiworks') 확인
        item_service = hosp.get('service', service)
        
        if item_service == "naver":
            write_url = "https://mail.naver.com/v2/popup/new"
            open_script = f"window.open('{write_url}', '_blank', 'width=1100,height=750,scrollbars=yes,resizable=yes');"
        elif item_service == "hiworks":
            # 자동 감지된 도메인이 있다면 그것을 쓰고, 정 없다면 가비아 통합 메일 기본 주소(mails.office.hiworks.com)로 폴백 처리
            h_domain = hosp.get('hiworks_domain', detected_hiworks_domain)
            if not h_domain or "회사도메인" in h_domain:
                h_domain = "https://mails.office.hiworks.com"
                
            # 신형 메일 플랫폼(mails.)과 구형 오피스 플랫폼(office.)의 쓰기 URL 차별화 적용
            if "mails.office.hiworks.com" in h_domain:
                write_url = f"{h_domain}/write?mode=normal"
            else:
                write_url = f"{h_domain}/mail/write/"
                
            # 하이웍스는 별도의 독립된 팝업 쓰기 모드가 없으므로, 새 탭(_blank)으로 넓게 엽니다.
            open_script = f"window.open('{write_url}', '_blank');"
        elif item_service == "other":
            write_url = hosp.get('other_domain', other_domain) or "https://mail.example.com"
            open_script = f"window.open('{write_url}', '_blank');"
        else:
            print(f"❌ [{hosp['hospital']}] 알 수 없는 이메일 서비스 타입입니다: {item_service}")
            continue

        print(f"\n📂 [{idx + 1}/{len(hospitals_data)}] {hosp['hospital']} 팝업 창 띄우는 중 (서비스: {item_service})...")
        
        # 2. 자바스크립트를 이용해 규격화된 독립된 새 창(Popup Window) 실행
        driver.execute_script(open_script)
        
        # 3. 새로 열린 창으로 제어권 포커스 이동
        driver.switch_to.window(driver.window_handles[-1])
        
        # 주소창 로딩 대기
        time.sleep(1.2)
        
        try:
            # 4. 받는 사람 / 제목 / HTML 본문 입력
            if item_service == "naver":
                # [네이버 받는사람 입력]
                to_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='recipient_input_element'] | //textarea[contains(@placeholder, '받는 사람')] | //input[contains(@placeholder, '받는 사람')] | //textarea[contains(@placeholder, '받는사람')]"))
                )
                if hosp.get('to') and hosp['to'].strip():
                    to_input.clear()
                    to_input.send_keys(hosp['to'])
                    to_input.send_keys("\n")  # 주소 확정 엔터
                
                # [네이버 제목 입력]
                subject_input = driver.find_element(By.XPATH, "//*[@id='subject_title'] | //input[contains(@placeholder, '제목')]")
                subject_input.clear()
                subject_input.send_keys(hosp['subject'])
                
                # [네이버 에디터 본문 주입 (HTML 탭 클릭 -> 코드 입력 -> Editor 복귀)]
                try:
                    # 1) [HTML] 버튼 클릭 (메인 페이지 또는 iframe 내부 자동 탐색)
                    html_btn_clicked = False
                    try:
                        html_btn = driver.find_element(By.XPATH, "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]")
                        html_btn.click()
                        html_btn_clicked = True
                        print("👉 [HTML] 버튼 클릭 성공 (메인 페이지)")
                    except Exception:
                        pass
                    
                    if not html_btn_clicked:
                        try:
                            editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                            driver.switch_to.frame(editor_iframe)
                            html_btn = driver.find_element(By.XPATH, "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]")
                            html_btn.click()
                            html_btn_clicked = True
                            print("👉 [HTML] 버튼 클릭 성공 (iframe 내부)")
                        except Exception as e:
                            print(f"❌ [HTML] 버튼을 찾을 수 없습니다: {e}")
                            driver.switch_to.default_content()
                            raise e

                    time.sleep(0.5) # 화면 전환 대기
                    
                    # 2) HTML 소스 코드 입력창(textarea) 찾기 및 코드 입력
                    source_input_filled = False
                    
                    # 현재 컨텍스트(iframe 또는 메인)에서 탐색
                    try:
                        source_area = driver.find_element(By.XPATH, "//textarea[contains(@class, 'source')] | //textarea[contains(@class, 'editor')] | //textarea[@id='ir1'] | //textarea")
                        driver.execute_script("arguments[0].value = arguments[1];", source_area, hosp['html_body'])
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", source_area)
                        source_input_filled = True
                        print("👉 HTML 소스 코드 주입 완료")
                    except Exception:
                        pass
                    
                    # 실패 시 컨텍스트 전환하여 다시 탐색
                    if not source_input_filled:
                        try:
                            editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                            driver.switch_to.frame(editor_iframe)
                            source_area = driver.find_element(By.XPATH, "//textarea[contains(@class, 'source')] | //textarea[contains(@class, 'editor')] | //textarea[@id='ir1'] | //textarea")
                            driver.execute_script("arguments[0].value = arguments[1];", source_area, hosp['html_body'])
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", source_area)
                            source_input_filled = True
                            print("👉 HTML 소스 코드 주입 완료 (iframe 내부)")
                        except Exception:
                            driver.switch_to.default_content()
                            try:
                                source_area = driver.find_element(By.XPATH, "//textarea[contains(@class, 'source')] | //textarea[contains(@class, 'editor')] | //textarea[@id='ir1'] | //textarea")
                                driver.execute_script("arguments[0].value = arguments[1];", source_area, hosp['html_body'])
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", source_area)
                                source_input_filled = True
                                print("👉 HTML 소스 코드 주입 완료 (메인 페이지)")
                            except Exception as e:
                                print(f"❌ HTML 입력창(textarea)을 찾을 수 없습니다: {e}")
                                driver.switch_to.default_content()
                                raise e

                    time.sleep(0.5)
                    
                    # 3) [Editor] 또는 [에디터] 버튼 클릭하여 복귀
                    editor_btn_clicked = False
                    try:
                        editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                        editor_btn.click()
                        editor_btn_clicked = True
                        print("👉 [Editor] 버튼 클릭 성공 (현재 컨텍스트)")
                    except Exception:
                        pass
                    
                    if not editor_btn_clicked:
                        try:
                            driver.switch_to.default_content()
                            editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                            editor_btn.click()
                            editor_btn_clicked = True
                            print("👉 [Editor] 버튼 클릭 성공 (메인 페이지)")
                        except Exception:
                            try:
                                editor_iframe = driver.find_element(By.XPATH, "//div[contains(@class, 'workseditor')]//iframe | //iframe[1]")
                                driver.switch_to.frame(editor_iframe)
                                editor_btn = driver.find_element(By.XPATH, "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]")
                                editor_btn.click()
                                editor_btn_clicked = True
                                print("👉 [Editor] 버튼 클릭 성공 (iframe 내부)")
                            except Exception as e:
                                print(f"❌ [Editor] 버튼을 찾을 수 없습니다: {e}")
                    
                    # 복귀 완료 후 메인 컨텍스트로 전환
                    driver.switch_to.default_content()
                    print("👉 [성공] HTML 팝업 전환 주입 최종 성공!")
                except Exception as err:
                    print(f"❌ 네이버 HTML 팝업 전환 주입 실패: {err}")
                    driver.switch_to.default_content()
                
            elif item_service == "hiworks":
                # [하이웍스 받는사람 입력]
                # AddressInput_address-input__form__0Rse6 또는 input[placeholder*='구분하여 입력하세요']
                to_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='구분하여 입력하세요'], input[class*='AddressInput_address-input'], input[name='to'], #mail_to_input"))
                )
                if hosp.get('to') and hosp['to'].strip():
                    to_input.clear()
                    to_input.send_keys(hosp['to'])
                    to_input.send_keys("\n")  # 엔터를 눌러 이메일 주소 칩/태그 생성
                
                # [하이웍스 숨은참조 입력 (선택)]
                # 사용자 요청: fixedCc 주소를 '숨은참조' 칸에 넣도록 수정
                if hosp.get('cc'):
                    try:
                        # 1) 먼저 숨은참조 입력창이 현재 화면에 보이는지 검사
                        is_bcc_visible = False
                        bcc_input = None
                        try:
                            bcc_input = driver.find_element(By.XPATH, "//*[contains(text(), '숨은참조')]/ancestor::tr//input[contains(@class, 'AddressInput_address-input')] | //th[contains(., '숨은참조')]/..//input | //*[contains(text(), '숨은참조')]/..//input")
                            if bcc_input.is_displayed():
                                is_bcc_visible = True
                        except Exception:
                            pass
                        
                        # 2) 만약 보이지 않는다면, 우측의 '숨은참조' 버튼/링크를 클릭하여 입력칸을 활성화합니다.
                        if not is_bcc_visible:
                            try:
                                # 보통 메일 쓰기 화면 우측에 '숨은참조' 활성화 링크가 있습니다.
                                bcc_toggle = driver.find_element(By.XPATH, "//button[contains(., '숨은참조')] | //span[contains(., '숨은참조')] | //a[contains(., '숨은참조')]")
                                bcc_toggle.click()
                                time.sleep(0.3)
                            except Exception as toggle_err:
                                print(f"⚠️ 숨은참조 활성화 버튼 클릭 실패: {toggle_err}")
                        
                        # 3) 다시 한번 숨은참조 입력칸을 확실하게 조회합니다.
                        try:
                            bcc_input = driver.find_element(By.XPATH, "//*[contains(text(), '숨은참조')]/ancestor::tr//input[contains(@class, 'AddressInput_address-input')] | //th[contains(., '숨은참조')]/..//input | //*[contains(text(), '숨은참조')]/..//input")
                        except Exception:
                            pass
                            
                        # 4) 찾지 못했을 경우, 클래스로 탐색된 주소 입력칸들의 인덱스로 타겟팅 (To:0, CC:1, BCC:2)
                        if not bcc_input:
                            addr_inputs = driver.find_elements(By.CSS_SELECTOR, "input[class*='AddressInput_address-input']")
                            if len(addr_inputs) > 2:
                                bcc_input = addr_inputs[2]  # To, CC, BCC 모두 열려 있는 경우
                            elif len(addr_inputs) > 1:
                                # 만약 To와 하나의 칸만 보인다면, 그것이 숨은참조일 수 있음
                                bcc_input = addr_inputs[1]
                                
                        if bcc_input:
                            bcc_input.clear()
                            bcc_input.send_keys(hosp['cc'])
                            bcc_input.send_keys("\n")
                            print("👉 숨은참조(BCC) 입력 완료")
                        else:
                            print("⚠️ 숨은참조(BCC) 입력칸을 찾지 못했습니다.")
                    except Exception as cc_err:
                        print(f"⚠️ 숨은참조(BCC) 입력 실패: {cc_err}")
                
                # [하이웍스 제목 입력]
                # Input_input__cjFgv Input_input-right-padding__mbeO1
                subject_input = driver.find_element(By.CSS_SELECTOR, "input[class*='Input_input-right-padding'], input[class*='Input_input__'], input[name='subject'], #mail_subject_input")
                subject_input.clear()
                subject_input.send_keys(hosp['subject'])
                
                # [하이웍스 에디터 iframe 본문 주입]
                # iframe.se-contents-edit
                editor_iframe = driver.find_element(By.CSS_SELECTOR, "iframe.se-contents-edit, iframe[title='웹에디터'], iframe.editor-iframe")
                driver.switch_to.frame(editor_iframe)
                
                # JavaScript로 기존 서명(sign_body)을 보존하며 본문 맨 위에 HTML 표를 삽입
                injection_js = """
                var contentsDiv = document.querySelector('div.se-contents');
                var signBody = document.getElementById('sign_body');
                if (contentsDiv) {
                    var mailWrapper = document.createElement('div');
                    mailWrapper.innerHTML = arguments[0] + '<br>';
                    
                    if (signBody) {
                        // 서명(sign_body) 바로 앞에 HTML 표 삽입 (서명 보존!)
                        contentsDiv.insertBefore(mailWrapper, signBody);
                        
                        // 첫 번째 빈 단락(<p><br></p>)이 있으면 주입 후 불필요한 줄바꿈 방지를 위해 제거
                        var firstP = contentsDiv.querySelector('p');
                        if (firstP && firstP !== signBody && (firstP.innerHTML === '<br>' || firstP.textContent.trim() === '')) {
                            try { contentsDiv.removeChild(firstP); } catch(e) {}
                        }
                    } else {
                        // 서명이 없는 경우 그냥 맨 뒤에 추가
                        contentsDiv.appendChild(mailWrapper);
                    }
                    return true;
                }
                return false;
                """
                
                driver.execute_script(injection_js, hosp['html_body'])
                driver.switch_to.default_content()
                
            elif item_service == "other":
                # TODO: 기타 메일 서비스의 입력창 선택자(CSS Selector)를 입력하고 주입 로직을 활성화하세요
                print(f"👉 [기타 메일] 팝업창 주입 모드 (메일 주소: {hosp['to']})")
                # 아래는 구현을 돕기 위해 작성된 템플릿입니다. 사이트 구조에 맞게 수정하여 사용하세요.
                try:
                    # 1. 받는 사람 입력창
                    # to_input = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.address-input")))
                    # to_input.send_keys(hosp['to'])
                    
                    # 2. 제목 입력창
                    # subject_input = driver.find_element(By.CSS_SELECTOR, "input.subject-input")
                    # subject_input.send_keys(hosp['subject'])
                    
                    # 3. 본문 입력창
                    # editor_body = driver.find_element(By.CSS_SELECTOR, "div.editor-body")
                    # driver.execute_script("arguments[0].innerHTML = arguments[1];", editor_body, hosp['html_body'])
                    pass
                except Exception as other_err:
                    print(f"⚠️ 기타 메일 주입 중 오류: {other_err}")
                
            print(f"✅ [{hosp['hospital']}] 팝업창 주입 완료!")
            
        except Exception as e:
            print(f"❌ [{hosp['hospital']}] 데이터 주입 도중 에러 발생: {e}")
            driver.switch_to.default_content()
            
        # 브라우저 팝업 차단 및 안정성을 위해 짧게 대기
        time.sleep(1.5)

    print("\n🎉 모든 병원의 메일 팝업 창 생성 및 내용 주입이 완료되었습니다!")
    print("각 팝업 창을 확인하시고 [보내기] 버튼을 직접 눌러주세요.")


if __name__ == "__main__":
    # ⚠️ 테스트할 메일 서비스 선택 ("naver" 또는 "hiworks")
    MAIL_SERVICE_TYPE = "naver" 
    
    # 하이웍스를 선택할 경우 회사 전용 도메인 지정 필요 (예: https://office.hiworks.com/회사도메인)
    HIWORKS_OFFICE_DOMAIN = "https://office.hiworks.com/회사도메인"
    
    # 기타(Other) 메일 전송 시 사용할 기본 주소를 입력하세요
    OTHER_MAIL_URL = "https://mail.example.com"

    # ⚡ [백엔드 API 호환성: 임시 단일 전송 처리 전용]
    import sys
    temp_json_filename = "temp_single_mail.json"
    temp_json_path = os.path.join(os.path.dirname(__file__), temp_json_filename)
    
    if os.path.exists(temp_json_path) or "--temp" in sys.argv:
        try:
            with open(temp_json_path, "r", encoding="utf-8") as f:
                temp_list = json.load(f)
            try:
                os.remove(temp_json_path)
            except Exception:
                pass
            print(f"⚡ [Express API Trigger] 단일 메일 전송 데이터를 실행합니다: {len(temp_list)}건")
            open_and_fill_multiple_popup_windows(
                temp_list, 
                service=MAIL_SERVICE_TYPE, 
                hiworks_domain=HIWORKS_OFFICE_DOMAIN, 
                other_domain=OTHER_MAIL_URL
            )
            sys.exit(0)
        except Exception as temp_err:
            print(f"❌ 임시 데이터 처리 중 오류 발생: {temp_err}")
            sys.exit(1)
    else:
        print("\n❌ [실행 오류] 이 스크립트는 단독으로 실행할 수 없습니다.")
        print("💡 대시보드 웹사이트에서 [네이버 메일(8080) 전송] 버튼을 클릭해 실행해 주세요.")
        sys.exit(1)
