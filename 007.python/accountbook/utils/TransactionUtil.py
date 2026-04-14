import pandas as pd
from utils.Common import map_columns

class TransactionUtil:
    """가계부 요약 및 엑셀 데이터 처리를 담당하는 유틸리티 클래스"""
    
    def __init__(self, mapping_rules=None):
        self.mapping_rules = mapping_rules or []

    def _get_valid_df(self, df):
        """취소, 선승인, 이체 등을 제외한 실제 소비/수입 데이터프레임 반환"""
        valid_df = df.copy()
        for col in ['is_cancel', 'is_pre_auth', 'is_double_count']:
            if col not in valid_df.columns:
                valid_df[col] = False
        
        valid_df['타입'] = valid_df['타입'].fillna('지출').astype(str).str.strip()
        # 실질 소비 데이터만 남기기 위해 '이체' 타입 제거
        valid_df = valid_df[valid_df['타입'] != '이체']
        
        valid_df['대분류'] = valid_df['대분류'].fillna('미분류').astype(str).str.strip().replace(['None', 'nan', ''], '미분류')
        return valid_df

    def get_summary_data(self, df):
        if df is None or df.empty: return 0, 0, {}
        valid_df = self._get_valid_df(df)
        
        # 제외 대상 필터링
        active_df = valid_df[~(valid_df['is_cancel'] | valid_df['is_pre_auth'] | valid_df['is_double_count'])]
        
        # 순수 수입: 타입='수입' AND 대분류='수입'
        income = active_df[(active_df['타입'] == '수입') & (active_df['대분류'] == '수입')]['금액'].abs().sum()
        
        # 순수 지출 계산: (타입='지출'의 합) - (타입='수입'이면서 환불/취소분인 것의 합)
        exp_df = active_df[active_df['타입'] == '지출']
        ref_df = active_df[(active_df['타입'] == '수입') & (active_df['대분류'] != '수입')]
        
        total_exp = exp_df['금액'].abs().sum() - ref_df['금액'].abs().sum()
        expense = max(0, total_exp)
        
        cat_summary = {}
        if not exp_df.empty:
            all_cats = active_df['대분류'].unique()
            for cat in all_cats:
                if cat == '수입' or cat == '금융/이체': continue
                c_exp = active_df[(active_df['대분류'] == cat) & (active_df['타입'] == '지출')]['금액'].abs().sum()
                c_ref = active_df[(active_df['대분류'] == cat) & (active_df['타입'] == '수입')]['금액'].abs().sum()
                net = c_exp - c_ref
                if net > 0:
                    cat_summary[cat] = int(net)
        
        return int(income), int(expense), cat_summary

    def get_sub_category_summary(self, df, target_category):
        if df is None or df.empty: return {}
        valid_df = self._get_valid_df(df)
        active_df = valid_df[~(valid_df['is_cancel'] | valid_df['is_pre_auth'] | valid_df['is_double_count'])]
        
        sub_df = active_df[(active_df['대분류'] == target_category) & (active_df['타입'] == '지출')].copy()
        ref_sub_df = active_df[(active_df['대분류'] == target_category) & (active_df['타입'] == '수입')].copy()
        
        if sub_df.empty and ref_sub_df.empty: return {}
        
        # 소분류별 합산 (지출 - 환불)
        result = {}
        all_subs = set(sub_df['소분류'].unique()) | set(ref_sub_df['소분류'].unique())
        for s in all_subs:
            s_exp = sub_df[sub_df['소분류'] == s]['금액'].abs().sum()
            s_ref = ref_sub_df[ref_sub_df['소분류'] == s]['금액'].abs().sum()
            net = s_exp - s_ref
            if net > 0: result[str(s)] = int(net)
            
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def auto_classify(self, row):
        content = str(row.get('내용', '')).strip().lower()
        original_type = str(row.get('타입', '지출')).strip()
        
        # 금융/이체/카드대금 보정 (교통비 오분류 방지 핵심 키워드)
        financial_kws = ['카드대금', '결제대금', '보험', '이자', '적금', '송금', '이체', '대출', '상환', '현금서비스']
        if any(kw in content for kw in financial_kws):
            return pd.Series({'대분류': '금융/이체', '소분류': '자동분류', '타입': '이체'})

        for rule in self.mapping_rules:
            if isinstance(rule, dict):
                kw, cat, sub = rule.get('merchant'), rule.get('category'), rule.get('sub_category')
            else:
                kw, cat, sub = rule[0], rule[1], rule[2]
            
            if kw and str(kw).strip().lower() in content:
                new_type = original_type
                if cat in ['이체', '자산이동', '금융/이체']:
                    new_type = '이체'
                return pd.Series({'대분류': str(cat or '기타').strip(), '소분류': str(sub or '미분류').strip(), '타입': new_type})
        
        return pd.Series({'대분류': '미분류', '소분류': '미분류', '타입': original_type})

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
                val_str = "".join(c for c in str(v) if c.isdigit() or c == '-')
                return int(val_str or 0)
            except: return 0

        final_df = pd.DataFrame()
        final_df['DT'] = df['DT']
        final_df['금액'] = df['amount'].apply(clean_amt)
        final_df['내용'] = df['desc'].fillna("") if 'desc' in df.columns else ""
        final_df['결제수단'] = df['payment'].fillna("") if 'payment' in df.columns else ""
        final_df['타입'] = df['type'].fillna("") if 'type' in df.columns else ""
        final_df['대분류'] = df['cat'].fillna("") if 'cat' in df.columns else ""
        final_df['소분류'] = df['subcat'].fillna("") if 'subcat' in df.columns else ""
        return final_df
