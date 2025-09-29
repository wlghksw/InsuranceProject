# app/models.py

from pydantic import BaseModel, Field
from typing import Optional, Tuple, Any, List
from enum import Enum

# --- 정렬 순서 정의 Enum ---
class SortOrder(str, Enum):
    """추천 결과 정렬 순서 정의"""
    DEFAULT = "default"  # 기본값 (추천 점수 순)
    COVERAGE_DESC = "coverage_desc"  # 보장금액 높은 순
    COVERAGE_ASC = "coverage_asc"   # 보장금액 낮은 순

class RenewalPreference(str, Enum):
    NON_RENEWAL = "non_renewal"
    RENEWAL = "renewal"
    NEUTRAL = "neutral"

class RecommendationRequest(BaseModel):
    """암보험 상품 추천 요청 모델"""
    min_coverage: Optional[int] = Field(None, description="최소 보장금액 (원 단위)", example=30000000)
    max_premium_avg: Optional[float] = Field(None, description="최대 평균 보험료 (원 단위)", example=20000)
    prefer_non_renewal: bool = Field(True, description="비갱신형 선호 여부")
    require_sales_channel: Optional[str] = Field(None, description="필요한 판매 채널", example="온라인")
    sex: Optional[str] = Field(None, description="성별", example="M", pattern="^[MF]$")
    monthly_budget: Optional[int] = Field(None, description="월 예산 (원)", example=50000, ge=10000, le=500000)
    weights: Tuple[float, float, float] = Field((0.5, 0.3, 0.2), description="가중치 (보장금액, 가치, 안정성)")
    top_n: int = Field(10, description="추천 상품 개수", ge=1, le=50)
    # --- sort_by 필드 추가 ---
    sort_by: SortOrder = Field(SortOrder.DEFAULT, description="추천 정렬 순서 (default: 추천점수순, coverage_desc: 보장금액 높은순, coverage_asc: 보장금액 낮은순)")

    class Config:
        schema_extra = {
            "example": {
                "min_coverage": 50000000,
                "max_premium_avg": 30000,
                "prefer_non_renewal": True,
                "require_sales_channel": "온라인",
                "sex": "M",
                "monthly_budget": 40000,
                "weights": [0.6, 0.2, 0.2],
                "top_n": 5,
                "sort_by": "coverage_desc"
            }
        }

class UserProfileRecommendationRequest(BaseModel):
    """사용자 특성 기반 추천 요청 모델"""
    age: int = Field(..., example=40)
    sex: str = Field(..., example="M", pattern="^[MF]$")
    smoker_flag: int = Field(..., example=1)
    occupation_class: int = Field(..., example=1)
    monthly_budget: int = Field(..., example=70000)
    min_coverage: Optional[int] = Field(None, description="최소 보장금액 (원 단위)", example=30000000)
    max_premium_avg: Optional[float] = Field(None, description="최대 평균 보험료 (원 단위)", example=20000)
    prefer_non_renewal: bool = Field(True, description="비갱신형 선호 여부")
    require_sales_channel: Optional[str] = Field(None, description="필요한 판매 채널", example="온라인")
    top_n: int = Field(10, description="추천 상품 개수", ge=1, le=50)
    # --- sort_by 필드 추가 ---
    sort_by: SortOrder = Field(SortOrder.DEFAULT, description="추천 정렬 순서 (default: 추천점수순, coverage_desc: 보장금액 높은순, coverage_asc: 보장금액 낮은순)")

    class Config:
        schema_extra = {
            "example": {
                "age": 35,
                "sex": "M",
                "smoker_flag": 0,
                "occupation_class": 0,
                "monthly_budget": 50000,
                "min_coverage": 30000000,
                "max_premium_avg": 20000,
                "prefer_non_renewal": True,
                "require_sales_channel": "온라인",
                "top_n": 10,
                "sort_by": "default"
            }
        }

class AccidentRecommendationRequest(BaseModel):
    """상해보험 상품 추천 요청 모델"""
    age: int = Field(30, description="사용자 나이")
    sex: str = Field("M", description="성별 (M/F)", pattern="^[MF]$")
    top_n: int = Field(5, description="추천 상품 개수", ge=1, le=50)
    # --- sort_by 필드 추가 ---
    sort_by: SortOrder = Field(SortOrder.DEFAULT, description="추천 정렬 순서 (default: 추천점수순, coverage_desc: 보장금액 높은순, coverage_asc: 보장금액 낮은순)")

    class Config:
        schema_extra = {
            "example": { "age": 35, "sex": "M", "top_n": 5, "sort_by": "coverage_desc" }
        }

class ProductRecommendation(BaseModel):
    """추천 상품 정보"""
    policy_id: int
    insurance_company: str
    product_name: str
    coverage_amount: int
    male_premium: Optional[float]
    female_premium: Optional[float]
    avg_premium: Optional[float]
    renewal_cycle: str
    surrender_value: str
    sales_channel: str
    coverage_score: float
    value_score: float
    stability_score: float
    final_score: float

class RecommendationResponse(BaseModel):
    """추천 API 응답 모델"""
    success: bool
    message: str
    total_products: int
    recommendations: List[ProductRecommendation]
    request_params: Optional[Any] = None

class HealthCheckResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    message: str
    data_loaded: bool