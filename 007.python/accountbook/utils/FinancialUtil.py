import pandas as pd
import database
from utils.Common import map_columns
from utils.Logger import logger

class FinancialUtil:
    @staticmethod
    def _clean_amount(value):
        s = str(value).strip()
        if not s or s.lower() in ["nan", "none"]:
            return 0
        try:
            cleaned = "".join(c for c in s if c.isdigit() or c in ".-")
            return int(float(cleaned)) if cleaned not in ["", "-", ".", "-."] else 0
        except:
            return 0

    @staticmethod
    def _is_meaningful_name(value):
        name = str(value).strip()
        if not name or name.lower() in ["nan", "none"]:
            return False
        lowered = name.lower()
        if lowered in ["합계", "소계", "총계", "total", "subtotal"]:
            return False
        # 다음 섹션 제목(예: "4.보험현황") 등도 제외
        if lowered[0].isdigit() and "." in lowered[:4]:
            return False
        return True

    @staticmethod
    def parse_financial_status_table(df_raw):
        """
        '재무현황' 표(좌: 자산 / 우: 부채)에서 상품명/금액을 추출합니다.
        기대 구조(대략): 자산(상품명,금액) 컬럼과 부채(상품명,금액) 컬럼이 같은 행에 나란히 존재
        """
        if df_raw is None or df_raw.empty:
            return []

        # 문자열 정규화된 매트릭스
        df = df_raw.copy()
        df = df.where(pd.notna(df), None)

        def norm(x):
            if x is None:
                return ""
            return str(x).strip()

        # 헤더 행 찾기: "상품명"과 "금액"이 2세트(자산/부채)로 존재하는 행을 우선 탐색
        header_idx = None
        header_cells = None
        for i in range(min(len(df), 200)):  # 상단 200행 정도만 탐색
            row = [norm(v) for v in df.iloc[i].tolist()]
            if not any(row):
                continue
            상품명_cols = [j for j, v in enumerate(row) if "상품명" == v]
            금액_cols = [j for j, v in enumerate(row) if "금액" == v]
            if len(상품명_cols) >= 2 and len(금액_cols) >= 2:
                header_idx = i
                header_cells = row
                break

        # fallback: "자산" "부채" 라벨이 있는 행 이후 1~3행 안에서 헤더를 찾기
        if header_idx is None:
            for i in range(min(len(df), 200)):
                row = [norm(v) for v in df.iloc[i].tolist()]
                if any(v == "자산" for v in row) and any(v == "부채" for v in row):
                    for k in range(i, min(i + 5, len(df))):
                        r = [norm(v) for v in df.iloc[k].tolist()]
                        if r.count("상품명") >= 1 and r.count("금액") >= 1:
                            header_idx = k
                            header_cells = r
                            break
                if header_idx is not None:
                    break

        if header_idx is None:
            return []

        # 자산/부채 쌍을 구성: "상품명"의 왼쪽 절반을 자산, 오른쪽 절반을 부채로 간주
        name_cols = [j for j, v in enumerate(header_cells) if v == "상품명"]
        amt_cols = [j for j, v in enumerate(header_cells) if v == "금액"]

        # "부채" 라벨이 있는 위치를 찾아 좌/우를 나누는 기준점으로 사용
        split_col = None
        for k in range(max(0, header_idx - 2), min(len(df), header_idx + 3)):
            r = [norm(v) for v in df.iloc[k].tolist()]
            if "부채" in r:
                try:
                    split_col = r.index("부채")
                    break
                except:
                    pass

        # 가장 가까운 금액 컬럼을 각 상품명 컬럼에 매칭
        pairs = []
        for nc in name_cols:
            # 상품명 오른쪽 방향으로 가장 가까운 "금액"을 찾는다
            candidates = [ac for ac in amt_cols if ac > nc]
            if not candidates:
                continue
            pairs.append((nc, min(candidates)))

        if len(pairs) < 2:
            return []

        # 좌/우 pair 선택: 가능하면 split_col(부채 라벨 위치) 기준으로 분리
        pairs = sorted(pairs, key=lambda x: x[0])
        if split_col is not None:
            left_pairs = [p for p in pairs if p[0] < split_col]
            right_pairs = [p for p in pairs if p[0] > split_col]
            # split_col을 찾았는데 한쪽이 비는 경우만 fallback
            asset_name_col, asset_amt_col = (left_pairs[0] if left_pairs else pairs[0])
            debt_name_col, debt_amt_col = (right_pairs[0] if right_pairs else pairs[-1])
        else:
            # fallback: 좌측 pair = 자산, 우측 pair = 부채
            asset_name_col, asset_amt_col = pairs[0]
            debt_name_col, debt_amt_col = pairs[-1]

        # 항목(분류) 컬럼도 있으면 저장용으로 함께 사용 (자산: '항목'이 상품명 왼쪽, 부채도 동일)
        def find_left_col(label, name_col):
            if "항목" in header_cells:
                # 해당 영역의 가장 가까운 '항목'을 사용
                item_cols = [j for j, v in enumerate(header_cells) if v == "항목" and j < name_col]
                return max(item_cols) if item_cols else None
            return None

        asset_item_col = find_left_col("항목", asset_name_col)
        debt_item_col = find_left_col("항목", debt_name_col)

        results = []
        empty_streak = 0
        for i in range(header_idx + 1, len(df)):
            row = df.iloc[i].tolist()
            a_name = norm(row[asset_name_col]) if asset_name_col < len(row) else ""
            a_amt = row[asset_amt_col] if asset_amt_col < len(row) else None
            d_name = norm(row[debt_name_col]) if debt_name_col < len(row) else ""
            d_amt = row[debt_amt_col] if debt_amt_col < len(row) else None
            a_item_fallback = norm(row[asset_item_col]) if asset_item_col is not None and asset_item_col < len(row) else ""
            d_item_fallback = norm(row[debt_item_col]) if debt_item_col is not None and debt_item_col < len(row) else ""

            # 다음 섹션 진입 감지(행에 "현황" 같은 타이틀이 오면 중단)
            joined = " ".join(norm(v) for v in row if norm(v))
            if any(k in joined for k in ["보험현황", "투자현황", "대출현황"]) and not (a_name or d_name):
                break

            produced = 0
            a_used_fallback = not FinancialUtil._is_meaningful_name(a_name) and FinancialUtil._is_meaningful_name(a_item_fallback)
            a_final_name = a_name if FinancialUtil._is_meaningful_name(a_name) else (a_item_fallback if a_used_fallback else "")
            if FinancialUtil._is_meaningful_name(a_final_name):
                amt = FinancialUtil._clean_amount(a_amt)
                if amt != 0:
                    # 상품명이 비어서 '항목'을 상품명으로 대체한 경우 institution에는 중복으로 넣지 않음
                    results.append({"item_name": a_final_name, "category": "자산", "institution": ("" if a_used_fallback else a_item_fallback), "amount": amt, "note": ""})
                    produced += 1

            # 부채는 '상품명' 칸이 비어 있고 '항목'만 채워진 템플릿이 많아 fallback을 허용
            d_used_fallback = not FinancialUtil._is_meaningful_name(d_name) and FinancialUtil._is_meaningful_name(d_item_fallback)
            d_final_name = d_name if FinancialUtil._is_meaningful_name(d_name) else (d_item_fallback if d_used_fallback else "")
            if FinancialUtil._is_meaningful_name(d_final_name):
                amt = FinancialUtil._clean_amount(d_amt)
                if amt != 0:
                    # 예: '장기대출'이 사실상 상품명인 케이스(상품명 칸이 비어있음) → institution은 비움
                    results.append({"item_name": d_final_name, "category": "부채", "institution": ("" if d_used_fallback else d_item_fallback), "amount": amt, "note": ""})
                    produced += 1

            if produced == 0 and not joined:
                empty_streak += 1
            else:
                empty_streak = 0

            # 표 하단의 빈 행이 연속되면 종료
            if empty_streak >= 10:
                break

        return results

    @staticmethod
    def save_financial_rows(rows, truncate=True):
        """parse_financial_status_table() 결과를 DB에 저장합니다. (itemName/item_name 둘 다 호환)"""
        if not rows:
            return 0
        count = 0
        with database.get_db_connection() as conn:
            with conn.cursor() as cursor:
                if truncate:
                    cursor.execute("TRUNCATE TABLE financial")

                # 컬럼명/updated_at 유무 호환 처리 (첫 성공 쿼리를 캐시)
                insert_sqls = [
                    # itemName
                    "INSERT INTO financial (itemName, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)",
                    "INSERT INTO financial (itemName, category, institution, amount, note, updated_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                    # item_name
                    "INSERT INTO financial (item_name, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)",
                    "INSERT INTO financial (item_name, category, institution, amount, note, updated_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                ]

                working_sql = None

                for r in rows:
                    name = str(r.get("item_name", "")).strip()
                    if not FinancialUtil._is_meaningful_name(name):
                        continue
                    params = (
                        name,
                        str(r.get("category", "")).strip(),
                        str(r.get("institution", "")).strip(),
                        int(r.get("amount", 0) or 0),
                        str(r.get("note", "")).strip(),
                    )

                    if working_sql is None:
                        last_err = None
                        for sql in insert_sqls:
                            try:
                                cursor.execute(sql, params)
                                working_sql = sql
                                count += 1
                                last_err = None
                                break
                            except Exception as e:
                                last_err = e
                                continue
                        if last_err is not None and working_sql is None:
                            raise last_err
                        continue

                    cursor.execute(working_sql, params)
                    count += 1
            conn.commit()
        return count

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
