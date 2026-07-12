import json
import urllib.request
import urllib.error
import os

# =========================================================================
# [데이터 생성기] 대시보드 API에서 '20260101_20260707' 파일의 '미확인' 건들을
# 가져와 대시보드 UI/스타일과 동일한 HTML 테이블을 포함한 JSON을 생성합니다.
# =========================================================================

def generate_hospitals_json():
    api_base_url = "http://localhost:3000/api/errorStatistics"
    
    # 1. 대상 파일 지정
    target_file_key = "20260101_20260707"
    print(f"[Generator] '{target_file_key}' 차수의 데이터를 대시보드 API로부터 읽어옵니다...")

    # 2. 지정 파일의 데이터 조회 API 호출
    try:
        req = urllib.request.Request(f"{api_base_url}/data/{target_file_key}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            rows_data = json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"❌ 대시보드 API 서버(포트 3000) 연결 실패: {e}")
        print("💡 백엔드 서버(Express)가 켜져 있는지 확인해 주세요 (npm run dev).")
        return False
    except Exception as e:
        print(f"❌ 데이터 조회 실패: {e}")
        return False

    if not rows_data.get("success") or not rows_data.get("rows"):
        print("❌ 엑셀 데이터를 정상적으로 읽어오지 못했습니다.")
        return False

    all_rows = rows_data["rows"]
    print(f"📊 총 {len(all_rows)}개의 행 데이터를 읽어왔습니다.")

    # 3. 진행상태가 '미확인'인 대상만 필터링
    unconfirmed_rows = [r for r in all_rows if r.get("state") == "미확인"]
    print(f"🔍 진행상태 '미확인' 건수: {len(unconfirmed_rows)}건")

    if not unconfirmed_rows:
        print(f"✨ '{target_file_key}' 파일에 진행해야 할 '미확인' 청구 에러 내역이 없습니다!")
        return False

    # 4. 병원별(hospital)로 데이터 그룹화
    hospitals_group = {}
    for row in unconfirmed_rows:
        h_name = row.get("hospital", "알 수 없는 병원").strip()
        if h_name not in hospitals_group:
            hospitals_group[h_name] = []
        hospitals_group[h_name].append(row)

    # 5. 병원별 메일 주입용 JSON 포맷 구성 (대시보드 UI/스타일 그대로 구현)
    hospitals_mail_list = []
    
    for h_name, rows in hospitals_group.items():
        # 대시보드에서 사용하는 6개 열(No, 기관번호, 병원명, 병원EMR, 청구실패사유, 진료내역) 스타일 그대로 행 구성
        table_rows_html = ""
        for idx, row in enumerate(rows):
            no = idx + 1
            inst_id = row.get("institutionId", "-")
            hosp_name = row.get("hospital", "-")
            emr_type = row.get("emr", "-")
            category = row.get("category", "미분류")
            details = row.get("details", "-")

            table_rows_html += f"""
        <tr style="height: 25px;">
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">{no}</td>
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">{inst_id}</td>
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #333;">{hosp_name}</td>
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">{emr_type}</td>
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #1e3a8a; font-weight: bold;">{category}</td>
          <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #555; word-break: break-all;">{details}</td>
        </tr>"""

        # 대시보드 메일 발송기 UI의 청색 프리미엄 스타일(#1f4e78) 그대로 HTML 조립 (상태 제외)
        html_body = f"""
<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 13px; line-height: 1.6; color: #333;">
    <p>안녕하세요. {h_name} 원무팀 담당자님.</p>
    <p>이메일 또는 메신저로 전달되는 자동화 문구입니다. 아래 오류 내역을 확인해 주십시오.</p>
    
    <div style="margin-top: 25px; margin-bottom: 5px; font-size: 15px; font-weight: bold; color: #002060;">
      ■ {h_name} - 청구 오류 내역 취합 현황
    </div>
    
    <table style="width: 100%; border-collapse: collapse; border: 1.5px solid #1f4e78; margin-bottom: 18px; font-size: 12px;">
      <thead>
        <tr style="background-color: #1f4e78; color: #ffffff; height: 28px; font-weight: bold;">
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 40px; text-align: center;">No</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원기관번호</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 160px; text-align: left;">병원명</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원EMR</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 170px; text-align: left;">청구실패사유</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; text-align: left;">진료내역 (진료일자 및 UUID)</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
    </table>
    
    <p style="margin-top: 20px;">처리되시면 회신 부탁드립니다.<br>감사합니다.</p>
</div>
        """

        # 병원별 JSON 구조체 작성
        hospital_mail_data = {
            "hospital": h_name,
            "to": "dudxor129@naver.com", # 테스트 수신 계정 고정
            "subject": f"[보정요청] {h_name} 청구오류 내역",
            "html_body": html_body.strip()
        }
        hospitals_mail_list.append(hospital_mail_data)

    # 6. JSON 파일로 저장
    output_filename = "hospitals_data.json"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hospitals_mail_list, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 메일 전송 데이터 파일 생성 완료: {output_path} (총 {len(hospitals_mail_list)}개 병원)")
    return True

if __name__ == "__main__":
    generate_hospitals_json()
