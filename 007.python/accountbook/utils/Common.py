import pandas as pd

def map_columns(df, alias_map):
    """엑셀의 다양한 헤더 명칭을 표준 컬럼명으로 매핑합니다."""
    # 1. header=None으로 읽었을 경우를 대비해 첫 번째 행이 헤더인지 확인 및 처리
    # 컬럼명이 숫자로만 되어 있다면 첫 번째 행을 컬럼명으로 사용 시도
    if all(isinstance(c, int) for c in df.columns):
        first_row = df.iloc[0].astype(str).tolist()
        df.columns = [c.strip().replace(" ", "") for c in first_row]
        df = df[1:].reset_index(drop=True)
    else:
        # 이미 문자열 컬럼명이 있다면 공백만 제거
        df.columns = [str(c).strip().replace(" ", "") for c in df.columns]
    
    new_columns_map = {}
    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            cleaned_alias = str(alias).strip().replace(" ", "")
            if cleaned_alias in df.columns:
                new_columns_map[cleaned_alias] = standard_name
                break
    
    # 매핑된 컬럼 이름으로 변경
    df = df.rename(columns=new_columns_map)
    
    return df
