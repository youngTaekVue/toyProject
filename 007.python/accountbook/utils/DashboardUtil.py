import pandas as pd
from utils.Common import map_columns

class DashboardUtil:
    """가계부 요약 및 엑셀 데이터 처리를 담당하는 유틸리티 클래스"""
    
    def __init__(self, mapping_rules=None):
        self.mapping_rules = mapping_rules or []

    def get_summary_data(self, df):
        """데이터프레임에서 실질 수입, 지출 및 카테고리별 합계를 계산합니다."""
        if df is None or df.empty:
            return 0, 0, {}

        valid_df = self._get_valid_df(df)
        
        income = valid_df[valid_df['타입'] == '수입']['금액'].abs().sum()
        expense = valid_df[valid_df['타입'] == '지출']['금액'].abs().sum()
        
        # 카테고리별 지출 요약
        expense_df = valid_df[valid_df['타입'] == '지출']
        cat_summary = {}
        if not expense_df.empty:
            cat_group = expense_df.groupby('대분류')['금액'].sum().abs()
            cat_summary = cat_group[cat_group > 0].sort_values(ascending=False).to_dict()
        
        return int(income), int(expense), cat_summary

    def get_sub_category_summary(self, df, target_category):
        """특정 대분류 내의 소분류별 지출 통계를 반환합니다."""
        if df is None or df.empty:
            return {}

        valid_df = self._get_valid_df(df)
        # 해당 카테고리의 지출 내역만 필터링
        sub_df = valid_df[(valid_df['대분류'] == target_category) & (valid_df['타입'] == '지출')]
        
        if sub_df.empty:
            return {}
            
        sub_df['소분류'] = sub_df['소분류'].fillna('미분류').astype(str).str.strip().replace(['None', 'nan', ''], '미분류')
        sub_group = sub_df.groupby('소분류')['금액'].sum().abs()
        return sub_group[sub_group > 0].sort_values(ascending=False).to_dict()

    def _get_valid_df(self, df):
        """취소, 선승인 등을 제외한 유효 데이터프레임 반환"""
        valid_df = df.copy()
        for col in ['is_cancel', 'is_pre_auth', 'is_double_count']:
            if col not in valid_df.columns:
                valid_df[col] = False
        
        valid_df = valid_df[~(valid_df['is_cancel'] | valid_df['is_pre_auth'] | valid_df['is_double_count'])]
        valid_df['타입'] = valid_df['타입'].astype(str).str.strip()
        valid_df['대분류'] = valid_df['대분류'].fillna('미분류').astype(str).str.strip().replace(['None', 'nan', ''], '미분류')
        return valid_df

    def auto_classify(self, row):
        """설정된 규칙에 따라 거래 내역의 카테고리를 자동 분류합니다."""
        content = str(row.get('내용', ''))
        for rule in self.mapping_rules:
            if isinstance(rule, dict):
                kw, cat, sub = rule.get('merchant'), rule.get('category'), rule.get('sub_category')
            else:
                kw, cat, sub = rule[0], rule[1], rule[2]
            if kw and str(kw) in content:
                return pd.Series({'대분류': cat, '소분류': sub})
        
        exist_cat = str(row.get('대분류', '')).strip()
        if exist_cat and exist_cat not in ['None', 'nan', '']:
            return pd.Series({'대분류': exist_cat, '소분류': row.get('소분류', '미분류')})
        return pd.Series({'대분류': '기타', '소분류': '미분류'})

    def process_excel_data(self, df):
        """엑셀 데이터를 가공합니다."""
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
        return final_df
