종신 보험 맞춤 추천 (Life Insurance Recommender)

KNN 기반의 종신보험 추천 시스템
CSV 데이터를 기반으로 사용자 입력값(성별, 희망 보험료, 지급금액, 나이, 직업)에 따라
가장 유사한 보험 상품 Top-K를 추천.

주요 특징

성별 분리 스케일링
남/녀 풀을 각각 분리하여 StandardScaler로 정규화
→ 성별별 보험료 스케일 차이 보정

직업 위험도 추정
직업명에 대응되는 위험도가 불명확할 경우,
동일 직업군의 최빈값(mode) 으로 위험도 추정

정렬 옵션

distance : 전체 피처 거리 (기본값)

premium : 보험료 차이 절댓값

coverage : 지급금액 차이 절댓값

상품명 복원
내부적으로 라벨 인코딩을 수행하지만,
출력 시 원래 상품명으로 복원되어 표시됩니다.

Repository 구조
life-insurance-recommender/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  └─ README.md
├─ src/
│  └─ life_insurance_recommender/
│     ├─ __init__.py
│     └─ recommender.py
└─ scripts/
   └─ demo.py

실행 방법
1️⃣ 의존성 설치
pip install -r requirements.txt

2️⃣ CSV 파일 준비

insurance_core.csv 파일을 프로젝트 루트 또는 data/ 폴더에 둡니다.

3️⃣ 데모 실행
python scripts/demo.py \
  --csv ./insurance_core.csv \
  --gender 남자 \
  --premium 50000 \
  --coverage 10000000 \
  --age 25 \
  --job 사무직 \
  --k 10 \
  --sort distance

4️⃣ Python에서 직접 사용
from src.life_insurance_recommender import Recommender

rec = Recommender().fit_csv("./insurance_core.csv")
result = rec.recommend_top_k(
    gender_input="남자",
    premium=50000,
    coverage=10000000,
    age=25,
    job_text="사무직",
    k=5,
    sort_by="distance"
)
print(result)

데이터 스키마
컬럼명	설명
상품명	보험 상품 이름
성별	남자 / 여자 / M / F
남자(보험료)	남자 기준 월 보험료
여자(보험료)	여자 기준 월 보험료
지급금액	보장(지급) 금액
가입금액	총 납입금액
나이	가입자 나이
직업	직업명
직업 위험도	낮음 / 중간 / 높음 등 위험 수준


추천 로직
1️⃣ 라벨 인코딩 (LabelEncoder)

문자열 데이터를 숫자 코드로 변환
(직업, 위험도, 상품명, 성별)

2️⃣ 성별별 스케일링 (StandardScaler)

여자 풀 : [여자(보험료), 지급금액, 나이, 직업, 직업 위험도]

남자 풀 : [남자(보험료), 지급금액, 나이, 직업, 직업 위험도]
각각 별도의 스케일러로 정규화

3️⃣ 직업 위험도 보정

동일 직업군의 최빈 위험도(mode) 사용
→ 데이터가 불완전해도 안정적인 추천 가능

4️⃣ 거리 계산 및 정렬

입력 벡터와 후보 벡터 간 유클리드 거리 (Euclidean distance) 계산
sort_by 옵션에 따라 거리, 보험료 차, 지급금액 차 기준으로 정렬

5️⃣ 결과 복원

인코딩된 상품명을 inverse_transform()으로 복원
→ 최종 표에는 원래 상품명 + 핵심 속성 출력

예시 결과
상품명	남자(보험료)	지급금액	나이	직업(원문)	직업 위험도(원문)
○○생명 종신보장형	45,000	10,000,000	25	사무직	낮음
△△생명 플러스형	48,000	9,500,000	26	사무직	낮음


주요 매개변수
매개변수	설명
gender_input	"남자", "여자", "M", "F" 등 입력 가능
premium	희망 월 보험료
coverage	원하는 보장금액
age	나이
job_text	직업명
k	추천 개수
sort_by	정렬 기준 (distance, premium, coverage)



