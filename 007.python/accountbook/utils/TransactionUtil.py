import pandas as pd
from utils.Common import map_columns

class TransactionUtil:
    """가계부 요약 및 엑셀 데이터 처리를 담당하는 유틸리티 클래스"""
    
    def __init__(self, mapping_rules=None):
        # 규칙 초기화 시 글자수가 긴 키워드부터 매칭되도록 정렬
        self.mapping_rules = mapping_rules or []

    def _get_valid_df(self, df):
        """취소, 선승인, 이체 등을 제외한 실제 소비/수입 데이터프레임 반환"""
        valid_df = df.copy()
        # 필요한 컬럼이 없을 경우 기본값 생성
        for col in ['is_cancel', 'is_pre_auth', 'is_double_count']:
            if col not in valid_df.columns:
                valid_df[col] = False
        
        # 제외 조건: 취소됨, 선승인, 이중지출, 그리고 '이체' 타입 제외
        mask = ~(valid_df['is_cancel'] | valid_df['is_pre_auth'] | valid_df['is_double_count'])
        valid_df = valid_df[mask]
        
        # 타입 및 분류 정규화
        valid_df['타입'] = valid_df['타입'].fillna('지출').astype(str).str.strip()
        
        # 실질 소비 데이터만 남기기 위해 '이체' 타입 제거
        valid_df = valid_df[valid_df['타입'] != '이체']
        
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
        """내용을 분석하여 카테고리 자동 분류 및 타입(지출/수입/이체) 결정"""
        content = str(row.get('내용', '')).strip().lower()
        original_type = str(row.get('타입', '지출')).strip()
        
        for rule in self.mapping_rules:
            if isinstance(rule, dict):
                kw, cat, sub = rule.get('merchant'), rule.get('category'), rule.get('sub_category')
            else:
                kw, cat, sub = rule[0], rule[1], rule[2]
            
            if kw and str(kw).strip().lower() in content:
                # 대분류가 '이체' 또는 '자산이동'이면 타입을 '이체'로 변경
                new_type = original_type
                if cat in ['이체', '자산이동']:
                    new_type = '이체'
                
                return pd.Series({
                    '대분류': str(cat or '기타').strip(), 
                    '소분류': str(sub or '미분류').strip(),
                    '타입': new_type
                })
        
        # 매칭되는 규칙이 없을 경우
        return pd.Series({
            '대분류': '미분류', 
            '소분류': '미분류',
            '타입': original_type
        })

    def process_excel_data(self, df):
        alias_map = {
            'date': ['날짜', '일자', '거래일자', '거래일시'],
            'time': ['시간', '거래시간', '거래시각'],
            'amount': ['금액', '거래금액', '지출'],
            'desc': ['내용', '사용내역', '사용처'],
            'payment': ['결제수단', '카드명'],
            'type': ['타입', '구분'],
            'cat': ['대분류', '카테고리'],
            'subcat': ['소분류', '상세분류']
        }
        df = map_columns(df, alias_map)
        
        if 'time' in df.columns and 'date' in df.columns:
            combined = df['date'].astype(str).str.split(' ').str[0] + ' ' + df['time'].astype(str).str.split(' ').str[-1]
            df['DT'] = pd.to_datetime(combined, errors='coerce')
        else:
            df['DT'] = pd.to_datetime(df['date'], errors='coerce')

        df = df.dropna(subset=['DT'])
        
        def clean_amt(v): 
            try:
                return int("".join(c for c in str(v) if c.isdigit() or c == '-') or 0)
            except:
                return 0

        final_df = pd.DataFrame()
        final_df['DT'] = df['DT']
        final_df['금액'] = df['amount'].apply(clean_amt)
        final_df['내용'] = df['desc'].fillna("") if 'desc' in df.columns else ""
        final_df['결제수단'] = df['payment'].fillna("") if 'payment' in df.columns else ""
        final_df['타입'] = df['type'].fillna("") if 'type' in df.columns else ""
        final_df['대분류'] = df['cat'].fillna("") if 'cat' in df.columns else ""
        final_df['소분류'] = df['subcat'].fillna("") if 'subcat' in df.columns else ""
        return final_df
