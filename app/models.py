from pydantic import BaseModel, Field
from typing import Optional, Tuple, Any
from enum import Enum

class RenewalPreference(str, Enum):
    NON_RENEWAL = "non_renewal"  # 비갱신형 선호
    RENEWAL = "renewal"          # 갱신형 선호
    NEUTRAL = "neutral"          # 중립

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

    class Config:
        schema_extra = {
            "example": {
                "min_coverage": 30000000,
                "max_premium_avg": 20000,
                "prefer_non_renewal": True,
                "require_sales_channel": "온라인",
                "sex": "M",
                "monthly_budget": 50000,
                "weights": [0.5, 0.3, 0.2],
                "top_n": 10
            }
        }


class UserProfileRecommendationRequest(BaseModel):
    """사용자 특성 기반 추천 요청 모델"""
    age: int = Field(..., description="나이", example=35, ge=18, le=80)
    sex: str = Field(..., description="성별", example="M", pattern="^[MF]$")
    smoker_flag: int = Field(0, description="흡연 여부 (0: 비흡연, 1: 흡연)", example=0, ge=0, le=1)
    monthly_budget: int = Field(..., description="월 예산 (원)", example=50000, ge=10000, le=500000)
    min_coverage: Optional[int] = Field(None, description="최소 보장금액 (원 단위)", example=30000000)
    max_premium_avg: Optional[float] = Field(None, description="최대 평균 보험료 (원 단위)", example=20000)
    prefer_non_renewal: bool = Field(True, description="비갱신형 선호 여부")
    require_sales_channel: Optional[str] = Field(None, description="필요한 판매 채널", example="온라인")
    top_n: int = Field(10, description="추천 상품 개수", ge=1, le=50)

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
                "top_n": 10
            }
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
    """추천 결과 응답 모델"""
    success: bool
    message: str
    total_products: int
    recommendations: list[ProductRecommendation]
    request_params: Any

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    message: str
    data_loaded: bool
