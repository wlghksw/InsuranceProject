# app/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging

from .models import (
    RecommendationRequest,
    RecommendationResponse,
    HealthCheckResponse,
    ProductRecommendation,
    UserProfileRecommendationRequest,
    AccidentRecommendationRequest
)
from .data_loader import DataLoader
from .recommendation_engine import RecommendationEngine
from .user_behavior_engine import UserBehaviorEngine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="통합 보험 상품 추천 API",
    description="사용자 조건에 맞는 암보험 및 상해보험 상품을 추천하는 API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
data_loader: Optional[DataLoader] = None
recommendation_engine: Optional[RecommendationEngine] = None
user_behavior_engine: Optional[UserBehaviorEngine] = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 로드"""
    global data_loader, recommendation_engine, user_behavior_engine
    try:
        logger.info("데이터 로딩 시작...")
        data_loader = DataLoader()
        recommendation_engine = RecommendationEngine(data_loader)
        user_behavior_engine = UserBehaviorEngine(data_loader)
        user_behavior_engine.load_user_behavior_data()
        logger.info("데이터 로딩 완료")
    except Exception as e:
        logger.error(f"데이터 로딩 실패: {str(e)}")
        raise e

def get_recommendation_engine() -> RecommendationEngine:
    """추천 엔진 의존성 주입"""
    if recommendation_engine is None:
        raise HTTPException(status_code=500, detail="추천 엔진이 초기화되지 않았습니다")
    return recommendation_engine

def get_user_behavior_engine() -> UserBehaviorEngine:
    """사용자 행동 엔진 의존성 주입"""
    if user_behavior_engine is None:
        raise HTTPException(status_code=500, detail="사용자 행동 엔진이 초기화되지 않았습니다")
    return user_behavior_engine

def calculate_weights_for_user_profile(age, sex, smoker_flag, occupation_class, monthly_budget):
    """사용자 특성에 따라 가중치를 계산"""
    coverage_weight, value_weight, stability_weight = 0.4, 0.3, 0.3

    if age < 30:
        coverage_weight, value_weight, stability_weight = 0.3, 0.5, 0.2
    elif age >= 50:
        coverage_weight, value_weight, stability_weight = 0.4, 0.2, 0.4

    if smoker_flag == 1:
        coverage_weight = min(0.6, coverage_weight + 0.1)
        value_weight = max(0.2, value_weight - 0.05)
        stability_weight = max(0.2, stability_weight - 0.05)

    if occupation_class == 1:
        stability_weight = min(0.5, stability_weight + 0.1)
        coverage_weight = max(0.3, coverage_weight - 0.05)

    if monthly_budget < 30000:
        value_weight = min(0.6, value_weight + 0.1)
        coverage_weight = max(0.2, coverage_weight - 0.05)
    elif monthly_budget > 100000:
        coverage_weight = min(0.6, coverage_weight + 0.1)
        stability_weight = min(0.4, stability_weight + 0.05)
        value_weight = max(0.2, value_weight - 0.05)

    total = coverage_weight + value_weight + stability_weight
    return (coverage_weight/total, value_weight/total, stability_weight/total)

@app.get("/", response_model=HealthCheckResponse, tags=["System"])
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return HealthCheckResponse(
        status="healthy",
        message="통합 보험 상품 추천 API가 정상적으로 실행 중입니다",
        data_loaded=data_loader.is_data_loaded() if data_loader else False
    )

@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """헬스체크 엔드포인트"""
    return HealthCheckResponse(
        status="healthy",
        message="API가 정상적으로 작동 중입니다",
        data_loaded=data_loader.is_data_loaded() if data_loader else False
    )

@app.post("/recommend", response_model=RecommendationResponse, tags=["Cancer Insurance"])
async def recommend_products(
        request: RecommendationRequest,
        engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """암보험 상품 추천 (기존 기능)"""
    try:
        logger.info(f"암보험 추천 요청 받음: {request.dict()}")
        recommendations = engine.recommend_products(**request.dict())
        logger.info(f"추천 상품 {len(recommendations)}개 반환")
        return RecommendationResponse(
            success=True,
            message=f"총 {len(recommendations)}개의 상품을 추천했습니다",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
    except Exception as e:
        logger.error(f"추천 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/recommend/user-profile", response_model=RecommendationResponse, tags=["Cancer Insurance"])
async def get_user_profile_recommendations(
        request: UserProfileRecommendationRequest,
        behavior_engine: UserBehaviorEngine = Depends(get_user_behavior_engine)
):
    """사용자 특성 기반 암보험 추천 (기존 기능)"""
    try:
        logger.info(f"사용자 특성 기반 추천 요청 받음: {request.dict()}")
        recommendations_data = behavior_engine.get_user_profile_recommendations(**request.dict())

        product_recommendations = [
            ProductRecommendation(**rec) for rec in recommendations_data
        ]

        logger.info(f"사용자 특성 기반 추천 상품 {len(product_recommendations)}개 반환")
        return RecommendationResponse(
            success=True,
            message=f"총 {len(product_recommendations)}개의 맞춤형 상품을 추천했습니다 (사용자 행동 데이터 기반)",
            total_products=len(product_recommendations),
            recommendations=product_recommendations,
            request_params=request
        )
    except Exception as e:
        logger.error(f"사용자 특성 기반 추천 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 특성 기반 추천 처리 중 오류가 발생했습니다: {str(e)}")

# --- ✨ 여기에 새로운 상해보험 API 엔드포인트를 추가! ✨ ---
@app.post("/recommend/accident", response_model=RecommendationResponse, tags=["Accident Insurance"])
async def recommend_accident_products(
        request: AccidentRecommendationRequest,
        engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """상해보험 상품 추천 (신규 기능)"""
    try:
        logger.info(f"상해보험 추천 요청 받음: {request.dict()}")
        recommendations = engine.recommend_accident_products(**request.dict())
        logger.info(f"상해보험 추천 상품 {len(recommendations)}개 반환")
        return RecommendationResponse(
            success=True,
            message=f"총 {len(recommendations)}개의 상해보험 상품을 추천했습니다",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
    except Exception as e:
        logger.error(f"상해보험 추천 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상해보험 추천 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/analytics/summary", tags=["Analytics"])
async def get_analytics_summary():
    """추천 시스템 분석 요약"""
    try:
        summary = {
            "total_products": len(data_loader.products) if data_loader else 0,
            "total_companies": len(set(p.get('insurance_company', '') for p in data_loader.products)) if data_loader else 0,
            "average_coverage": sum(p.get('coverage_amount', 0) for p in data_loader.products if p.get('coverage_amount')) / len(data_loader.products) if data_loader and data_loader.products else 0,
            "status": "active"
        }
        return summary
    except Exception as e:
        logger.error(f"분석 요약 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 요약 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/products/sample", response_model=List[ProductRecommendation], tags=["Products"])
async def get_sample_products(
        engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """샘플 상품 조회 (모든 조건 없이 상위 5개)"""
    try:
        recommendations = engine.recommend_products(top_n=5)
        return recommendations
    except Exception as e:
        logger.error(f"샘플 상품 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"샘플 상품 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/analytics/user-behavior", tags=["Analytics"])
async def get_user_behavior_analytics():
    """사용자 행동 데이터 분석"""
    try:
        if user_behavior_engine is None:
            raise HTTPException(status_code=500, detail="사용자 행동 엔진이 초기화되지 않았습니다")

        analytics = user_behavior_engine.get_analytics_summary()
        return analytics
    except Exception as e:
        logger.error(f"사용자 행동 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 행동 분석 실패: {str(e)}")

@app.get("/debug/user-behavior", tags=["Debug"])
async def debug_user_behavior():
    """사용자 행동 데이터 디버깅"""
    try:
        if user_behavior_engine is None:
            return {"error": "사용자 행동 엔진이 초기화되지 않았습니다"}

        debug_info = {
            "user_profiles_loaded": user_behavior_engine.user_profiles is not None,
            "user_events_loaded": user_behavior_engine.user_events is not None,
            "user_item_matrix_loaded": user_behavior_engine.user_item_matrix is not None,
            "user_profiles_count": len(user_behavior_engine.user_profiles) if user_behavior_engine.user_profiles is not None else 0,
            "user_events_count": len(user_behavior_engine.user_events) if user_behavior_engine.user_events is not None else 0,
            "user_item_matrix_shape": user_behavior_engine.user_item_matrix.shape if user_behavior_engine.user_item_matrix is not None else "None"
        }
        return debug_info
    except Exception as e:
        logger.error(f"사용자 행동 디버깅 실패: {str(e)}")
        return {"error": f"사용자 행동 디버깅 실패: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)