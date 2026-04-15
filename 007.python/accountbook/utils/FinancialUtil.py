import pandas as pd
import database
from utils.Common import map_columns
from utils.Logger import logger

class FinancialUtil:
    @staticmethod
    def extract_section(df, keyword, stop_keyword=None):
        """
        키워드 기반 섹션 추출 (중복 컬럼명 해결 로직 포함, stop_keyword로 섹션 경계 명확화,
        데이터 열 범위 동적 파악)
        """
        print(f"\n[FinancialUtil] '{keyword}' 섹션 탐색 시작...")
        try:
            # 1. 현재 섹션의 제목(keyword) 행 찾기
            mask = df.apply(lambda row: row.astype(str).str.strip().str.contains(keyword, na=False).any(), axis=1)
            if not mask.any():
                print(f" -> [경고] '{keyword}' 키워드를 찾지 못했습니다.")
                return None

            title_idx = mask.idxmax()
            print(f" -> [확인] '{keyword}' 제목 행 발견 (Index: {title_idx})")

            # 2. 정지 키워드(stop_keyword) 행 찾기 (현재 섹션의 끝을 지정)
            stop_idx = len(df) # 기본값: DataFrame의 끝
            if stop_keyword:
                stop_mask = df.apply(lambda row: row.astype(str).str.strip().str.contains(stop_keyword, na=False).any(), axis=1)
                if stop_mask.any():
                    # 현재 제목 행 이후에 나타나는 첫 번째 stop_keyword를 찾음
                    potential_stop_indices = stop_mask[stop_mask].index.tolist()
                    for idx in potential_stop_indices:
                        if idx > title_idx: # stop_keyword가 현재 섹션 제목 이후에 나타나야 함
                            stop_idx = idx
                            print(f" -> [확인] '{stop_keyword}' 정지 키워드 발견 (Index: {stop_idx})")
                            break
            print(f" -> [DEBUG] 최종 stop_idx: {stop_idx}")

            # 3. 헤더 행 탐색 (제목 행과 정지 키워드 행 사이에서)
            header_idx = -1
            potential_keywords = ['항목', '자산명', '상품명', '금액', '잔액', '기관', '비고']
            for i in range(title_idx + 1, min(title_idx + 11, stop_idx, len(df))):
                row_str = "".join(df.iloc[i].astype(str))
                if sum(1 for k in potential_keywords if k in row_str) >= 2:
                    header_idx = i
                    break

            if header_idx == -1:
                header_idx = title_idx + 2 # 못 찾으면 기본 오프셋 적용
                print(f" -> [알림] 헤더를 찾지 못해 기본 오프셋(+2) 적용 (Index: {header_idx})")
            else:
                print(f" -> [확인] 헤더 행 확정 (Index: {header_idx})")

            if header_idx >= len(df) or header_idx >= stop_idx:
                print(f" -> [경고] 헤더 행 ({header_idx})이 데이터 범위를 벗어나거나 정지 키워드({stop_idx}) 이후입니다.")
                return None

            # 4. 데이터 열 범위 동적 파악
            header_row_values = df.iloc[header_idx].astype(str).str.strip()
            valid_cols_indices = header_row_values[header_row_values != ''].index.tolist()

            if not valid_cols_indices:
                print(f" -> [경고] 헤더 행에 유효한 컬럼명이 없습니다. 전체 열 사용.")
                data_start_col = 0
                data_end_col = len(df.columns) - 1
            else:
                data_start_col = valid_cols_indices[0]
                data_end_col = valid_cols_indices[-1]

            print(f" -> [확인] 데이터 열 범위: {data_start_col}번 열부터 {data_end_col}번 열까지")

            # 5. 데이터 추출 및 컬럼명 정제 (헤더부터 정지 키워드 직전까지, 동적으로 파악된 열 범위로)
            print(f" -> [DEBUG] df.iloc[{header_idx}:{stop_idx}, {data_start_col}:{data_end_col+1}] 슬라이싱 시도")
            temp_df = df.iloc[header_idx:stop_idx, data_start_col:data_end_col+1].copy().reset_index(drop=True)

            if temp_df.empty:
                print(f" -> [결과] '{keyword}' 섹션에 추출할 데이터가 없습니다 (헤더 이후 정지 키워드까지).")
                return None

            # 중복 컬럼명 처리 로직
            raw_cols = [str(c).strip() for c in temp_df.iloc[0]]
            new_cols = []
            counts = {}
            for col in raw_cols:
                if col in counts:
                    counts[col] += 1
                    new_cols.append(f"{col}_{counts[col]}")
                else:
                    counts[col] = 0
                    new_cols.append(col)

            temp_df.columns = new_cols
            section_df = temp_df.iloc[1:].copy().reset_index(drop=True)

            # 6. 데이터 끝 지점 판단 (행 전체가 비어있는지 확인)
            final_rows = []
            for idx, row in section_df.iterrows():
                # 행 전체가 비어있으면 데이터의 끝으로 간주
                if row.astype(str).str.strip().isin(['', 'nan', 'None']).all():
                    print(f" -> [DEBUG] 빈 행 발견 (Index: {idx}), 데이터 끝으로 판단.")
                    break
                final_rows.append(row)

            if not final_rows:
                print(f" -> [결과] '{keyword}' 섹션에 데이터가 없습니다.")
                return None

            result_df = pd.DataFrame(final_rows)
            print(f" -> [완료] '{keyword}' 섹션 추출 성공 (총 {len(result_df)}건)")
            return result_df

        except Exception as e:
            print(f" -> [에러] '{keyword}' 추출 중 오류: {e}")
            return None

    @staticmethod
    def save_financial_data(df_list_with_cat):
        """재무 데이터 DB 저장 (금액 .0 처리 및 컬럼명 반영)"""
        print(f"\n[FinancialUtil] DB 저장 프로세스 시작...")
        count = 0
        try:
            with database.get_db_connection() as conn:
                print(" -> DB 연결 성공")
                with conn.cursor() as cursor:
                    print(" -> 기존 데이터 초기화(TRUNCATE) 중...")
                    cursor.execute("TRUNCATE TABLE financial")

                    sql = "INSERT INTO financial (itemName, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)"

                    alias_map = {
                        'item_name': ['상품명', '항목명', '항목', '자산명'],
                        'amount': ['금액', '잔액', '부채금액', '평가금액', '가치'],
                        'institution': ['기관', '은행', '증권사', '금융사'],
                        'note': ['비고', '메모', '설명']
                    }

                    for df, overall_cat in df_list_with_cat:
                        print(f"\n -> [DEBUG] 처리 중인 DataFrame의 overall_cat: '{overall_cat}'")
                        print(" -> [DEBUG] DataFrame head:\n", df.head())
                        print(" -> [DEBUG] DataFrame tail:\n", df.tail())

                        cleaned = map_columns(df, alias_map)
                        current_sub_cat = overall_cat # 섹션의 기본 카테고리 (예: "자산", "부채")
                        last_inst, last_note = "", ""

                        for _, row in cleaned.iterrows():
                            def get_v(col):
                                val = row.get(col, '')
                                if isinstance(val, pd.Series): val = val.iloc[0]
                                return str(val).strip()

                            name = get_v('item_name')
                            if not name or name in ['None', 'nan']: continue

                            raw_amt = get_v('amount')
                            try:
                                clean_amt = ''.join(c for c in raw_amt if c.isdigit() or c in '.-')
                                amt = int(float(clean_amt)) if clean_amt else 0
                            except:
                                amt = 0

                            # 그룹 헤더 판단 (금액이 0이거나 금액 컬럼이 비어있으면 새로운 카테고리 시작으로 인식)
                            if amt == 0 and (not raw_amt or raw_amt in ['nan', '0', 'None']):
                                current_sub_cat = name # "자유입출금 자산" 등이 여기에 할당되어 category가 됨
                                print(f"    [카테고리 변경] -> {current_sub_cat}")
                                continue

                            # "장기대출" 그룹은 제외
                            if "장기대출" in current_sub_cat:
                                print(f"    [건너뛰기] '장기대출' 그룹 항목: {name}")
                                continue

                            # 병합 셀 상속 처리
                            inst = get_v('institution')
                            if inst and inst != 'nan': last_inst = inst
                            note = get_v('note')
                            if note and note != 'nan': last_note = note

                            # DB에 삽입: itemName에 상품명(name), category에 그룹명(current_sub_cat) 삽입
                            print(f"    [삽입 예정] itemName='{name}', category='{current_sub_cat}', inst='{last_inst}', amt={amt}, note='{last_note}'")
                            cursor.execute(sql, (name, current_sub_cat, last_inst, amt, last_note))
                            count += 1
                conn.commit()

            print(f"[FinancialUtil] 저장 성공: 총 {count}건의 데이터가 반영되었습니다.")
            logger.log("INFO", "FinancialDB", f"재무 데이터 {count}건 저장 완료")
        except Exception as e:
            print(f" -> [에러] DB 저장 중 오류 발생: {e}")
            raise

    @staticmethod
    def process_bank_status_sheet(df_bank_status):
        """뱅샐현황 시트 분석 및 DB 동기화 통합 처리"""
        print("\n" + "="*50)
        print("[FinancialUtil] 뱅샐현황 분석 및 DB 동기화 시작")
        print("="*50)

        # 전체 DataFrame의 상위/하위 몇 줄을 출력하여 구조 파악에 도움
        print("\n[DEBUG] 전체 엑셀 데이터 (df_bank_status) 미리보기:")
        print(df_bank_status.head(10))
        print(df_bank_status.tail(10))
        print(f"[DEBUG] 전체 엑셀 데이터 shape: {df_bank_status.shape}\n")

        # 섹션 정의 (순서 중요: 다음 섹션의 키워드가 현재 섹션의 stop_keyword가 됨)
        sections_config = [
            ("재무현황", "자산"), # '재무현황' 섹션은 '자산' 키워드 전까지 추출
            ("자산", "부채"),    # '자산' 섹션은 '부채' 키워드 전까지 추출
            ("부채", None)     # '부채' 섹션은 끝까지 추출
        ]

        extracted_sections = []
        for keyword, stop_keyword in sections_config:
            df_section = FinancialUtil.extract_section(df_bank_status, keyword, stop_keyword)
            if df_section is not None and not df_section.empty:
                extracted_sections.append((df_section, keyword))
            else:
                print(f" -> [DEBUG] '{keyword}' 섹션은 추출되지 않았거나 비어있습니다.")

        if extracted_sections:
            FinancialUtil.save_financial_data(extracted_sections)
        else:
            print("\n[FinancialUtil] 결과: 유효한 데이터를 찾지 못했습니다. 엑셀 시트 구조를 확인하세요.")

        print("\n" + "="*50)
        print("[FinancialUtil] 모든 프로세스 종료")
        print("="*50)