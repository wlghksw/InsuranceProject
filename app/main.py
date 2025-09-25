from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from .models import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthCheckResponse,
    ProductRecommendation,
    UserProfileRecommendationRequest,
    SavingsRecommendationRequest,
    SavingsRecommendationResponse
)
from .data_loader import DataLoader
from .recommendation_engine import RecommendationEngine
from .user_behavior_engine import UserBehaviorEngine

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="암보험 상품 추천 API",
    description="사용자 조건에 맞는 암보험 상품을 추천하는 API",
    version="1.0.0",
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
data_loader = None
recommendation_engine = None
user_behavior_engine = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 로드"""
    global data_loader, recommendation_engine, user_behavior_engine
    try:
        logger.info("데이터 로딩 시작...")
        data_loader = DataLoader()
        recommendation_engine = RecommendationEngine(data_loader)
        
        # 사용자 행동 데이터 엔진 초기화
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
    # 기본 가중치: 보장금액 40%, 가치 30%, 안정성 30%
    coverage_weight = 0.4
    value_weight = 0.3
    stability_weight = 0.3
    
    # 나이에 따른 조정
    if age < 30:
        # 젊은 층: 가성비 중시
        coverage_weight = 0.3
        value_weight = 0.5
        stability_weight = 0.2
    elif age >= 50:
        # 중장년층: 안정성 중시
        coverage_weight = 0.4
        value_weight = 0.2
        stability_weight = 0.4
    
    # 흡연 여부에 따른 조정
    if smoker_flag == 1:
        # 흡연자: 보장금액 중시
        coverage_weight = min(0.6, coverage_weight + 0.1)
        value_weight = max(0.2, value_weight - 0.05)
        stability_weight = max(0.2, stability_weight - 0.05)
    
    # 직업에 따른 조정
    if occupation_class == 1:  # 전문직
        # 전문직: 안정성 중시
        stability_weight = min(0.5, stability_weight + 0.1)
        coverage_weight = max(0.3, coverage_weight - 0.05)
    elif occupation_class == 2:  # 관리직
        # 관리직: 균형
        pass  # 기본 가중치 유지
    
    # 예산에 따른 조정
    if monthly_budget < 30000:
        # 낮은 예산: 가성비 중시
        value_weight = min(0.6, value_weight + 0.1)
        coverage_weight = max(0.2, coverage_weight - 0.05)
    elif monthly_budget > 100000:
        # 높은 예산: 보장금액과 안정성 중시
        coverage_weight = min(0.6, coverage_weight + 0.1)
        stability_weight = min(0.4, stability_weight + 0.05)
        value_weight = max(0.2, value_weight - 0.05)
    
    # 가중치 정규화 (합이 1이 되도록)
    total = coverage_weight + value_weight + stability_weight
    return (coverage_weight/total, value_weight/total, stability_weight/total)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return HealthCheckResponse(
        status="healthy",
        message="암보험 상품 추천 API가 정상적으로 실행 중입니다",
        data_loaded=data_loader.is_data_loaded() if data_loader else False
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    return HealthCheckResponse(
        status="healthy",
        message="API가 정상적으로 작동 중입니다",
        data_loaded=data_loader.is_data_loaded() if data_loader else False
    )

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_products(
    request: RecommendationRequest,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    암보험 상품 추천
    
    사용자의 조건에 맞는 암보험 상품을 추천합니다.
    """
    try:
        logger.info(f"추천 요청 받음: {request.dict()}")
        
        # 추천 상품 조회
        recommendations = engine.recommend_products(
            min_coverage=request.min_coverage,
            max_premium_avg=request.max_premium_avg,
            prefer_non_renewal=request.prefer_non_renewal,
            require_sales_channel=request.require_sales_channel,
            sex=request.sex,
            monthly_budget=request.monthly_budget,
            weights=request.weights,
            top_n=request.top_n
        )
        
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


@app.post("/recommend/user-profile", response_model=RecommendationResponse)
async def get_user_profile_recommendations(
    request: UserProfileRecommendationRequest,
    behavior_engine: UserBehaviorEngine = Depends(get_user_behavior_engine)
):
    """
    사용자 특성 기반 추천 (사용자 행동 데이터 활용)
    
    나이, 성별, 흡연여부, 직업, 예산 등 사용자 특성을 직접 입력받아 
    실제 사용자 행동 데이터를 기반으로 한 맞춤형 암보험 상품을 추천합니다.
    """
    try:
        logger.info(f"사용자 특성 기반 추천 요청 받음: age={request.age}, sex={request.sex}, {request.dict()}")
        
        # 사용자 행동 데이터 기반 추천
        recommendations = behavior_engine.get_user_profile_recommendations(
            age=request.age,
            sex=request.sex,
            smoker_flag=request.smoker_flag,
            monthly_budget=request.monthly_budget,
            top_n=request.top_n
        )
        
        # ProductRecommendation 형태로 변환
        product_recommendations = []
        for rec in recommendations:
            product_recommendations.append(ProductRecommendation(
                policy_id=rec.get('policy_id'),
                insurance_company=rec.get('insurance_company'),
                product_name=rec.get('product_name'),
                coverage_amount=rec.get('coverage_amount'),
                male_premium=rec.get('male_premium'),
                female_premium=rec.get('female_premium'),
                avg_premium=rec.get('avg_premium'),
                renewal_cycle=rec.get('renewal_cycle'),
                surrender_value=rec.get('surrender_value'),
                sales_channel=rec.get('sales_channel'),
                coverage_score=rec.get('coverage_score', 0),
                value_score=rec.get('value_score', 0),
                stability_score=rec.get('stability_score', 0),
                final_score=rec.get('final_score', 0)
            ))
        
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

@app.get("/analytics/summary")
async def get_analytics_summary():
    """
    추천 시스템 분석 요약
    
    기본 분석 결과를 제공합니다.
    """
    try:
        # 기본 분석 결과 반환
        summary = {
            "total_products": len(data_loader.products) if data_loader else 0,
            "total_companies": len(set(p.get('insurance_company', '') for p in data_loader.products)) if data_loader else 0,
            "average_coverage": sum(p.get('coverage_amount', 0) for p in data_loader.products) / len(data_loader.products) if data_loader and data_loader.products else 0,
            "status": "active"
        }
        return summary
    except Exception as e:
        logger.error(f"분석 요약 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 요약 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/products/sample", response_model=List[ProductRecommendation])
async def get_sample_products(
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    샘플 상품 조회 (모든 조건 없이 상위 5개)
    """
    try:
        recommendations = engine.recommend_products(top_n=5)
        return recommendations
    except Exception as e:
        logger.error(f"샘플 상품 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"샘플 상품 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/analytics/user-behavior")
async def get_user_behavior_analytics():
    """
    사용자 행동 데이터 분석
    """
    try:
        if user_behavior_engine is None:
            raise HTTPException(status_code=500, detail="사용자 행동 엔진이 초기화되지 않았습니다")
        
        analytics = user_behavior_engine.get_analytics_summary()
        return analytics
        
    except Exception as e:
        logger.error(f"사용자 행동 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 행동 분석 실패: {str(e)}")

@app.get("/debug/user-behavior")
async def debug_user_behavior():
    """
    사용자 행동 데이터 디버깅
    """
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

# 저축성보험 추천 엔드포인트
@app.post("/savings/recommend", response_model=SavingsRecommendationResponse)
async def get_savings_recommendations(request: SavingsRecommendationRequest):
    """저축성보험 상품 추천"""
    try:
        logger.info(f"저축성보험 추천 요청 받음: {request.dict()}")
        
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="추천 엔진이 초기화되지 않았습니다.")
        
        # 저축성보험 추천 로직 (기존 암보험 추천 로직을 활용)
        recommendations = recommendation_engine.get_savings_recommendations(request)
        
        response = SavingsRecommendationResponse(
            success=True,
            message=f"저축성보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
        
        logger.info(f"저축성보험 추천 상품 {len(recommendations)}개 반환")
        return response
        
    except Exception as e:
        logger.error(f"저축성보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저축성보험 추천 중 오류가 발생했습니다: {str(e)}")


@app.post("/savings/profile-recommend", response_model=SavingsRecommendationResponse)
async def get_savings_profile_recommendations(request: UserProfileRecommendationRequest):
    """사용자 특성 기반 저축성보험 추천"""
    try:
        logger.info(f"사용자 특성 기반 저축성보험 추천 요청 받음: {request.dict()}")
        
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="추천 엔진이 초기화되지 않았습니다.")
        
        # 사용자 특성 기반 저축성보험 추천 로직
        recommendations = recommendation_engine.get_savings_profile_recommendations(request)
        
        response = SavingsRecommendationResponse(
            success=True,
            message=f"사용자 특성 기반 저축성보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            total_products=len(recommendations),
            recommendations=recommendations
        )
        
        logger.info(f"사용자 특성 기반 저축성보험 추천 상품 {len(recommendations)}개 반환")
        return response
        
    except Exception as e:
        logger.error(f"사용자 특성 기반 저축성보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 특성 기반 저축성보험 추천 중 오류가 발생했습니다: {str(e)}")


@app.get("/savings/analytics/summary")
async def get_savings_analytics_summary():
    """저축성보험 분석 요약 정보 조회"""
    try:
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="추천 엔진이 초기화되지 않았습니다.")
        
        summary = recommendation_engine.get_savings_analytics_summary()
        return summary
        
    except Exception as e:
        logger.error(f"저축성보험 분석 요약 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저축성보험 분석 요약 조회 중 오류가 발생했습니다: {str(e)}")


@app.get("/savings/products")
async def get_savings_products():
    """저축성보험 상품 목록 조회"""
    try:
        if not recommendation_engine:
            raise HTTPException(status_code=503, detail="추천 엔진이 초기화되지 않았습니다.")
        
        products = recommendation_engine.get_savings_products()
        return products
        
    except Exception as e:
        logger.error(f"저축성보험 상품 목록 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저축성보험 상품 목록 조회 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
