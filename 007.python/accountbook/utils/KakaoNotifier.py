import json
import requests
import os
import urllib3
from datetime import datetime, timedelta

# verify=False 사용 시 발생하는 InsecureRequestWarning 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KakaoNotifier:
    """카카오톡 메시지 전송 및 이미지 업로드를 담당하는 전용 클래스"""
    def __init__(self, rest_api_key=None):
        self.rest_api_key = rest_api_key
        self.token_file = "kakao_access_token_data.json"
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
            except Exception as e:
                print(f"토큰 로드 실패: {e}")
                self.token_info = {}

    def save_token(self, token_data):
        """새로 발급받거나 갱신된 토큰 정보를 저장합니다."""
        self.token_info.update(token_data)
        # 만료 시간 계산 (현재 시간 + expires_in)
        if "expires_in" in token_data:
            self.token_info["expires_at"] = (datetime.now() + timedelta(seconds=token_data["expires_in"])).isoformat()

        try:
            with open(self.token_file, "w", encoding='utf-8') as f:
                json.dump(self.token_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"토큰 저장 실패: {e}")

    def is_token_expired(self):
        """액세스 토큰이 만료되었는지 확인합니다."""
        if not self.token_info or "expires_at" not in self.token_info:
            return True
        expire_time = datetime.fromisoformat(self.token_info["expires_at"])
        # 안전하게 만료 5분 전부터 만료된 것으로 간주
        return datetime.now() >= (expire_time - timedelta(minutes=5))

    def refresh_access_token(self):
        """리프레시 토큰을 사용하여 액세스 토큰을 갱신합니다."""
        if not self.token_info.get("refresh_token") or not self.rest_api_key:
            return False

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": self.token_info["refresh_token"]
        }

        try:
            res = requests.post(url, data=data, verify=False)
            if res.status_code == 200:
                new_token_data = res.json()
                self.save_token(new_token_data)
                print("토큰 자동 갱신 성공")
                return True
            else:
                print(f"토큰 갱신 실패: {res.text}")
                return False
        except Exception as e:
            print(f"토큰 갱신 중 오류: {e}")
            return False

    def get_valid_headers(self):
        """유효한 토큰 헤더를 반환하며, 필요시 자동 갱신합니다."""
        if self.is_token_expired():
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
            return False, "유효한 토큰이 없으며 갱신에 실패했습니다."

        if image_url:
            template = {
                "object_type": "feed",
                "content": {
                    "title": "가계부 월간 리포트",
                    "description": text,
                    "image_url": image_url,  # 누락된 이미지 URL 추가
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

            # 상세 디버깅을 위해 응답 코드와 헤더 일부 출력
            if response.status_code == 401:
                print(f"DEBUG: 401 에러 발생 - 사용된 토큰: {self.access_token[:10]}...")

            if response.status_code != 200:
                error_data = response.json()
                if error_data.get("code") == -401 and "ip mismatched" in error_data.get("msg", ""):
                    print(f"\n[보안 설정 오류] 카카오 개발자 센터의 [앱 설정 > 보안 > IP 화이트리스트]에 현재 IP를 추가하거나 기능을 꺼주세요.")
                    print(f"현재 접속 IP (callerIp): {error_data.get('msg').split('=')[-1].split('.')[0] + '...'}\n")

                print(f"카카오 API 오류 응답: {response.text}")
            return response.status_code == 200, response.text
        except Exception as e:
            return False, f"네트워크 또는 요청 오류: {str(e)}"