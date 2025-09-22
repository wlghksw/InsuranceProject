# 암보험 상품 추천 API

사용자의 조건에 맞는 암보험 상품을 추천하는 REST API 서비스입니다.

## 주요 기능

- **사용자 맞춤 추천**: 최소 보장금액, 최대 보험료, 갱신형/비갱신형 선호도, 판매채널 등 사용자 조건에 따른 상품 추천
- **다중 점수 시스템**: 보장금액, 가치(보장금액/보험료), 안정성(갱신형/해약환급금) 점수를 가중치로 조합
- **실시간 필터링**: 가입 자격 요건 및 사용자 조건에 따른 실시간 상품 필터링
- **RESTful API**: FastAPI 기반의 표준 REST API 제공

## 프로젝트 구조

```
Insurance/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션
│   ├── models.py            # Pydantic 모델 정의
│   ├── data_loader.py       # 데이터 로딩 및 전처리
│   └── recommendation_engine.py  # 추천 알고리즘
├── products/
│   ├── cancer_coverages.csv
│   ├── cancer_eligibility.csv
│   ├── cancer_policies.csv
│   └── cancer_rates.csv
├── requirements.txt
└── README.md
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 직접 실행
python -m app.main
```

### 3. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 1. 헬스체크

```http
GET /health
```

서버 상태 및 데이터 로드 상태를 확인합니다.

### 2. 상품 추천

```http
POST /recommend
```

사용자 조건에 맞는 암보험 상품을 추천합니다.

#### 요청 예시

```json
{
  "min_coverage": 30000000,
  "max_premium_avg": 20000,
  "prefer_non_renewal": true,
  "require_sales_channel": "온라인",
  "weights": [0.5, 0.3, 0.2],
  "top_n": 10
}
```

#### 요청 파라미터

| 파라미터                | 타입   | 필수 | 설명                                                      | 예시            |
| ----------------------- | ------ | ---- | --------------------------------------------------------- | --------------- |
| `min_coverage`          | int    | 선택 | 최소 보장금액 (원 단위)                                   | 30000000        |
| `max_premium_avg`       | float  | 선택 | 최대 평균 보험료 (원 단위)                                | 20000           |
| `prefer_non_renewal`    | bool   | 선택 | 비갱신형 선호 여부 (기본값: true)                         | true            |
| `require_sales_channel` | string | 선택 | 필요한 판매 채널                                          | "온라인"        |
| `weights`               | array  | 선택 | 가중치 [보장금액, 가치, 안정성] (기본값: [0.5, 0.3, 0.2]) | [0.5, 0.3, 0.2] |
| `top_n`                 | int    | 선택 | 추천 상품 개수 (기본값: 10, 최대: 50)                     | 10              |

#### 응답 예시

```json
{
  "success": true,
  "message": "총 5개의 상품을 추천했습니다",
  "total_products": 5,
  "recommendations": [
    {
      "policy_id": 1,
      "insurance_company": "한화생명",
      "product_name": "한화생명 장애인전용 곰두리보장보험 무배당",
      "coverage_amount": 10000000,
      "male_premium": 26400.0,
      "female_premium": 28200.0,
      "avg_premium": 27300.0,
      "renewal_cycle": "비갱신형",
      "surrender_value": "만기환급",
      "sales_channel": "대면채널",
      "coverage_score": 0.8,
      "value_score": 0.7,
      "stability_score": 0.9,
      "final_score": 0.8
    }
  ],
  "request_params": { ... }
}
```

### 3. 샘플 상품 조회

```http
GET /products/sample
```

모든 조건 없이 상위 5개 상품을 조회합니다.

## 추천 알고리즘

### 1. 필터링 단계

1. **가입 자격 필터**: `cancer_eligibility` 테이블의 보장금액 범위 내 상품만 통과
2. **사용자 조건 필터**:
   - 최소 보장금액 이상
   - 최대 평균 보험료 이하
   - 지정된 판매채널 (선택사항)

### 2. 점수 계산

1. **보장금액 점수 (Coverage Score)**: 보장금액이 높을수록 높은 점수
2. **가치 점수 (Value Score)**: 보장금액 ÷ 평균보험료 (효율성)
3. **안정성 점수 (Stability Score)**:
   - 비갱신형 선호도 (70%)
   - 해약환급금 보조 (30%)

### 3. 최종 점수

```
final_score = w1 × coverage_score + w2 × value_score + w3 × stability_score
```

## 사용 예시

### Python 클라이언트 예시

```python
import requests

# 추천 요청
response = requests.post(
    "http://localhost:8000/recommend",
    json={
        "min_coverage": 30000000,
        "max_premium_avg": 20000,
        "prefer_non_renewal": True,
        "top_n": 5
    }
)

result = response.json()
print(f"추천 상품 수: {result['total_products']}")
for product in result['recommendations']:
    print(f"- {product['insurance_company']}: {product['product_name']}")
    print(f"  보장금액: {product['coverage_amount']:,}원")
    print(f"  평균보험료: {product['avg_premium']:,.0f}원")
    print(f"  최종점수: {product['final_score']:.3f}")
```

### cURL 예시

```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "min_coverage": 50000000,
    "max_premium_avg": 40000,
    "prefer_non_renewal": false,
    "weights": [0.6, 0.25, 0.15],
    "top_n": 10
  }'
```

## 개발자 정보

- **프레임워크**: FastAPI
- **데이터 처리**: Pandas, NumPy
- **데이터 검증**: Pydantic
- **서버**: Uvicorn

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
