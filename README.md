## 종신 보험 맞춤 추천 (Life Insurance Recommender)

간단한 KNN 기반의 종신보험 추천 시스템입니다.
CSV의 스키마에 맞춰 라벨 인코딩과 스케일링을 수행하고,
사용자의 입력(성별, 희망 보험료, 지급금액, 나이, 직업)을 기준으로 가장 가까운 상품 Top-K를 추천합니다.

🧩 추천 로직

성별 분리 스케일링:
남/녀 데이터를 분리하고 각각 StandardScaler로 정규화 후, KNN 거리 기반 근접도 계산

직업 위험도 추정:
직업명 → 위험도 매핑이 불확실할 경우, 동일 직업군의 위험도 mode 값 사용

정렬 옵션:

distance (기본): 전체 피처 거리

premium: 보험료 차이 절댓값

coverage: 지급금액 차이 절댓값

상품명 복원:
내부적으로 LabelEncoder로 인코딩하지만, 출력 시 원래 상품명으로 복원

📂 Repository 구조
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

⚙️ 의존성
from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
import pandas as pd
from difflib import get_close_matches
from sklearn.preprocessing import LabelEncoder, StandardScaler

🧠 역할
모듈	용도
pandas, numpy	데이터 핸들링
difflib.get_close_matches	문자열 근사 매칭 (직업명 유사 검색)
LabelEncoder, StandardScaler	범주형 인코딩 / 수치 정규화

💡 주의:
LabelEncoder는 “문자열 → 정수” 변환용이며, 숫자 크기에 의미는 없음.
따라서 거리 계산에는 직접 사용하지 않고 설명 필드용으로만 유지합니다.

🧱 클래스 구조
SortBy = Literal["distance", "premium", "coverage"]

@dataclass
class _Encoders:
    job: LabelEncoder
    jobrisk: LabelEncoder
    product: LabelEncoder
    gender: LabelEncoder

class Recommender:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.enc: Optional[_Encoders] = None
        self.df_f = self.df_m = None
        self.scaler_f = self.scaler_m = None
        self.X_f_scaled = self.X_m_scaled = None
        self.job2risk_lookup: Optional[dict] = None


4종 인코더(직업, 직업 위험도, 상품명, 성별)를 통합 관리

성별별로 풀을 분리하고 각각 StandardScaler로 정규화

fit_csv() → CSV 로드 및 인코딩

recommend_top_k() → 입력값 기반 추천 수행

🧩 전처리 및 학습
fit_csv / fit_df
def fit_csv(self, csv_path: str) -> "Recommender":
    df = pd.read_csv(csv_path)
    return self.fit_df(df)

def fit_df(self, df: pd.DataFrame) -> "Recommender":
    required = ["상품명","성별","남자(보험료)","여자(보험료)","지급금액","가입금액","나이","직업","직업 위험도"]

    # 라벨 인코딩
    job = LabelEncoder(); jobrisk = LabelEncoder()
    product = LabelEncoder(); gender = LabelEncoder()

    df["직업"] = job.fit_transform(df["직업"].astype(str))
    df["직업 위험도"] = jobrisk.fit_transform(df["직업 위험도"].astype(str))
    df["상품명"] = product.fit_transform(df["상품명"].astype(str))
    df["성별"] = gender.fit_transform(df["성별"].astype(str))

    self.enc = _Encoders(job=job, jobrisk=jobrisk, product=product, gender=gender)

    # 직업→위험도 룩업, 성별 풀 분리
    self.job2risk_lookup = self._build_job_to_risk_lookup(df)
    self.df_f = df[df["성별"] == 0].copy()
    self.df_m = df[df["성별"] == 1].copy()
    self._fit_gender_pool()

⚖️ 성별별 스케일링
def _fit_gender_pool(self):
    # Female
    X_f = self.df_f[["여자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
    self.scaler_f = StandardScaler().fit(X_f)
    self.X_f_scaled = self.scaler_f.transform(X_f)

    # Male
    X_m = self.df_m[["남자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
    self.scaler_m = StandardScaler().fit(X_m)
    self.X_m_scaled = self.scaler_m.transform(X_m)

💡 추천 함수 예시
res = recommender.recommend_top_k(
    gender_input="남자",
    premium=50000,
    coverage=10000000,
    age=25,
    job_text="사무직",
    k=10,                # 추천 개수
    sort_by="distance"   # 정렬 기준: "distance" | "premium" | "coverage"
)
print(res)

🚀 실행 순서
# 1. 환경 설정
pip install -r requirements.txt

# 2. CSV 파일 준비
# 예: ./insurance_core.csv

# 3. 실행
python scripts/demo.py

🔍 구현 포인트 요약
항목	설명
LabelEncoder	문자열을 숫자로 변환 (직업, 위험도, 상품, 성별)
StandardScaler	성별별 피처 스케일 통일
get_close_matches	직업명 오타/근사 대응
직업→위험도	동일 직업군의 최빈(mode) 위험도 추정
정렬 옵션	거리·보험료·지급금액 기준 선택 가능
상품명 복원	추천 결과에 실제 상품명 표시
🧮 예시 결과
상품명	남자(보험료)	지급금액	나이	직업(원문)	직업 위험도(원문)
○○생명 종신보장형	45,000	10,000,000	25	사무직	낮음
△△생명 플러스형	48,000	9,500,000	26	사무직	낮음
...	...	...	...	...	...
