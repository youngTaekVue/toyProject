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
        self.rest_api_key = rest_api_key
        self.token_file = token_file
        self.token_info = {}
        self.send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        self.friends_url = "https://kapi.kakao.com/v1/api/talk/friends"
        self.friend_send_url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        self.load_token()

    def load_token(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r", encoding='utf-8') as f:
                    self.token_info = json.load(f)
                return True
            except Exception:
                self.token_info = {}
        return False

    def save_token(self, token_data):
        for key, value in token_data.items():
            self.token_info[key] = value
        if "expires_in" in token_data:
            expire_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            self.token_info["access_token_expires_at"] = expire_at.isoformat()
        try:
            with open(self.token_file, "w", encoding='utf-8') as f:
                json.dump(self.token_info, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def issue_token(self, auth_code, redirect_uri):
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
                if self.save_token(res.json()):
                    return True, "토큰 발급 성공"
            return False, f"실패: {res.text}"
        except Exception as e:
            return False, str(e)

    def refresh_access_token(self):
        refresh_token = self.token_info.get("refresh_token")
        if not refresh_token or not self.rest_api_key: return False
        url = "https://kauth.kakao.com/oauth/token"
        data = {"grant_type": "refresh_token", "client_id": self.rest_api_key, "refresh_token": refresh_token}
        try:
            res = requests.post(url, data=data, verify=False)
            if res.status_code == 200:
                self.save_token(res.json())
                return True
            return False
        except Exception: return False

    def get_valid_headers(self):
        if not self.token_info.get("access_token"): return None
        # 만료 확인 (10분 전)
        exp = self.token_info.get("access_token_expires_at")
        if exp and datetime.now() >= (datetime.fromisoformat(exp) - timedelta(minutes=10)):
            if not self.refresh_access_token(): return None
        return {"Authorization": f"Bearer {self.token_info['access_token']}"}

    def get_friends(self):
        """메시지를 보낼 수 있는 친구 목록을 가져옵니다."""
        headers = self.get_valid_headers()
        if not headers: return None
        try:
            res = requests.get(self.friends_url, headers=headers, verify=False)
            if res.status_code == 200:
                return res.json().get('elements', [])
            print(f"친구 목록 조회 실패: {res.text}")
            return None
        except Exception as e:
            print(f"에러: {e}")
            return None

    def send_report(self, text):
        """나에게 전송"""
        headers = self.get_valid_headers()
        if not headers: return False, "인증 필요"
        template = {"object_type": "text", "text": text, "link": {"web_url": "http://localhost"}}
        try:
            payload = {'template_object': json.dumps(template, ensure_ascii=False)}
            res = requests.post(self.send_url, headers=headers, data=payload, verify=False)
            return res.status_code == 200, res.text
        except Exception as e: return False, str(e)

    def send_report_with_images(self, title, description, image_urls):
        """
        나에게 전송(이미지 포함).
        KakaoTalk Message REST API는 로컬 파일 첨부를 지원하지 않으므로,
        image_urls는 외부에서 접근 가능한 공개 URL이어야 합니다.
        """
        headers = self.get_valid_headers()
        if not headers:
            return False, "인증 필요"

        safe_urls = [u for u in (image_urls or []) if isinstance(u, str) and u.strip()]
        if not safe_urls:
            return False, "image_urls가 비어 있습니다(공개 URL 필요)"

        # list 템플릿으로 여러 이미지를 카드 형태로 전송
        contents = []
        for i, url in enumerate(safe_urls[:5]):  # 카카오 템플릿/화면상 과도한 길이 방지
            contents.append(
                {
                    "title": f"차트 {i+1}",
                    "description": "",
                    "image_url": url,
                    "image_width": 640,
                    "image_height": 640,
                    "link": {"web_url": "http://localhost"},
                }
            )

        template = {
            "object_type": "list",
            "header_title": title or "가계부 리포트",
            "header_link": {"web_url": "http://localhost"},
            "contents": contents,
            "buttons": [
                {"title": "열기", "link": {"web_url": "http://localhost"}},
            ],
        }

        # description은 list 템플릿 구조상 별도 영역이 없어 text 템플릿로 추가 전송(2회 전송)
        # - 1) 이미지 리스트
        try:
            payload = {"template_object": json.dumps(template, ensure_ascii=False)}
            res = requests.post(self.send_url, headers=headers, data=payload, verify=False)
            ok = res.status_code == 200
            if not ok:
                return False, res.text
        except Exception as e:
            return False, str(e)

        if description:
            self.send_report(description)
        return True, "OK"

    def send_to_friend(self, friend_uuid, text):
        """특정 친구(uuid)에게 전송"""
        headers = self.get_valid_headers()
        if not headers: return False, "인증 필요"
        template = {"object_type": "text", "text": text, "link": {"web_url": "http://localhost"}}
        try:
            payload = {
                'receiver_uuids': json.dumps([friend_uuid]),
                'template_object': json.dumps(template, ensure_ascii=False)
            }
            res = requests.post(self.friend_send_url, headers=headers, data=payload, verify=False)
            return res.status_code == 200, res.text
        except Exception as e: return False, str(e)
