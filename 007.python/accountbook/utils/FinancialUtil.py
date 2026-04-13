import pandas as pd
import database
from utils.Common import map_columns
from utils.Logger import logger

class FinancialUtil:
    """재무(financial), 보험(insurance), 투자(investment) 데이터 처리를 담당"""
    
    @staticmethod
    def extract_section(df, keyword, start_col_idx=None, end_col_idx=None):
        """특정 열에서 제목을 찾고 2칸 아래부터 데이터를 추출"""
        print(f"[FinancialUtil] '{keyword}' 탐색 시작 (열: {start_col_idx})...")
        
        # 제목 행 찾기
        if start_col_idx is not None:
            col_data = df.iloc[:, start_col_idx].astype(str).str.strip()
            mask = col_data.str.contains(keyword, na=False)
        else:
            mask = df.apply(lambda row: row.astype(str).str.contains(keyword).any(), axis=1)
            
        if not mask.any():
            print(f"[FinancialUtil] '{keyword}' 제목을 찾지 못함.")
            return None
        
        title_idx = mask.idxmax()
        header_idx = title_idx + 2 # 제목 2칸 아래가 헤더
        
        if header_idx >= len(df):
            return None
            
        # 열 범위 지정 추출
        if start_col_idx is not None and end_col_idx is not None:
            section_df = df.iloc[header_idx:, start_col_idx:end_col_idx+1].copy().reset_index(drop=True)
        else:
            section_df = df.iloc[header_idx:].copy().reset_index(drop=True)
        
        # 헤더 설정
        section_df.columns = [str(c).strip() for c in section_df.iloc[0]]
        section_df = section_df.iloc[1:].copy().reset_index(drop=True)
        
        # 데이터 끝 지점 (빈 칸 나오기 전까지)
        is_empty = section_df.iloc[:, 0].isnull() | (section_df.iloc[:, 0].astype(str).str.strip() == '')
        if is_empty.any():
            last_idx = is_empty.idxmax()
            section_df = section_df.iloc[:last_idx]
            
        print(f"[FinancialUtil] '{keyword}' 추출 완료: {len(section_df)}건")
        return section_df

    @staticmethod
    def save_financial_data(df_list_with_cat):
        """재무(financial) 테이블 저장"""
        print("[FinancialUtil] 'financial' 테이블 저장 중...")
        count = 0
        try:
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE financial")
                    sql = "INSERT INTO financial (item_name, category, institution, amount, note) VALUES (%s, %s, %s, %s, %s)"
                    
                    alias_map = {
                        'item_name': ['항목', '자산명', '항목명'],
                        'amount': ['금액', '잔액', '가치', '부채금액'],
                        'note': ['비고', '메모']
                    }

                    for df, cat_name in df_list_with_cat:
                        if df is None or df.empty: continue
                        cleaned = map_columns(df, alias_map)
                        
                        # 병합된 열(상품명 등) 처리
                        others = [c for c in cleaned.columns if c not in ['item_name', 'amount', 'note']]
                        cleaned['inst'] = cleaned[others].fillna('').astype(str).agg(' '.join, axis=1).str.strip() if others else ""

                        for _, r in cleaned.iterrows():
                            name = str(r.get('item_name', '')).strip()
                            if name and name not in ['None', 'nan', '']:
                                raw_amt = str(r.get('amount', '0'))
                                amt = int(''.join(filter(str.isdigit, raw_amt)) or 0)
                                cursor.execute(sql, (name, cat_name, r['inst'], amt, r.get('note', '')))
                                count += 1
                conn.commit()
            logger.log("INFO", "FinancialDB", f"자산/부채 데이터 {count}건 저장 완료")
        except Exception as e:
            logger.log("ERROR", "FinancialDB", f"자산/부채 저장 중 오류: {str(e)}")
            raise

    @staticmethod
    def save_insurance_data(df):
        """보험(insurance) 테이블 저장"""
        if df is None or df.empty: return
        print("[FinancialUtil] 'insurance' 테이블 저장 중...")
        count = 0
        try:
            alias_map = {
                'company': ['보험사', '회사명'],
                'product_name': ['상품명', '보험명'],
                'premium': ['보험료', '월납']
            }
            cleaned = map_columns(df, alias_map)
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE insurance")
                    sql = "INSERT INTO insurance (company, product_name, insured, premium, expiry_date, status) VALUES (%s, %s, %s, %s, %s, %s)"
                    for _, r in cleaned.iterrows():
                        comp = str(r.get('company', '')).strip()
                        if comp and comp != 'nan':
                            raw_prem = str(r.get('premium', '0'))
                            prem = int(''.join(filter(str.isdigit, raw_prem)) or 0)
                            cursor.execute(sql, (comp, r.get('product_name'), r.get('insured'), prem, r.get('expiry_date'), r.get('status')))
                            count += 1
                conn.commit()
            logger.log("INFO", "InsuranceDB", f"보험 데이터 {count}건 저장 완료")
        except Exception as e:
            logger.log("ERROR", "InsuranceDB", f"보험 저장 중 오류: {str(e)}")
            raise

    @staticmethod
    def save_investment_data(df):
        """투자(investment) 테이블 저장"""
        if df is None or df.empty: return
        print("[FinancialUtil] 'investment' 테이블 저장 중...")
        count = 0
        try:
            alias_map = {'stock_name': ['종목명', '자산명']}
            cleaned = map_columns(df, alias_map)
            with database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE investment")
                    sql = "INSERT INTO investment (stock_name, quantity, avg_price, current_price, profit_loss, return_rate) VALUES (%s, %s, %s, %s, %s, %s)"
                    for _, r in cleaned.iterrows():
                        name = str(r.get('stock_name', '')).strip()
                        if name and name != 'nan':
                            def to_n(v): return float(''.join(c for c in str(v) if c.isdigit() or c in '.-') or 0)
                            cursor.execute(sql, (name, r.get('quantity'), to_n(r.get('avg_price')), to_n(r.get('current_price')), to_n(r.get('profit_loss')), to_n(r.get('return_rate'))))
                            count += 1
                conn.commit()
            logger.log("INFO", "InvestmentDB", f"투자 데이터 {count}건 저장 완료")
        except Exception as e:
            logger.log("ERROR", "InvestmentDB", f"투자 저장 중 오류: {str(e)}")
            raise
