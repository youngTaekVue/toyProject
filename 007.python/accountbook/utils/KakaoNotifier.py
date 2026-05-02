import json
import requests
import os
import urllib3
import webbrowser
from urllib.parse import urlencode
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

    def get_authorize_url(self, redirect_uri, scope=None, state=None):
        """
        카카오 OAuth 동의 페이지 URL을 생성합니다.
        - scope: "talk_message,friends" 같은 문자열 또는 ["talk_message","friends"] 형태
        """
        if not self.rest_api_key:
            return None
        q = {"client_id": self.rest_api_key, "redirect_uri": redirect_uri, "response_type": "code"}
        if scope:
            if isinstance(scope, (list, tuple, set)):
                q["scope"] = ",".join([str(s).strip() for s in scope if str(s).strip()])
            else:
                q["scope"] = str(scope).strip()
        if state:
            q["state"] = state
        return "https://kauth.kakao.com/oauth/authorize?" + urlencode(q)

    def open_authorize_page(self, redirect_uri, scope=None):
        """기본 브라우저로 인증 페이지를 엽니다."""
        url = self.get_authorize_url(redirect_uri, scope=scope)
        if not url:
            return False
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

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
            # refresh_token이 만료되었거나 무효한 경우가 대부분이라 재인증이 필요함
            return False
        except Exception: return False

    def _safe_json(self, res):
        try:
            return res.json()
        except Exception:
            return None

    def _needs_reauth(self, res):
        """
        카카오 API 응답을 보고 재인증이 필요한지 판단합니다.
        - 일반적으로 access token 만료/무효: 401
        - 권한(scope) 부족: 403 (insufficient_scope)
        """
        if res is None:
            return False
        if res.status_code in (401,):
            return True
        if res.status_code in (403,):
            body = self._safe_json(res) or {}
            msg = str(body.get("msg", "")).lower()
            code = body.get("code")
            # 다양한 형태의 메시지를 넓게 커버
            if "insufficient" in msg and "scope" in msg:
                return True
            if "insufficient_scope" in msg:
                return True
            # 일부 케이스는 code로만 내려올 수 있어 보수적으로 처리
            if code in (403, -403):
                return True
        return False

    def _error_message(self, res):
        if res is None:
            return "요청 실패"
        body = self._safe_json(res)
        if isinstance(body, dict) and (body.get("msg") or body.get("message")):
            msg = body.get("msg") or body.get("message")
            code = body.get("code")
            if code is not None:
                return f"{msg} (code={code})"
            return str(msg)
        return res.text

    def _request(self, method, url, headers=None, data=None, params=None):
        """카카오 API 호출 공통 래퍼. 재인증 필요 여부를 일관되게 처리합니다."""
        try:
            res = requests.request(method, url, headers=headers, data=data, params=params, verify=False)
        except Exception as e:
            return None, str(e)

        if res.status_code == 200:
            return res, None

        if self._needs_reauth(res):
            # access token이 무효하면 이후 로직에서도 혼동이 생겨 제거
            self.token_info.pop("access_token", None)
            return res, "인증 필요"

        return res, self._error_message(res)

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
        res, err = self._request("GET", self.friends_url, headers=headers)
        if err == "인증 필요":
            return None
        if not res:
            print(f"친구 목록 조회 실패: {err}")
            return None
        body = self._safe_json(res) or {}
        return body.get('elements', [])

    def send_report(self, text):
        """나에게 전송"""
        headers = self.get_valid_headers()
        if not headers: return False, "인증 필요"
        template = {"object_type": "text", "text": text, "link": {"web_url": "http://localhost"}}
        payload = {'template_object': json.dumps(template, ensure_ascii=False)}
        res, err = self._request("POST", self.send_url, headers=headers, data=payload)
        if err:
            return False, err
        return True, res.text

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
        payload = {"template_object": json.dumps(template, ensure_ascii=False)}
        res, err = self._request("POST", self.send_url, headers=headers, data=payload)
        if err:
            return False, err

        if description:
            self.send_report(description)
        return True, "OK"

    def send_to_friend(self, friend_uuid, text):
        """특정 친구(uuid)에게 전송"""
        headers = self.get_valid_headers()
        if not headers: return False, "인증 필요"
        template = {"object_type": "text", "text": text, "link": {"web_url": "http://localhost"}}
        payload = {
            'receiver_uuids': json.dumps([friend_uuid]),
            'template_object': json.dumps(template, ensure_ascii=False)
        }
        res, err = self._request("POST", self.friend_send_url, headers=headers, data=payload)
        if err:
            return False, err
        return True, res.text
