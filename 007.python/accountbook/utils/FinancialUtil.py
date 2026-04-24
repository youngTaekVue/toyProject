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
                stop_mask = df.iloc[title_idx + 1:].apply(lambda row: row.astype(str).str.strip().str.contains(stop_keyword, na=False).any(), axis=1)
                if stop_mask.any():
                    stop_idx = stop_mask.idxmax()
                    print(f" -> [확인] '{stop_keyword}' 정지 키워드 발견 (Index: {stop_idx})")

            # 3. 헤더 행 탐색
            header_idx = -1
            potential_keywords = ['상품명', '자산명', '금액', '잔액', '기관', '비고', '항목']
            search_limit = min(title_idx + 6, stop_idx, len(df))

            for i in range(title_idx + 1, search_limit):
                row_values = df.iloc[i].astype(str).str.strip().tolist()
                match_count = sum(1 for k in potential_keywords if any(k in val for val in row_values))
                if match_count >= 2:
                    header_idx = i
                    break

            if header_idx == -1:
                header_idx = title_idx + 1
                print(f" -> [알림] 헤더를 찾지 못해 제목 다음 행(Index: {header_idx})을 헤더로 가정합니다.")
            else:
                print(f" -> [확인] 헤더 행 발견 (Index: {header_idx})")

            # 4. 데이터 추출
            if header_idx >= stop_idx or header_idx >= len(df):
                print(f" -> [경고] 추출할 데이터 범위가 유효하지 않습니다. (header_idx: {header_idx}, stop_idx: {stop_idx})")
                return None, stop_idx

            temp_df = df.iloc[header_idx:stop_idx].copy().reset_index(drop=True)
            print(f" -> [정보] 추출된 행 수(헤더 포함): {len(temp_df)}")

            if temp_df.empty or len(temp_df) <= 1:
                print(f" -> [알림] '{keyword}' 섹션에 유효한 데이터 행이 없습니다.")
                return None, stop_idx

            # 컬럼명 설정 및 정리
            raw_cols = [str(c).strip() for c in temp_df.iloc[0]]
            new_cols = []
            counts = {}
            for col in raw_cols:
                if not col or col == 'nan' or col == 'None': col = 'unnamed'
                if col in counts:
                    counts[col] += 1
                    new_cols.append(f"{col}_{counts[col]}")
                else:
                    counts[col] = 0
                    new_cols.append(col)

            temp_df.columns = new_cols
            section_df = temp_df.iloc[1:].copy().reset_index(drop=True)

            print(f" -> [성공] '{keyword}' 섹션 추출 완료 ({len(section_df)}건)")
            return section_df, stop_idx

        except Exception as e:
            print(f" -> [에러] '{keyword}' 추출 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None, start_search_idx

    @staticmethod
    def save_financial_data(df_list_with_cat):
        """재무 데이터(자산/부채) DB 저장"""
        print(f"\n[FinancialUtil] DB 저장 시작 (섹션 수: {len(df_list_with_cat)})")
        count = 0
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE financial")
                    sql = "INSERT INTO financial (itemName, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)"

                    alias_map = {
                        'item_name': ['상품명', '항목명', '자산명', '항목'],
                        'amount': ['금액', '잔액', '부채', '평가금액', '가치'],
                        'institution': ['기관', '은행', '증권사', '금융사'],
                        'note': ['비고', '메모', '설명']
                    }

                    for df, overall_cat in df_list_with_cat:
                        print(f"  - {overall_cat} 섹션 처리 중... (데이터 행: {len(df)})")
                        cleaned = map_columns(df, alias_map)

                        last_inst, last_note = "", ""

                        for _, row in cleaned.iterrows():
                            name = str(row.get('item_name', '')).strip()

                            if not name or name.lower() in ['none', 'nan', '합계', '소계', 'total']:
                                if overall_cat == "부채":
                                    logger.log("WARNING", "FinancialDB", f"부채 섹션에서 상품명(item_name)이 없어 항목을 건너뜁니다. Row: {row.to_dict()}")
                                continue

                            raw_amt = str(row.get('amount', '0')).strip()
                            try:
                                clean_amt = ''.join(c for c in raw_amt if c.isdigit() or c in '.-')
                                amt = int(float(clean_amt)) if clean_amt else 0
                            except:
                                amt = 0

                            if amt == 0 and (not raw_amt or raw_amt.lower() in ['nan', 'none']):
                                continue

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
        """뱅샐현황 시트 분석"""
        print("\n" + "="*50)
        print("[FinancialUtil] 뱅샐현황 분석 시작")

        mask = df_bank_status.apply(lambda row: row.astype(str).str.contains("재무현황", na=False).any(), axis=1)
        start_pos = mask.idxmax() if mask.any() else 0
        print(f"[확인] '재무현황' 기준점: Index {start_pos}")

        df_asset, asset_end_pos = FinancialUtil.extract_section(
            df_bank_status, "자산", stop_keyword="부채", start_search_idx=start_pos
        )

        df_debt, _ = FinancialUtil.extract_section(
            df_bank_status, "부채", stop_keyword=None, start_search_idx=asset_end_pos if asset_end_pos > start_pos else start_pos
        )

        extracted_sections = []
        if df_asset is not None:
            extracted_sections.append((df_asset, "자산"))
        if df_debt is not None:
            extracted_sections.append((df_debt, "부채"))

        if extracted_sections:
            FinancialUtil.save_financial_data(extracted_sections)
        else:
            print("[알림] 추출된 자산/부채 데이터가 전혀 없습니다.")

        print("="*50)
