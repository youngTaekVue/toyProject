import json
import requests
import os
import urllib3
from datetime import datetime, timedelta

# verify=False 사용 시 발생하는 InsecureRequestWarning 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KakaoNotifier:
    """카카오톡 메시지 전송 및 토큰 관리를 담당하는 클래스"""
    def __init__(self, rest_api_key=None, token_file="kakao_access_token_data.json"):
        # 실행 경로에 관계없이 프로젝트 루트 근처에 저장되도록 조정 가능
        # 여기서는 기본적으로 실행 위치 기준 또는 절대 경로를 사용할 수 있도록 함
        self.rest_api_key = rest_api_key
        self.token_file = token_file
        self.token_info = {}
        self.upload_url = "https://kapi.kakao.com/v1/storage/image"
        self.send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        self.load_token()

    def load_token(self):
        """파일에서 토큰 정보를 로드합니다."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r", encoding='utf-8') as f:
                    self.token_info = json.load(f)
                return True
            except Exception as e:
                print(f"토큰 로드 실패: {e}")
                self.token_info = {}
        return False

    def save_token(self, token_data):
        """새로 발급받거나 갱신된 토큰 정보를 저장합니다."""
        # 기존 정보 유지하면서 업데이트
        for key, value in token_data.items():
            self.token_info[key] = value

        # 액세스 토큰 만료 시간 계산 (현재 시간 + expires_in)
        if "expires_in" in token_data:
            expire_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            self.token_info["access_token_expires_at"] = expire_at.isoformat()

        # 리프레시 토큰 만료 시간 계산 (보통 2달, 있을 경우에만)
        if "refresh_token_expires_in" in token_data:
            refresh_expire_at = datetime.now() + timedelta(seconds=token_data["refresh_token_expires_in"])
            self.token_info["refresh_token_expires_at"] = refresh_expire_at.isoformat()

        try:
            with open(self.token_file, "w", encoding='utf-8') as f:
                json.dump(self.token_info, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"토큰 저장 실패: {e}")
            return False

    def issue_token(self, auth_code, redirect_uri):
        """인증 코드를 사용하여 최초 토큰을 발급받습니다."""
        if not self.rest_api_key:
            return False, "REST API KEY가 설정되지 않았습니다."

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.rest_api_key,
            "redirect_uri": redirect_uri,
            "code": auth_code
        }

        try:
            res = requests.post(url, data=data, verify=False)
            if res.status_code == 200:
                token_data = res.json()
                if self.save_token(token_data):
                    return True, "토큰 발급 및 저장 성공"
                return False, "토큰 저장 중 오류 발생"
            else:
                return False, f"토큰 발급 실패: {res.text}"
        except Exception as e:
            return False, f"토큰 발급 중 오류: {e}"

    def is_access_token_expired(self):
        """액세스 토큰이 만료되었는지 확인합니다."""
        if not self.token_info or "access_token_expires_at" not in self.token_info:
            return True
        
        expire_time = datetime.fromisoformat(self.token_info["access_token_expires_at"])
        # 안전하게 만료 10분 전부터 만료된 것으로 간주
        return datetime.now() >= (expire_time - timedelta(minutes=10))

    def refresh_access_token(self):
        """리프레시 토큰을 사용하여 액세스 토큰을 갱신합니다."""
        refresh_token = self.token_info.get("refresh_token")
        if not refresh_token or not self.rest_api_key:
            print("리프레시 토큰 또는 API 키가 없어 갱신할 수 없습니다.")
            return False

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": refresh_token
        }

        try:
            res = requests.post(url, data=data, verify=False)
            if res.status_code == 200:
                new_token_data = res.json()
                # 리프레시 토큰은 만료 기간이 1개월 미만일 때만 새로 내려옴
                self.save_token(new_token_data)
                print("액세스 토큰 자동 갱신 성공")
                return True
            else:
                print(f"토큰 갱신 실패: {res.text}")
                return False
        except Exception as e:
            print(f"토큰 갱신 중 오류: {e}")
            return False

    def get_valid_headers(self):
        """유효한 토큰 헤더를 반환하며, 필요시 자동 갱신합니다."""
        # 파일에서 로드 시도
        if not self.token_info:
            self.load_token()

        if not self.token_info.get("access_token"):
            return None

        # 만료 확인 및 갱신
        if self.is_access_token_expired():
            if not self.refresh_access_token():
                return None

        access_token = self.token_info.get("access_token")
        return {"Authorization": f"Bearer {access_token}"}

    def upload_image(self, image_path):
        """로컬 이미지를 카카오 서버에 업로드하고 URL을 반환"""
        headers = self.get_valid_headers()
        if not headers or not image_path or not os.path.exists(image_path):
            return None
        try:
            with open(image_path, 'rb') as f:
                res = requests.post(self.upload_url, headers=headers, files={'file': f}, verify=False, timeout=10)
            if res.status_code == 200:
                return res.json().get('infos', {}).get('original', {}).get('url')
            return None
        except Exception as e:
            print(f"이미지 업로드 실패: {e}")
            return None

    def send_report(self, text, image_url=None):
        """텍스트 또는 이미지 피드 메시지 전송"""
        headers = self.get_valid_headers()
        if not headers:
            return False, "유효한 토큰이 없으며 갱신에 실패했습니다. 다시 인증해주세요."

        if image_url:
            template = {
                "object_type": "feed",
                "content": {
                    "title": "가계부 월간 리포트",
                    "description": text,
                    "image_url": image_url,
                    "link": {"web_url": "http://localhost"}
                },
                "buttons": [{"title": "내역 보기", "link": {"web_url": "http://localhost"}}]
            }
        else:
            template = {
                "object_type": "text",
                "text": text,
                "link": {"web_url": "http://localhost"},
                "button_title": "내역 보기"
            }

        try:
            payload = {'template_object': json.dumps(template, ensure_ascii=False)}
            response = requests.post(self.send_url, headers=headers, data=payload, verify=False, timeout=10)

            if response.status_code != 200:
                error_data = response.json()
                # IP 화이트리스트 체크
                if error_data.get("code") == -401 and "ip mismatched" in error_data.get("msg", "").lower():
                    return False, f"IP 보안 설정 오류. 개발자 센터에 IP를 추가하세요."
                return False, f"API 오류: {response.text}"
            
            return True, "성공"
        except Exception as e:
            return False, f"네트워크 오류: {str(e)}"