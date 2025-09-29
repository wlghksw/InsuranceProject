import pandas as pd
import os
import re

# --- 금액 문자열을 숫자로 변환하는 함수 ---
def parse_coverage_amount(amount_str):
    if not isinstance(amount_str, str):
        return None

    # '만원' 단위를 숫자로 변환 (예: 1,000만원 -> 10000000)
    if '만원' in amount_str:
        num_part = re.sub(r'[^0-9]', '', amount_str)
        if num_part:
            return int(num_part) * 10000

    # '만원' 단위가 없는 일반 숫자 처리 (예: 30000000)
    num_part = re.sub(r'[^0-9]', '', amount_str)
    if num_part:
        return int(num_part)

    return None


# --- 현재 폴더 구조에 맞게 파일 경로를 설정합니다 ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'insurance_data_raw.csv')
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, 'InsuranceWeb', 'products')
OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, 'accident_products.csv')

# 1. 원본 CSV 파일 읽기
try:
    df_raw = pd.read_csv(RAW_DATA_PATH, engine='python')
    print(f"1/5: '{RAW_DATA_PATH}' 파일을 성공적으로 읽었습니다.")
except FileNotFoundError:
    print(f"오류: '{RAW_DATA_PATH}' 파일을 찾을 수 없습니다.")
    exit()

# 2. '주계약' 데이터만 필터링
df_main = df_raw[df_raw['구분'] == '주계약'].copy()
print(f"2/5: 전체 데이터 중 '주계약' {len(df_main)}건을 필터링했습니다.")

# 3. 필요한 컬럼만 선택하고, 영어 이름으로 변경
column_mapping = {
    '보험회사명': 'insurance_company',
    '상품명': 'product_name',
    '남자 (월)': 'male_premium',
    '여자 (월)': 'female_premium',
    '가입금액': 'coverage_amount',
    '갱신주기': 'renewal_cycle',
    '특이사항': 'special_notes'
}
required_columns = list(column_mapping.keys())
existing_columns = [col for col in required_columns if col in df_main.columns]
df_selected = df_main[existing_columns]
df_cleaned = df_selected.rename(columns=column_mapping)
print("3/5: 필요한 7개 컬럼을 선택하고, 영어 이름으로 변경했습니다.")

# 4. ✨[수정된 부분]✨ 가입금액(coverage_amount)을 숫자로 변환
df_cleaned['coverage_amount'] = df_cleaned['coverage_amount'].apply(parse_coverage_amount)
# 변환 후 비어있는 값이 생긴 행은 삭제
df_cleaned.dropna(subset=['coverage_amount'], inplace=True)
print("4/5: 'coverage_amount'의 텍스트를 숫자로 변환했습니다.")


# 5. 최종 결과 CSV 파일로 저장
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
df_cleaned.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"5/5: 데이터 변환 완료! '{OUTPUT_PATH}' 경로에 파일이 생성되었습니다.")
print("\n >> 이제 API 서버를 다시 확인해주세요! <<")