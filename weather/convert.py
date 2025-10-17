import pandas as pd
import json

# CSV 파일 경로
csv_file_path = 'file/coordinate.csv'

# JSON으로 저장할 경로
json_file_path = 'output_file_name.json'

# CSV 파일을 데이터프레임으로 읽기
df = pd.read_csv(csv_file_path)

# 데이터프레임을 JSON 형식 문자열로 변환
json_data = df.to_json(orient='records', indent=4)

# JSON 파일로 저장
with open(json_file_path, 'w', encoding='utf-8') as f:
    f.write(json_data)

print(f"CSV 파일이 성공적으로 JSON으로 변환되어 '{json_file_path}'에 저장되었습니다.")