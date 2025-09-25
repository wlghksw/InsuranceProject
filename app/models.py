from pydantic import BaseModel, Field
from typing import Optional, Tuple, Any, List
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


class SavingsRecommendationRequest(BaseModel):
    """저축성보험 상품 추천 요청 모델"""
    monthly_budget: int = Field(..., description="월 예산 (원)", example=50000, ge=10000, le=500000)
    preferred_term: int = Field(..., description="선호하는 보험기간 (년)", example=15, ge=10, le=30)
    min_guaranteed_rate: float = Field(..., description="최저 보증이율", example=0.025, ge=0.0, le=0.1)
    min_refund_10y: float = Field(..., description="10년 환급률", example=0.90, ge=0.0, le=1.0)
    need_extra_contribution: bool = Field(False, description="추가납입 필요 여부")
    need_partial_withdrawal: bool = Field(False, description="부분인출 필요 여부")
    need_premium_holiday: bool = Field(False, description="납입유예 필요 여부")
    weights: dict = Field({
        "return": 0.3,
        "refund": 0.3,
        "tax": 0.2,
        "flex": 0.2
    }, description="가중치 (수익률, 환급률, 세제혜택, 유연성)")
    top_n: int = Field(10, description="추천 상품 개수", ge=1, le=50)

    class Config:
        schema_extra = {
            "example": {
                "monthly_budget": 50000,
                "preferred_term": 15,
                "min_guaranteed_rate": 0.025,
                "min_refund_10y": 0.90,
                "need_extra_contribution": True,
                "need_partial_withdrawal": False,
                "need_premium_holiday": True,
                "weights": {
                    "return": 0.3,
                    "refund": 0.3,
                    "tax": 0.2,
                    "flex": 0.2
                },
                "top_n": 10
            }
        }


class SavingsProductRecommendation(BaseModel):
    """저축성보험 상품 추천 정보"""
    product_id: str
    company: str
    product_name: str
    product_type: str
    score: float
    guaranteed_rate: str
    current_rate: str
    pay_period: str
    term: str
    monthly_premium_estimate: str
    annual_savings: str
    surrender_5y: str
    surrender_10y: str
    extra_contribution: str
    partial_withdrawal: str
    premium_holiday: str
    tax_benefit: str
    replacement_reason: str


class SavingsRecommendationResponse(BaseModel):
    """저축성보험 추천 응답 모델"""
    success: bool
    message: str
    total_products: int
    recommendations: List[SavingsProductRecommendation]
    request_params: Optional[SavingsRecommendationRequest] = None
