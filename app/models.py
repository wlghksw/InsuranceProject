from pydantic import BaseModel, Field
from typing import Optional, Tuple
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
    weights: Tuple[float, float, float] = Field((0.5, 0.3, 0.2), description="가중치 (보장금액, 가치, 안정성)")
    top_n: int = Field(10, description="추천 상품 개수", ge=1, le=50)

    class Config:
        schema_extra = {
            "example": {
                "min_coverage": 30000000,
                "max_premium_avg": 20000,
                "prefer_non_renewal": True,
                "require_sales_channel": "온라인",
                "weights": [0.5, 0.3, 0.2],
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
    request_params: RecommendationRequest

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    message: str
    data_loaded: bool
