import pandas as pd

def map_columns(df, alias_map):
    """엑셀의 다양한 헤더 명칭을 표준 컬럼명으로 매핑합니다."""
    # 모든 컬럼명의 공백 제거 및 문자열화
    df.columns = [str(c).strip().replace(" ", "") for c in df.columns]
    
    new_columns = {}
    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            if alias in df.columns:
                new_columns[alias] = standard_name
                break
    return df.rename(columns=new_columns)
