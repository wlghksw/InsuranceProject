from pydantic import BaseModel, Field
from typing import Optional, Tuple, Any, List
from enum import Enum


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
    smoker_flag: int = Field(0, description="흡연 여부 (0: 비흡연, 1: 흡연) - 기본값: 비흡연", example=0, ge=0, le=1)
    monthly_budget: int = Field(..., description="월 예산 (원)", example=50000, ge=10000, le=500000)
    min_coverage: Optional[int] = Field(None, description="최소 보장금액 (원 단위)", example=30000000)
    max_premium_avg: Optional[float] = Field(None, description="최대 평균 보험료 (원 단위)", example=20000)
    prefer_non_renewal: bool = Field(True, description="비갱신형 선호 여부")
    require_sales_channel: Optional[str] = Field(None, description="필요한 판매 채널", example="온라인")
    # 암보험 특화 조건들
    family_cancer_history: bool = Field(False, description="가족 암 병력 여부", example=False)
    preferred_coverage_period: Optional[str] = Field(None, description="선호 보장기간 (10년/20년/종신)", example="20년")
    cancer_type_preference: Optional[str] = Field(None, description="특정 암 종류 선호도 (전체/여성암/남성암/기타)", example="전체")
    premium_payment_method: Optional[str] = Field(None, description="보험료 납입 방법 (월납/연납/일시납)", example="월납")
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
    coverage_details: list[str] = Field(default_factory=list, description="주요 보장 내용")

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

# 연금 보험 추천 모델들
class SavingsPurpose(str, Enum):
    """연금 보험 가입 목적"""
    PENSION_PREPARATION = "연금준비"  # 연금 준비
    SHORT_TERM_SAVINGS = "단기저축"   # 단기 저축
    TAX_BENEFIT = "세제혜택"         # 세제 혜택

class SavingsRecommendationRequest(BaseModel):
    """연금 보험 추천 요청 모델"""
    age: int = Field(..., description="나이", example=35, ge=20, le=80)
    monthly_budget: int = Field(..., description="월 예산 (원)", example=300000, ge=100000, le=2000000)
    purpose: SavingsPurpose = Field(..., description="가입 목적", example=SavingsPurpose.PENSION_PREPARATION)
    preferred_term: Optional[int] = Field(None, description="선호 보험기간 (년)", example=10, ge=1, le=20)
    prefer_universal: Optional[bool] = Field(None, description="유니버셜 상품 선호 여부")
    min_guaranteed_rate: Optional[float] = Field(None, description="최소 보증이율", example=2.0, ge=0.0, le=5.0)
    top_n: int = Field(5, description="추천 상품 개수", ge=1, le=20)

class SavingsProductRecommendation(BaseModel):
    """연금 보험 상품 추천 정보"""
    product_id: str
    company: str
    product_name: str
    product_type: str
    score: float
    monthly_premium: str
    term: str
    accumulation_rate: str = "N/A"
    current_rate: str
    guaranteed_rate: str
    surrender_value: str
    payment_method: str
    universal: str
    sales_channel: str
    recommendation_reason: str

class SavingsRecommendationResponse(BaseModel):
    """연금 보험 추천 응답 모델"""
    success: bool
    message: str
    total_products: int
    recommendations: List[SavingsProductRecommendation]
    request_params: Optional[SavingsRecommendationRequest] = None

# === 종신보험 KNN 추천 모델 ===
class LifeInsuranceRequest(BaseModel):
    """종신보험 KNN 추천 요청 모델"""
    gender: str = Field(..., description="성별", example="남자")
    age: int = Field(..., description="나이", example=25, ge=18, le=80)
    job: str = Field(..., description="직업", example="사무직")
    desiredPremium: int = Field(..., description="희망 보험료", example=50000, ge=10000, le=1000000)
    desiredCoverage: int = Field(..., description="희망 보장금액", example=20000000, ge=5000000, le=100000000)
    topk: int = Field(5, description="추천 개수", ge=1, le=20)
    sortBy: str = Field("distance", description="정렬 기준 (distance/premium/coverage)")


class LifeInsuranceResponse(BaseModel):
    """종신보험 추천 응답 모델"""
    success: bool
    message: str
    total_products: int
    recommendations: List[dict]


