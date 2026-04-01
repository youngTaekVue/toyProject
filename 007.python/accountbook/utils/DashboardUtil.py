import pandas as pd
from utils.Common import map_columns

class DashboardUtil:
    """가계부 요약 및 엑셀 데이터 처리를 담당하는 유틸리티 클래스"""
    
    def __init__(self, mapping_rules=None):
        # 규칙 초기화 시 글자수가 긴 키워드부터 매칭되도록 정렬
        self.mapping_rules = mapping_rules or []

    def _get_valid_df(self, df):
        """취소, 선승인 등을 제외한 유효 데이터프레임 반환"""
        valid_df = df.copy()
        # 필요한 컬럼이 없을 경우 기본값 생성 (에러 방지)
        for col in ['is_cancel', 'is_pre_auth', 'is_double_count']:
            if col not in valid_df.columns:
                valid_df[col] = False
        
        valid_df = valid_df[~(valid_df['is_cancel'] | valid_df['is_pre_auth'] | valid_df['is_double_count'])]
        valid_df['타입'] = valid_df['타입'].fillna('지출').astype(str).str.strip()
        valid_df['대분류'] = valid_df['대분류'].fillna('미분류').astype(str).str.strip().replace(['None', 'nan', ''], '미분류')
        return valid_df

    def get_summary_data(self, df):
        if df is None or df.empty: return 0, 0, {}
        valid_df = self._get_valid_df(df)
        
        income = valid_df[valid_df['타입'] == '수입']['금액'].abs().sum()
        expense = valid_df[valid_df['타입'] == '지출']['금액'].abs().sum()
        
        expense_df = valid_df[valid_df['타입'] == '지출']
        cat_summary = {}
        if not expense_df.empty:
            cat_group = expense_df.groupby('대분류')['금액'].sum().abs()
            cat_summary = cat_group[cat_group > 0].sort_values(ascending=False).to_dict()
        
        return int(income), int(expense), cat_summary

    def get_sub_category_summary(self, df, target_category):
        if df is None or df.empty: return {}
        valid_df = self._get_valid_df(df)
        sub_df = valid_df[(valid_df['대분류'] == target_category) & (valid_df['타입'] == '지출')].copy()
        
        if sub_df.empty: return {}
        sub_df['소분류'] = sub_df['소분류'].fillna('미분류').astype(str).str.strip().replace(['None', 'nan', ''], '미분류')
        sub_group = sub_df.groupby('소분류')['금액'].sum().abs()
        return sub_group[sub_group > 0].sort_values(ascending=False).to_dict()

    def auto_classify(self, row):
        """내용(content)을 분석하여 카테고리 자동 분류 (대소문자 무시 및 포함 검사)"""
        content = str(row.get('내용', '')).strip().lower() # 소문자로 변환하여 비교
        
        for rule in self.mapping_rules:
            if isinstance(rule, dict):
                kw, cat, sub = rule.get('merchant'), rule.get('category'), rule.get('sub_category')
            else:
                kw, cat, sub = rule[0], rule[1], rule[2]
            
            # 키워드도 소문자로 변환하여 비교 (대소문자 구분 없이 매칭)
            if kw and str(kw).strip().lower() in content:
                return pd.Series({'대분류': str(cat or '기타').strip(), '소분류': str(sub or '미분류').strip()})
        
        # 매칭되는 규칙이 없을 경우 기존 값 유지 시도
        exist_cat = str(row.get('대분류', '')).strip()
        if exist_cat and exist_cat not in ['None', 'nan', '', '미분류']:
            return pd.Series({'대분류': exist_cat, '소분류': row.get('소분류', '미분류')})
            
        return pd.Series({'대분류': '미분류', '소분류': '미분류'})

    def process_excel_data(self, df):
        alias_map = {
            'date': ['날짜', '일자', '거래일시'],
            'amount': ['금액', '거래금액', '지출'],
            'desc': ['내용', '사용내역', '사용처'],
            'payment': ['결제수단', '카드명'],
            'type': ['타입', '구분'],
            'cat': ['대분류', '카테고리'],
            'subcat': ['소분류', '상세분류']
        }
        df = map_columns(df, alias_map)
        df['DT'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['DT'])
        def clean_amt(v): return int("".join(c for c in str(v) if c.isdigit() or c == '-') or 0)
        final_df = pd.DataFrame()
        final_df['DT'] = df['DT']; final_df['금액'] = df['amount'].apply(clean_amt)
        final_df['내용'] = df['desc'].fillna("") if 'desc' in df.columns else ""
        final_df['결제수단'] = df['payment'].fillna("") if 'payment' in df.columns else ""
        final_df['타입'] = df['type'].fillna("") if 'type' in df.columns else ""
        # 엑셀에 분류가 이미 있는 경우를 위해 보존
        final_df['대분류'] = df['cat'].fillna("") if 'cat' in df.columns else ""
        final_df['소분류'] = df['subcat'].fillna("") if 'subcat' in df.columns else ""
        return final_df
