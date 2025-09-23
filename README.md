# 암보험 상품 추천 API

효율성 중심의 암보험 상품 추천 시스템

## 🎯 추천 규칙

### 1. 필수 조건 (Filter 단계)

가입 가능성 보장을 위한 필수 필터링:

- **나이 범위**: `min_age ≤ 사용자 나이 ≤ max_age`
- **보장금액 범위**: `min_coverage ≤ coverage_amount ≤ max_coverage`
- **상품 판매 상태**: `sales_date` (현재 판매 중인 상품만)
- **제외 조건**: `special_notes` (특정 질환자 제외 등)

→ 이 조건을 통과하지 못한 상품은 자동 제외

### 2. 효율성 지표 (Ranking 단계)

남은 상품을 점수화하여 우선순위 부여:

#### 보장금액 점수 (Coverage Score)

- 일반암 진단비(`coverage_name`에 "일반암") 기준
- `payment_amount`가 클수록 높은 점수

#### 보험료 대비 효율성 (Value Score)

- **공식**: `보장금액 ÷ 월 보험료`
- 같은 보장이라면 보험료가 저렴할수록 유리

#### 상품 안정성 (Stability Score)

- 해약환급금(`surrender_value`)이 높을수록 점수 ↑
- 갱신주기(`renewal_cycle`)가 길수록 점수 ↑ (갱신형 < 종신형/정기형)

### 3. 최종 추천 점수

```
최종점수 = (Coverage Score × 0.5)
         + (Value Score × 0.3)
         + (Stability Score × 0.2)
```

## 🚀 빠른 시작

### 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python run_server.py
```

서버: `http://localhost:8001`

### API 사용

```http
POST http://localhost:8001/recommend
Content-Type: application/json

{
    "min_coverage": 30000000,
    "max_premium_avg": 50000,
    "prefer_non_renewal": true,
    "coverage_weight": 0.5,
    "value_weight": 0.3,
    "stability_weight": 0.2,
    "top_n": 10
}
```

## 📁 핵심 파일

- `app/main.py` - FastAPI 서버
- `app/recommendation_engine.py` - 추천 알고리즘
- `app/data_loader.py` - 데이터 처리
- `products/` - 암보험 상품 데이터 (CSV)
- `requirements.txt` - Python 의존성

## 💡 핵심 특징

- **가입 불가 상품 자동 제외**: 필수 조건 미달 시 자동 필터링
- **효율성 우선**: 보험료 대비 보장금액이 높은 상품 우선 추천
- **실제 가입 가능성**: 사용자가 실제 가입할 확률이 높은 상품 상위 노출
