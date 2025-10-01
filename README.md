# 상해보험 맞춤 추천 API 

사용자의 **보장금액**과 **나이와 성별**으로 맞는 상해보험 상품 목록을 제공하여 추천하는 기능을 제공하는 API

-----

## 핵심 기능


  * **보장금액 많은 상품 추천**

      * 사용자의 입력 정보를 통해 **보장금액**을 기준으로 가장 높은 상품들을 사용자에게 제공함 
      * **보장금액 높은 순 (`coverage_desc`)** 또는 \*\*낮은 순 (`coverage_asc`)\*\*으로 상품을 정렬하여 사용자가 자신의 우선순위에 맞는 상품을 쉽게 찾도록 도와줌

  * **나이/성별에 따른 저렴한 보험료 추천**

      * 사용자의 **나이와 성별**을 핵심 조건으로 받아, 가입이 불가능한 상품은 사전에 추천하지 않도록 필터링
      * 상품의 상세 조건(`특이사항`)에 명시된 내용을 분석하여 실제 가입 가능한 상품만 추천 목록에 포함한다 

      * 정렬 옵션을 선택하지 않을 경우, 보장금액, 보험료(가성비), 갱신주기(안정성)를 종합적으로 평가한 객관적인 **추천 점수** 순으로 상품을 제시함

-----

## 보험 추천 기능 로직

**필수 조건 필터링(Filter)**, **점수 계산(Scoring)**, \*\*최종 정렬(Sorting)\*\*의 세 단계로 이루어짐

### 1\. 필수 조건 (Filter 단계)

API가 요청을 받으면, 아래 조건에 맞지 않는 상품은 추천 후보에서 **자동으로 제외**합니다.

  * **보장금액 필터링**: `coverage_amount`(보장금액) 정보가 누락된 상품은 신뢰할 수 없으므로 추천 후보에서 제외합니다.
  * **성별 필터링**: 요청한 성별의 보험료 정보가 없거나 가입이 불가능한 상품(예: 남성 전용 상품에 여성 사용자가 요청)을 제외합니다.
  * **나이 필터링**: 각 상품의 `special_notes`(특이사항)에 명시된 가입 가능 나이(`15세~80세` 등)를 분석하여, 사용자의 나이가 이 범위에 속하지 않는 상품을 제외합니다.


### 2\. 점수 계산 (Scoring 단계)

필터링을 통과한 상품들을 대상으로 아래 3가지 지표를 점수화하여 상품의 매력도를 평가합니다.

| 지표                  | 설명                                         | 기준                                                                 |
| :-------------------- | :------------------------------------------- | :------------------------------------------------------------------- |
| **보장금액 점수** (Coverage Score) | 상품의 기본적인 보장 수준을 평가합니다.            | 보장금액(`coverage_amount`)이 높을수록 높은 점수를 받습니다.         |
| **가치 점수** (Value Score)     | \*\*'가성비'\*\*를 평가합니다.                 | 평균 보험료(`avg_premium`)가 낮을수록 높은 점수를 받습니다.          |
| **안정성 점수** (Stability Score) | 상품의 **장기적 안정성**을 평가합니다. | 갱신주기(`renewal_cycle`)가 '비갱신형'일 경우 더 높은 점수를 받습니다. |

#### 최종 추천 점수

> **최종 점수** = (보장금액 점수 × 0.5) + (가치 점수 × 0.4) + (안정성 점수 × 0.1)

### 3\. 최종 정렬 (Sorting 단계)

사용자의 `sort_by` 요청 값에 따라 최종 순서를 결정합니다.

  * `default` (기본값): 위에서 계산된 **최종 점수**가 높은 순서대로 정렬합니다.
  * `coverage_desc`: **보장금액**이 높은 순서대로 정렬합니다.
  * `coverage_asc`: **보장금액**이 낮은 순서대로 정렬합니다.

-----

## 🚀 빠른 시작

### 설치 및 실행

```bash
# Python 의존성 설치
pip install -r requirements.txt

# API 서버 실행 (프로젝트 최상위 폴더에서)
uvicorn app.main:app --reload --port 8000
```

서버가 정상적으로 실행되면 **`http://localhost:8000`** 에서 접속할 수 있습니다.

### API 사용법

`POST` 요청을 통해 실시간으로 상해보험 상품을 추천받을 수 있습니다.

  * **Endpoint**: `POST http://localhost:8000/recommend/accident`
  * **Body 예시**:
    ```json
    {
      "age": 35,
      "sex": "F",
      "top_n": 5,
      "sort_by": "coverage_desc"
    }
    ```

-----

## 📁 프로젝트 구조

```
├── app/
│   ├── main.py                   # FastAPI 라우터 및 API 엔드포인트 정의
│   ├── recommendation_engine.py  # 핵심 추천 알고리즘 로직
│   ├── data_loader.py            # 데이터 로딩 및 전처리
│   └── models.py                 # API 요청/응답 데이터 모델 (Pydantic)
│
├── products/
│   └── accident_products.csv     # 상해보험 상품 데이터
│
├── requirements.txt              # Python 의존성 목록
└── run_server.py                 # 서버 실행 스크립트
```| **가치 점수** (Value Score)     | \*\*'가성비'\*\*를 평가합니다.                 | 평균 보험료(`avg_premium`)가 낮을수록 높은 점수를 받습니다.          |
| **안정성 점수** (Stability Score) | 상품의 **장기적 안정성**을 평가합니다. | 갱신주기(`renewal_cycle`)가 '비갱신형'일 경우 더 높은 점수를 받습니다. |

#### 최종 추천 점수

> **최종 점수** = (보장금액 점수 × 0.5) + (가치 점수 × 0.4) + (안정성 점수 × 0.1)

### 3\. 최종 정렬 (Sorting 단계)

사용자의 `sort_by` 요청 값에 따라 최종 순서를 결정합니다.

  * `default` (기본값): 위에서 계산된 **최종 점수**가 높은 순서대로 정렬합니다.
  * `coverage_desc`: **보장금액**이 높은 순서대로 정렬합니다.
  * `coverage_asc`: **보장금액**이 낮은 순서대로 정렬합니다.

-----

## 🚀 빠른 시작

### 설치 및 실행

```bash
# Python 의존성 설치
pip install -r requirements.txt

# API 서버 실행 (프로젝트 최상위 폴더에서)
uvicorn app.main:app --reload --port 8000
```

서버가 정상적으로 실행되면 **`http://localhost:8000`** 에서 접속할 수 있습니다.

### API 사용법

`POST` 요청을 통해 실시간으로 상해보험 상품을 추천받을 수 있습니다.

  * **Endpoint**: `POST http://localhost:8000/recommend/accident`
  * **Body 예시**:
    ```json
    {
      "age": 35,
      "sex": "F",
      "top_n": 5,
      "sort_by": "coverage_desc"
    }
    ```

-----

## 📁 프로젝트 구조

```
├── app/
│   ├── main.py                   # FastAPI 라우터 및 API 엔드포인트 정의
│   ├── recommendation_engine.py  # 핵심 추천 알고리즘 로직
│   ├── data_loader.py            # 데이터 로딩 및 전처리
│   └── models.py                 # API 요청/응답 데이터 모델 (Pydantic)
│
├── products/
│   └── accident_products.csv     # 상해보험 상품 데이터
│
├── requirements.txt              # Python 의존성 목록
└── run_server.py                 # 서버 실행 스크립트
```
2.  아래 명령어를 실행하여 데이터를 가공하고, `InsuranceWeb/products/accident_products.csv` 파일을 생성합니다.

    ```bash
    python app/converter.py
    ```

### 3단계: API 서버 실행

아래 명령어를 실행하여 API 서버를 시작합니다.

```bash
uvicorn app.main:app --reload --port 8000
```

서버가 정상적으로 실행되면 **`http://localhost:8000`** 에서 접속할 수 있습니다.

-----

## 📖 API 사용법

`POST` 요청을 통해 실시간으로 상해보험 상품을 추천받을 수 있습니다.

  * **Endpoint**: `POST http://localhost:8000/recommend/accident`
  * **Body 예시**:
    ```json
    {
      "age": 35,
      "sex": "F",
      "top_n": 5,
      "sort_by": "coverage_desc"
    }
    ```
  * API의 모든 기능은 **`http://localhost:8000/docs`** 에서 직접 테스트해볼 수 있습니다.    "stability_weight": 0.2,
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
