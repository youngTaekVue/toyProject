import tkinter as tk
from tkinter import ttk
import requests
import threading
import urllib3

class TreatListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 데이터 초기화 (검색을 위해 멤버 변수로 저장)
        self.user_data = [
            {"id": 1, "treatCd": "01", "deptNm": "피부과", "startDt": "20250101", "endDt": "20250101", "billNo": "200", "prescriptionYn": "Y"},
            {"id": 2, "treatCd": "02", "deptNm": "외과", "startDt": "20250110", "endDt": "20250120", "billNo": "100", "prescriptionYn": "Y"},
            {"id": 3, "treatCd": "01", "deptNm": "미용과", "startDt": "20250201", "endDt": "20250201", "billNo": "400", "prescriptionYn": "N"},
            {"id": 4, "treatCd": "01", "deptNm": "산부인과", "startDt": "20251010", "endDt": "20251010", "billNo": "400", "prescriptionYn": "Y"},
            {"id": 5, "treatCd": "01", "deptNm": "검진", "startDt": "20251010", "endDt": "20251010", "billNo": "400", "prescriptionYn": "N"},
            {"id": 6, "treatCd": "02", "deptNm": "피부과", "startDt": "20251101", "endDt": "20251111", "billNo": "400", "prescriptionYn": "Y"},
            {"id": 7, "treatCd": "01", "deptNm": "내과", "startDt": "20251111", "endDt": "20251111", "billNo": "400", "prescriptionYn": "Y"},
            {"id": 8, "treatCd": "01", "deptNm": "알레르기과", "startDt": "20251201", "endDt": "20251201", "billNo": "400", "prescriptionYn": "Y"},
            {"id": 9, "treatCd": "01", "deptNm": "안과", "startDt": "20251201", "endDt": "20251201", "billNo": "400", "prescriptionYn": "N"},
            {"id": 10,"treatCd": "01", "deptNm": "이빈후과", "startDt": "20260101", "endDt": "20260101", "billNo": "400", "prescriptionYn": "Y"},
        ]
        self.setup_ui()

    def setup_ui(self):
        # 상단 프레임 (타이틀 + 검색창)
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=10, pady=(10, 0))

        lbl_header = ttk.Label(top_frame, text="전체 사용자 목록", font=("맑은 고딕", 14, "bold"))
        lbl_header.pack(side="left")

        # 검색 UI (오른쪽 정렬)
        ttk.Button(top_frame, text="조회", command=self.search_data).pack(side="right")
        ttk.Button(top_frame, text="API 호출", command=self.call_api).pack(side="right", padx=5)
        self.ent_search = ttk.Entry(top_frame, width=20)
        self.ent_search.pack(side="right", padx=5)
        self.ent_search.bind("<Return>", lambda event: self.search_data()) # 엔터키로도 조회 가능
        ttk.Label(top_frame, text="검색:").pack(side="right")


        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ("id", "treatCd", "deptNm", "startDt", "endDt", "billNo", "prescriptionYn")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("id", text="ID")
        self.tree.heading("treatCd", text="진료구분")
        self.tree.heading("deptNm", text="진료과")
        self.tree.heading("startDt", text="시작일")
        self.tree.heading("endDt", text="종료일")
        self.tree.heading("billNo", text="영수증번호")
        self.tree.heading("prescriptionYn", text="처방전 존재 유무")

        self.tree.column("id", width=20, anchor="center")
        self.tree.column("treatCd", width=100)
        self.tree.column("deptNm", width=100)
        self.tree.column("startDt", width=100)
        self.tree.column("endDt", width=100)
        self.tree.column("billNo", width=100)
        self.tree.column("prescriptionYn", width=100, anchor="center")

        # 초기 데이터 로드
        self.update_tree(self.user_data)

    def search_data(self):
        """검색어에 따라 데이터를 필터링"""
        keyword = self.ent_search.get().strip()

        # 검색어가 없으면 전체, 있으면 이름이나 이메일에 포함된 경우만 필터링
        filtered_data = [
            user for user in self.user_data
            if keyword == "" or keyword in user["deptNm"] or keyword in user["billNo"]
        ]
        self.update_tree(filtered_data)

    def update_tree(self, data):
        """트리뷰 비우고 새로운 데이터 채우기"""
        for item in self.tree.get_children():
            self.tree.delete(item)


        code_map = {"01": "외래", "02": "입원"}

        for user in data:
            # 코드를 텍스트로 변환 (매핑에 없는 코드는 원래 값 그대로 출력)
            treat_text = code_map.get(user["treatCd"], user["treatCd"])
            
            self.tree.insert("", "end", values=(user["id"], treat_text, user["deptNm"], user["startDt"], user["endDt"], user["billNo"], user["prescriptionYn"]))

    def call_api(self):
        """API 호출 (비동기 실행)"""
        # SSL 경고 메시지(InsecureRequestWarning) 숨기기
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # def _request():
        #     url = ''
        #     try:
        #         response = requests.post(url, json={
        #             'title': 'Postman Test',
        #             'body': 'Python requests call',
        #             'userId': 1,
        #         }, verify=False)
        #         response.raise_for_status()
        #
        #         result = response.json()
        #         self.user_data = result
        #         print('결과:', result)
        #     except Exception as e:
        #         print('에러 발생:', e)

        url = ""
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            data = response.json()
            print(data)
            self.user_data = data
        else:
            print("Request failed with status code:", response.status_code)
            self.user_data = [] # 에러 시 빈 리스트 초기화
        #self.setup_ui()

        # UI 프리징 방지를 위해 별도 스레드에서 실행
        #threading.Thread(target=_request, daemon=True).start()