import pandas as pd

# CSV 데이터 로드
df = pd.read_csv('files/sample1.csv', encoding='UTF-8')

# JSON 변환 및 저장
output_path = 'files/sample1.json'

# orient='records': 리스트 내의 딕셔너리 형태 [{"col":"val"}, ...] 로 변환
# force_ascii=False: 한글이 유니코드 코드로 이스케이프되지 않도록 설정
# indent=4: 사람이 읽기 좋게 들여쓰기 적용
df.to_json(output_path, orient='records', force_ascii=False, indent=4)

print(f"{output_path} 변환 완료")