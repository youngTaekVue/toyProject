import pandas as pd
import database
from utils.Common import map_columns
from utils.Logger import logger

class FinancialUtil:
    @staticmethod
    def extract_section(df, keyword, stop_keyword=None, start_search_idx=0):
        """키워드 기반 섹션 추출 (자산/부채 등)"""
        print(f"\n[FinancialUtil] '{keyword}' 섹션 탐색 시작... (Index {start_search_idx} 이후)")
        try:
            # 1. 특정 인덱스 이후부터 키워드(섹션 제목) 행 찾기
            search_df = df.iloc[start_search_idx:]
            # 완전 일치 또는 포함 확인
            mask = search_df.apply(lambda row: row.astype(str).str.strip().str.fullmatch(keyword, na=False).any(), axis=1)
            if not mask.any():
                mask = search_df.apply(lambda row: row.astype(str).str.strip().str.contains(keyword, na=False).any(), axis=1)

            if not mask.any():
                print(f" -> [경고] '{keyword}' 키워드를 찾지 못했습니다.")
                return None, start_search_idx

            title_idx = mask.idxmax()
            print(f" -> [확인] '{keyword}' 제목 행 발견 (Index: {title_idx})")

            # 2. 정지 키워드(다음 섹션) 행 찾기
            stop_idx = len(df)
            if stop_keyword:
                # 제목 행 이후부터 검색
                stop_mask = df.iloc[title_idx + 1:].apply(lambda row: row.astype(str).str.strip().str.contains(stop_keyword, na=False).any(), axis=1)
                if stop_mask.any():
                    stop_idx = stop_mask.idxmax()
                    print(f" -> [확인] '{stop_keyword}' 정지 키워드 발견 (Index: {stop_idx})")

            # 3. 헤더 행 탐색 (항목/상품명, 금액 등이 포함된 행)
            header_idx = -1
            # '항목' 키워드를 최우선으로 고려 (사용자 요청 반영)
            potential_keywords = ['상품명', '자산명', '금액', '잔액', '기관', '비고']
            for i in range(title_idx + 1, min(title_idx + 6, stop_idx, len(df))):
                row_values = df.iloc[i].astype(str).str.strip().tolist()
                # 키워드가 2개 이상 포함된 행을 헤더로 간주
                match_count = sum(1 for k in potential_keywords if any(k in val for val in row_values))
                if match_count >= 2:
                    header_idx = i
                    break

            if header_idx == -1:
                # 헤더를 못 찾으면 제목 바로 다음 행을 헤더로 가정
                header_idx = title_idx + 1

            # 4. 데이터 추출
            # 헤더 행의 컬럼명 정리
            header_row = df.iloc[header_idx].astype(str).str.strip()
            temp_df = df.iloc[header_idx:stop_idx].copy().reset_index(drop=True)

            if temp_df.empty or len(temp_df) <= 1:
                return None, stop_idx

            # 첫 행을 컬럼명으로 설정
            raw_cols = [str(c).strip() for c in temp_df.iloc[0]]
            # 중복 컬럼명 처리
            new_cols = []
            counts = {}
            for col in raw_cols:
                if not col or col == 'nan': col = 'unnamed'
                if col in counts:
                    counts[col] += 1
                    new_cols.append(f"{col}_{counts[col]}")
                else:
                    counts[col] = 0
                    new_cols.append(col)

            temp_df.columns = new_cols
            section_df = temp_df.iloc[1:].copy().reset_index(drop=True)

            # 유효한 데이터가 있는 행만 추출 (상품명/항목이 비어있지 않은 행)
            # 여기서는 나중에 save_financial_data에서 필터링하므로 일단 반환
            return section_df, stop_idx

        except Exception as e:
            print(f" -> [에러] '{keyword}' 추출 중 오류: {e}")
            return None, start_search_idx

    @staticmethod
    def save_financial_data(df_list_with_cat):
        """재무 데이터(자산/부채) DB 저장"""
        print(f"\n[FinancialUtil] DB 저장 시작...")
        count = 0
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 데이터 중복 방지를 위해 초기화 (필요시 조정)
                    cursor.execute("TRUNCATE TABLE financial")
                    sql = "INSERT INTO financial (itemName, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)"

                    # 사용자 요청에 따라 '항목'을 상품명 매핑에 포함
                    alias_map = {
                        'item_name': ['상품명', '항목명', '자산명'],
                        'amount': ['금액', '잔액', '부채', '평가금액', '가치'],
                        'institution': ['기관', '은행', '증권사', '금융사'],
                        'note': ['비고', '메모', '설명']
                    }

                    for df, overall_cat in df_list_with_cat:
                        print(f"  - {overall_cat} 섹션 처리 중...")
                        cleaned = map_columns(df, alias_map)

                        last_inst, last_note = "", ""

                        for _, row in cleaned.iterrows():
                            # 데이터 읽기 및 공백 제거
                            name = str(row.get('item_name', '')).strip()

                            # 제외 조건: 빈 값, nan, 합계/소계 행
                            if not name or name.lower() in ['none', 'nan', '합계', '소계', 'total']:
                                continue

                            raw_amt = str(row.get('amount', '0')).strip()
                            try:
                                # 숫자, 마이너스, 소수점만 남기고 제거
                                clean_amt = ''.join(c for c in raw_amt if c.isdigit() or c in '.-')
                                amt = int(float(clean_amt)) if clean_amt else 0
                            except:
                                amt = 0

                            # 금액이 0이고 이름만 있는 경우(구분선 등) 제외할 수 있으나
                            # 여기서는 사용자가 나열을 요청했으므로 이름이 있으면 저장 시도
                            if amt == 0 and (not raw_amt or raw_amt.lower() in ['nan', 'none']):
                                continue

                            # 기관(institution) 및 비고(note) 정보 상속 (병합 셀 대응)
                            inst = str(row.get('institution', '')).strip()
                            if inst and inst.lower() != 'nan': last_inst = inst
                            else: inst = last_inst

                            note = str(row.get('note', '')).strip()
                            if note and note.lower() != 'nan': last_note = note
                            else: note = last_note

                            print(f"    [저장] {overall_cat} > {name}: {amt}")
                            cursor.execute(sql, (name, overall_cat, inst, amt, note))
                            count += 1
                conn.commit()
            logger.log("INFO", "FinancialDB", f"재무 데이터 {count}건 저장 완료")
        except Exception as e:
            print(f" -> [에러] DB 저장 중 오류 발생: {e}")
            raise

    @staticmethod
    def process_bank_status_sheet(df_bank_status):
        """뱅샐현황 시트 분석 (재무현황 아래의 자산/부채 추출)"""
        print("\n" + "="*50)
        print("[FinancialUtil] 뱅샐현황 분석 시작")

        # 1. '재무현황' 키워드 행 찾기 (기준점)
        mask = df_bank_status.apply(lambda row: row.astype(str).str.contains("재무현황", na=False).any(), axis=1)
        if not mask.any():
            print("[경고] '재무현황' 섹션을 찾을 수 없어 시트 처음부터 탐색합니다.")
            start_pos = 0
        else:
            start_pos = mask.idxmax()
            print(f"[확인] '재무현황' 기준점 발견 (Index: {start_pos})")

        # 2. '자산' 섹션 추출 (재무현황 아래에서 검색, 부채가 나오면 중단)
        df_asset, asset_end_pos = FinancialUtil.extract_section(
            df_bank_status, "자산", stop_keyword="부채", start_search_idx=start_pos
        )

        # 3. '부채' 섹션 추출 (자산 섹션 이후부터 검색)
        df_debt, _ = FinancialUtil.extract_section(
            df_bank_status, "부채", stop_keyword=None, start_search_idx=asset_end_pos if asset_end_pos > start_pos else start_pos
        )

        extracted_sections = []
        if df_asset is not None:
            extracted_sections.append((df_asset, "자산"))
        if df_debt is not None:
            extracted_sections.append((df_debt, "부채"))

        # 4. 수집된 데이터 DB 저장
        if extracted_sections:
            FinancialUtil.save_financial_data(extracted_sections)
        else:
            print("[알림] 추출된 자산/부채 데이터가 없습니다.")

        print("="*50)
