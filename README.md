# FastAPI 보험 추천 엔진 상세 문서

AI 기반 보험 상품 추천 시스템 - Python FastAPI 엔진

---

## 목차

- [엔진 개요](#엔진-개요)
- [1. 암보험 추천 엔진](#1-암보험-추천-엔진)
- [2. 종신보험 KNN 추천 엔진](#2-종신보험-knn-추천-엔진)
- [3. 연금보험 추천 엔진](#3-연금보험-추천-엔진)
- [4. 저축성보험 추천 엔진](#4-저축성보험-추천-엔진)
- [5. 상해보험 추천 엔진](#5-상해보험-추천-엔진)
- [알고리즘 비교](#알고리즘-비교)

---

## 엔진 개요

### 전체 구조

```
app/
├── main.py              FastAPI 메인 서버
├── cancer_engine.py     암보험 추천 엔진
├── life_engine.py       종신보험 KNN 추천 엔진 (AI)
├── pension_engine.py    연금보험 추천 엔진
├── savings_engine.py    저축성보험 추천 엔진
├── accident_engine.py   상해보험 추천 엔진
├── helpers.py           공통 헬퍼 함수
└── models.py            Pydantic 요청/응답 모델
```

### 엔진별 핵심 기술 요약

| 보험 종류      | 클래스명                    | 추천 방식                    | 핵심 알고리즘                    | 데이터 규모  |
| -------------- | --------------------------- | ---------------------------- | -------------------------------- | ------------ |
| **암보험**     | PersonalizedCancerEngine    | 개인화 필터 + 가중치 점수    | 4가지 점수 시스템, 다양성 보너스 | 96개 상품    |
| **종신보험**   | LifeInsuranceEngine         | **K-Nearest Neighbors (ML)** | StandardScaler, 유클리디안 거리  | 4,326개 상품 |
| **연금보험**   | SavingsRecommendationEngine | 프로필 기반 점수 계산        | 목적별 필터링, 4요소 점수        | 732개 상품   |
| **저축성보험** | SavingsInsuranceEngine      | 목적별 특화 + 정규화         | 6가지 목적, 0-100 정규화         | 146개 상품   |
| **상해보험**   | AccidentInsuranceEngine     | 간단한 점수 계산             | 3가지 점수 시스템                | 46개 상품    |

---

## 1. 암보험 추천 엔진

**파일:** `cancer_engine.py`  
**클래스:** `PersonalizedCancerEngine`  
**데이터:** `data/csv/cancer.csv` (96개 상품)

### 핵심 기술

#### 1-1. 개인화 필터링

사용자 특성에 따라 상품을 사전 필터링합니다.

**필터링 조건:**

| 사용자 특성          | 필터링 규칙             |
| -------------------- | ----------------------- |
| **나이 < 25세**      | 월 보험료 ≤ 50,000원    |
| **나이 ≥ 60세**      | 보장금액 ≥ 20,000,000원 |
| **성별 = 여성**      | 여성 특화 상품 우선     |
| **예산 < 20,000원**  | 월 보험료 ≤ 20,000원    |
| **예산 > 100,000원** | 보장금액 ≥ 30,000,000원 |
| **가족 암력 있음**   | 보장금액 ≥ 25,000,000원 |
| **흡연자**           | 보장금액 ≥ 20,000,000원 |

#### 1-2. 4가지 점수 계산 시스템

```python
# 1. 보장금액 점수 (25-40%)
coverage_score = (coverage_amount / max_coverage) * 100

# 2. 가성비 점수 (20-40%)
value_ratio = coverage_amount / (avg_premium + 1)
value_score = (value_ratio / max_value_ratio) * 100

# 3. 안정성 점수 (20-30%)
stability_score = 100 - ((avg_premium - min_premium) / (max_premium - min_premium) * 100)

# 4. 개인화 점수 (10-20%)
personalization_score = calculate_personalization_score()  # 최대 100점

# 최종 점수
final_score = (coverage_score × 가중치1 + value_score × 가중치2 +
               stability_score × 가중치3 + personalization_score × 가중치4)
```

#### 1-3. 가중치 자동 조정 시스템

사용자 특성에 따라 가중치를 동적으로 조정합니다.

**나이별 가중치:**

| 연령대  | 보장금액 | 가성비  | 안정성 | 개인화 |
| ------- | -------- | ------- | ------ | ------ |
| < 25세  | 20%      | **40%** | 20%    | 20%    |
| 25-59세 | 25%      | 35%     | 25%    | 15%    |
| ≥ 60세  | **40%**  | 20%     | 30%    | 10%    |

**추가 조정 요인:**

- 여성: 안정성 +10%, 개인화 +5%
- 저예산 (<20,000원): 가성비 +20%, 안정성 +10%
- 고예산 (>100,000원): 보장금액 +20%, 개인화 +10%
- 가족 암력: 보장금액 +15%, 개인화 +10%
- 흡연자: 보장금액 +15%, 안정성 +10%

#### 1-4. 다양성 보너스

```python
# 회사별 다양성 점수
diversity_bonus = (total_companies - company_rank) * 2

# 랜덤 요소 (맞춤형은 적게)
random_bonus = random.uniform(0, 5)

# 최종 점수에 반영
final_score += diversity_bonus + random_bonus
```

### 추천 알고리즘 흐름

```
1. 데이터 로드 (cancer.csv)
   ↓
2. 사용자 특성 기반 필터링
   - 나이, 성별, 예산, 가족 암력, 흡연 여부
   ↓
3. 가중치 자동 조정
   - 사용자 프로필에 맞는 가중치 계산
   ↓
4. 4가지 점수 계산
   - 보장금액, 가성비, 안정성, 개인화
   ↓
5. 다양성 보너스 추가
   - 회사별 분산, 랜덤 요소
   ↓
6. 상위 N개 추천
```

---

## 2. 종신보험 KNN 추천 엔진

**파일:** `life_engine.py`  
**클래스:** `LifeInsuranceEngine`  
**데이터:** `data/csv/analysis.csv` (4,326개 상품)

### 핵심 기술

#### 2-1. K-Nearest Neighbors 알고리즘 (머신러닝)

**기술 스택:**

- `sklearn.neighbors.NearestNeighbors` - KNN 모델
- `sklearn.preprocessing.StandardScaler` - 특징 정규화
- `sklearn.preprocessing.LabelEncoder` - 범주형 인코딩
- `difflib.get_close_matches` - 직업명 유사 매칭

#### 2-2. 5차원 특징 벡터

```python
feature_vector = [
    보험료,           # 희망 보험료
    지급금액,         # 희망 보장금액
    나이,            # 사용자 나이
    직업코드,        # 직업 (LabelEncoder)
    직업위험도        # 위험도 (LabelEncoder)
]
```

#### 2-3. 성별별 모델 분리

```python
# 여성 모델
df_female = insurance_df[insurance_df["성별"] == 0]
X_female = df_female[["여자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]]
scaler_female = StandardScaler().fit(X_female)
knn_female = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(X_female_scaled)

# 남성 모델
df_male = insurance_df[insurance_df["성별"] == 1]
X_male = df_male[["남자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]]
scaler_male = StandardScaler().fit(X_male)
knn_male = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(X_male_scaled)
```

#### 2-4. 추천 프로세스

```
1. 사용자 입력 받기
   - 성별, 나이, 직업, 희망 보험료, 희망 보장금액
   ↓
2. 직업 텍스트 → 직업 코드 변환 (LabelEncoder)
   - "사무직" → 숫자 코드
   - 유사 직업 매칭 (difflib)
   ↓
3. 직업 → 위험도 자동 추론
   - lookup table 기반
   ↓
4. 5차원 특징 벡터 생성
   [보험료, 지급금액, 나이, 직업코드, 위험도]
   ↓
5. StandardScaler로 정규화
   - 각 특징을 평균 0, 분산 1로 정규화
   ↓
6. 성별에 따라 KNN 모델 선택
   - 여성 → knn_female
   - 남성 → knn_male
   ↓
7. 희망 보험료 이하 상품만 필터링
   ↓
8. 유클리디안 거리 계산
   distance = sqrt(Σ(x_i - y_i)²)
   ↓
9. 정렬 기준 적용
   - distance: 종합 유사도
   - premium: 보험료 근접도
   - coverage: 보장금액 근접도
   ↓
10. 상위 K개 반환
```

#### 2-5. 유클리디안 거리 계산

```python
# 사용자 입력 벡터
user_vector = [50000, 20000000, 25, 3, 1]  # 예시

# 정규화
user_scaled = scaler.transform([user_vector])

# 모든 상품과의 거리 계산
distances = np.linalg.norm(X_pool_scaled - user_scaled, axis=1)

# 가까운 순으로 정렬
sorted_indices = np.argsort(distances)
```

#### 2-6. 정렬 옵션

| 옵션       | 정렬 기준       | 설명                                 |
| ---------- | --------------- | ------------------------------------ | --------------------------- | --- |
| `distance` | 유클리디안 거리 | 전체적으로 가장 유사한 상품 (기본값) |
| `premium`  | 보험료 근접도   | `                                    | 상품보험료 - 희망보험료     | `   |
| `coverage` | 보장금액 근접도 | `                                    | 상품보장금액 - 희망보장금액 | `   |

---

## 3. 연금보험 추천 엔진

**파일:** `pension_engine.py`  
**클래스:** `SavingsRecommendationEngine`  
**데이터:** `data/csv/savings.csv` (732개 상품)

### 핵심 기술

#### 3-1. 프로필 기반 추천 시스템

**3요소 분석:**

1. **나이** - 연령대별 추천 전략
2. **예산** - 월 예산 기반 필터링
3. **목적** - 연금준비/단기저축/세제혜택

#### 3-2. 4가지 점수 계산 시스템

```python
# 1. 수익률 점수 (40%)
rate_score = 현재공시이율 × 0.6 + 최저보증이율 × 0.4

# 2. 목적 적합성 점수 (30%)
purpose_score = calculate_purpose_score(목적)

# 3. 나이 적합성 점수 (20%)
age_score = calculate_age_score(나이)

# 4. 예산 적합성 점수 (10%)
budget_score = calculate_budget_score(예산)

# 최종 점수
final_score = rate_score × 0.4 + purpose_score × 0.3 +
              age_score × 0.2 + budget_score × 0.1
```

#### 3-3. 목적별 추천 로직

| 목적         | 우선 조건                    | 점수 배분        |
| ------------ | ---------------------------- | ---------------- |
| **연금준비** | 유지기간 ≥5년, 적립률 ≥100%  | 장기 안정성 중시 |
| **단기저축** | 유지기간 ≤3년, 해약환급금 高 | 빠른 회수 가능성 |
| **세제혜택** | 유니버셜 상품, 월납 방식     | 유연한 납입 조건 |

**연금준비 점수 계산:**

```python
if 유지기간 >= 5년:
    score += 30
if 적립률 >= 100%:
    score += 50
if 적립률 >= 90%:
    score += 30
```

**단기저축 점수 계산:**

```python
if 유지기간 <= 3년:
    score += 40
if 해약환급금 > 0:
    score += 30
```

**세제혜택 점수 계산:**

```python
if 유니버셜여부 == "유니버셜":
    score += 60
if "월납" in 납입방법:
    score += 20
```

#### 3-4. 나이별 추천 전략

| 연령대      | 전략          | 우선 조건                         |
| ----------- | ------------- | --------------------------------- |
| **< 30세**  | 높은 수익률   | 현재공시이율 ≥3.0%, 유지기간 ≥5년 |
| **30-49세** | 균형잡힌 접근 | 수익성 + 안정성                   |
| **≥ 50세**  | 안정성 최우선 | 최저보증이율 ≥2.0%, 유니버셜 상품 |

```python
if age < 30:
    # 젊은 연령대
    if 현재공시이율 >= 3.0:
        score += 50
    if 유지기간 >= 5:
        score += 30

elif age >= 50:
    # 중장년층
    if 최저보증이율 >= 2.0:
        score += 50
    if 유니버셜여부 == "유니버셜":
        score += 30
```

#### 3-5. 예산 필터링

**2단계 필터링:**

```python
# 월 예산 → 연간 예산 변환
annual_budget = monthly_budget × 12

# 1단계: 기본 범위 (50% ~ 200%)
budget_min = annual_budget × 0.5
budget_max = annual_budget × 2.0
filtered = df[(납입보험료 >= budget_min) & (납입보험료 <= budget_max)]

# 2단계: 결과가 없으면 전체 데이터 반환 (안전장치)
if filtered.empty:
    return all_data
```

---

## 4. 저축성보험 추천 엔진

**파일:** `savings_engine.py`  
**클래스:** `SavingsInsuranceEngine`  
**데이터:** `data/csv/savings_comparison.csv` (146개 상품)

### 핵심 기술

#### 4-1. 6가지 저축 목적 지원

| 목적         | 가중치 배분             | 추천 특징                   |
| ------------ | ----------------------- | --------------------------- |
| **단기저축** | 유연성 60% + 수익성 30% | 월납/전기납 우선, 빠른 회수 |
| **중기저축** | 안정성 50% + 유연성 30% | 균형잡힌 접근               |
| **장기저축** | 안정성 70% + 수익성 20% | 최저보증이율 높은 상품      |
| **교육자금** | 안정성 60% + 수익성 30% | 확실한 자금 마련            |
| **주택자금** | 안정성 50% + 유연성 40% | 중도 해지 가능성 고려       |
| **노후자금** | 안정성 80% + 수익성 15% | 확실한 노후 준비            |

#### 4-2. 정규화된 점수 계산 (0-100 스케일)

```python
# 정규화 함수
def normalize_score(series):
    if series.max() == series.min():
        return 50  # 모두 같으면 중간값
    return (series - series.min()) / (series.max() - series.min()) * 100

# 1. 수익성 점수
적립률_score = normalize_score(df['적립률']) * 0.6
이율_score = normalize_score(df['현재공시이율'].clip(0, 15)) * 0.4
return_score = 적립률_score + 이율_score

# 2. 안정성 점수
보증이율_score = normalize_score(df['최저보증이율']) * 0.7
기간_score = np.where((유지기간 >= 3) & (유지기간 <= 7), 100,
                     np.where(유지기간 < 3, 60, 80)) * 0.3
stability_score = 보증이율_score + 기간_score

# 3. 유연성 점수
flexibility_score = np.where(납입방법 in ['월납', '전기납'], 80, 40)

# 4. 최종 점수 (목적별 가중치 적용)
if purpose == "단기저축":
    final_score = flexibility_score × 0.6 + return_score × 0.3 + budget_score × 0.1
elif purpose == "장기저축":
    final_score = stability_score × 0.7 + return_score × 0.2 + flexibility_score × 0.1
```

#### 4-3. 일시납/월납 구분 처리

```python
def calculate_monthly_premium(row):
    if row['납입방법'] == '일시납':
        # 일시납은 총액 그대로
        return row['납입보험료']
    else:
        # 월납은 총액 ÷ (유지기간 × 12)
        term_months = row['유지기간'] × 12
        return row['납입보험료'] / term_months
```

**예산 필터링 (보수적 기준):**

| 납입방법        | 예산 기준 | 허용 범위                            |
| --------------- | --------- | ------------------------------------ |
| **월납/전기납** | 월 예산   | 월 납입금 ≤ 월 예산 × 1.1 (10% 여유) |
| **일시납**      | 연간 예산 | 총액 ≤ 월 예산 × 12 (1년치)          |

#### 4-4. 목적별 우선 필터링

```python
if purpose == "단기저축":
    # 월납/전기납 상품 우선 선택
    priority = df[df['납입방법'].isin(['월납', '전기납'])]

elif purpose == "장기저축":
    # 최저보증이율 높은 상품 우선
    priority = df[df['최저보증이율'] >= 1.0]

elif purpose == "노후자금":
    # 안정성 최우선
    priority = df[(df['최저보증이율'] >= 0.5) & (df['유지기간'] >= 5)]

elif purpose == "교육자금":
    # 수익성과 안정성 균형
    priority = df[(df['현재공시이율'] >= 2.0) & (df['최저보증이율'] >= 0.5)]
```

---

## 5. 상해보험 추천 엔진

**파일:** `accident_engine.py`  
**클래스:** `AccidentInsuranceEngine`  
**데이터:** `data/csv/accident.csv` (46개 상품)

### 핵심 기술

#### 5-1. 간단한 점수 계산 시스템

```python
# 1. 보장금액 점수 (50%)
coverage_score = coverage_amount / max_coverage

# 2. 가성비 점수 (40%)
value_score = 1 - (avg_premium / max_premium)

# 3. 안정성 점수 (10%)
stability_score = 1.0 if '비갱신' in renewal_cycle else 0.5

# 최종 점수
final_score = coverage_score × 0.5 +
              value_score × 0.4 +
              stability_score × 0.1
```

#### 5-2. 성별 보험료 구분

```python
# 성별에 따른 보험료 선택
if sex == 'male':
    selected_premium = male_premium
else:
    selected_premium = female_premium

# 평균 보험료 계산
avg_premium = (male_premium + female_premium) / 2
```

#### 5-3. 3가지 정렬 옵션

| 옵션       | 정렬 기준        | 사용 케이스        |
| ---------- | ---------------- | ------------------ |
| `default`  | 최종 점수 순     | 종합 평가 (기본값) |
| `premium`  | 보험료 낮은 순   | 가격 중시          |
| `coverage` | 보장금액 높은 순 | 보장 중시          |

```python
if sort_by == "premium":
    df = df.sort_values('avg_premium')
elif sort_by == "coverage":
    df = df.sort_values('coverage_amount', ascending=False)
else:  # default
    df = df.sort_values('final_score', ascending=False)
```

---

## 알고리즘 비교

### 복잡도 비교

| 엔진           | 알고리즘 복잡도 | 계산 방식              | 개인화 수준       |
| -------------- | --------------- | ---------------------- | ----------------- |
| **암보험**     | O(n)            | 필터링 + 점수 계산     | ★★★★★ (매우 높음) |
| **종신보험**   | O(n log n)      | KNN + 거리 계산        | ★★★☆☆ (중간)      |
| **연금보험**   | O(n)            | 프로필 점수 계산       | ★★★★☆ (높음)      |
| **저축성보험** | O(n)            | 정규화 + 목적별 가중치 | ★★★★☆ (높음)      |
| **상해보험**   | O(n)            | 간단한 점수 계산       | ★★☆☆☆ (낮음)      |

### 머신러닝 vs 규칙 기반

| 구분          | 엔진                     | 방식                              |
| ------------- | ------------------------ | --------------------------------- |
| **머신러닝**  | 종신보험                 | KNN, StandardScaler, LabelEncoder |
| **규칙 기반** | 암보험, 연금, 저축, 상해 | 가중치 점수 계산, 필터링          |

### 추천 속도

| 엔진       | 평균 처리 시간 | 병목 구간        |
| ---------- | -------------- | ---------------- |
| 암보험     | ~50ms          | 개인화 점수 계산 |
| 종신보험   | ~100ms         | KNN 거리 계산    |
| 연금보험   | ~30ms          | 점수 계산        |
| 저축성보험 | ~40ms          | 정규화           |
| 상해보험   | ~20ms          | 매우 단순        |

### 데이터 활용도

| 엔진           | 활용 필드 수 | 주요 활용 데이터                       |
| -------------- | ------------ | -------------------------------------- |
| **암보험**     | 10개         | 보장금액, 보험료, 갱신주기, 해약환급금 |
| **종신보험**   | 5개          | 보험료, 지급금액, 나이, 직업, 위험도   |
| **연금보험**   | 8개          | 유지기간, 납입보험료, 적립률, 공시이율 |
| **저축성보험** | 12개         | 유지기간, 납입방법, 적립률, 보증이율   |
| **상해보험**   | 6개          | 보장금액, 보험료, 갱신주기             |

---

## 기술 스택

### 공통 라이브러리

```python
import pandas as pd      # 데이터 처리
import numpy as np       # 수치 계산
import logging          # 로깅
```

### 종신보험 전용 (머신러닝)

```python
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from difflib import get_close_matches
```

### 데이터 출처

| 보험 종류  | CSV 파일               | 경로                            |
| ---------- | ---------------------- | ------------------------------- |
| 암보험     | cancer.csv             | data/csv/cancer.csv             |
| 종신보험   | analysis.csv           | data/csv/analysis.csv           |
| 연금보험   | savings.csv            | data/csv/savings.csv            |
| 저축성보험 | savings_comparison.csv | data/csv/savings_comparison.csv |
| 상해보험   | accident.csv           | data/csv/accident.csv           |

---

## 실행 방법

### 서버 실행

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### API 문서 확인

```
http://localhost:8002/docs
```

