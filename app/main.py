from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import importlib
import sys

from models import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthCheckResponse,
    ProductRecommendation,
    UserProfileRecommendationRequest,
    SavingsRecommendationRequest,
    SavingsRecommendationResponse,
    LifeInsuranceRequest,
    LifeInsuranceResponse
)
from helpers import (
    handle_recommendation_request,
    handle_simple_dict_request,
    handle_analytics_request,
    convert_to_product_recommendation
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="보험 상품 추천 API",
    description="사용자 조건에 맞는 보험 상품을 추천하는 통합 API",
    version="2.0.0",
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
savings_engine = None
cancer_engine = None
simple_cancer_engine = None
life_engine = None
accident_engine = None


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 모든 엔진 초기화"""
    global savings_engine, simple_cancer_engine, cancer_engine, life_engine, accident_engine
    
    try:
        logger.info("=" * 50)
        logger.info("보험 추천 API 서버 시작 중...")
        logger.info("=" * 50)
        
        # 연금 보험 엔진
        try:
            from pension_engine import SavingsRecommendationEngine
            savings_engine = SavingsRecommendationEngine()
            logger.info("✓ 연금보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"✗ 연금보험 추천 엔진 초기화 실패: {e}")
            savings_engine = None
        
        # 암보험 엔진
        try:
            from cancer_engine import PersonalizedCancerEngine
            cancer_engine = PersonalizedCancerEngine()
            simple_cancer_engine = PersonalizedCancerEngine()
            logger.info("✓ 암보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"✗ 암보험 추천 엔진 초기화 실패: {e}")
            cancer_engine = None
            simple_cancer_engine = None
        
        # 저축성보험 엔진
        try:
            from savings_engine import SavingsInsuranceEngine
            savings_engine = SavingsInsuranceEngine()
            logger.info("✓ 저축성보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"✗ 저축성보험 추천 엔진 초기화 실패: {e}")
            savings_engine = None
        
        # 종신보험 KNN 엔진
        try:
            from life_engine import LifeInsuranceEngine
            life_engine = LifeInsuranceEngine()
            logger.info("✓ 종신보험 KNN 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"✗ 종신보험 KNN 추천 엔진 초기화 실패: {e}")
            life_engine = None
        
        # 상해보험 엔진
        try:
            from accident_engine import AccidentInsuranceEngine
            accident_engine = AccidentInsuranceEngine()
            logger.info("✓ 상해보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"✗ 상해보험 추천 엔진 초기화 실패: {e}")
            accident_engine = None
        
        logger.info("=" * 50)
        logger.info("모든 엔진 초기화 완료! 서버 준비됨")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"서버 초기화 중 치명적 오류 발생: {str(e)}")
        raise e


# ============================================================
# 헬스체크 엔드포인트
# ============================================================

@app.get("/", response_model=HealthCheckResponse)
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return HealthCheckResponse(
        status="healthy",
        message="보험 상품 추천 API가 정상적으로 실행 중입니다",
        data_loaded=cancer_engine is not None and cancer_engine.df is not None
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    return HealthCheckResponse(
        status="healthy",
        message="API가 정상적으로 작동 중입니다",
        data_loaded=cancer_engine is not None and cancer_engine.df is not None
    )


# ============================================================
# 암보험 추천 엔드포인트
# ============================================================

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest):
    """암보험 상품 추천 (기본)"""
    return handle_recommendation_request(
        simple_cancer_engine,
        request,
        "암보험",
        RecommendationResponse
    )


@app.post("/recommend/user-profile", response_model=RecommendationResponse)
async def get_user_profile_recommendations(request: UserProfileRecommendationRequest):
    """암보험 상품 추천 (사용자 프로필 기반 - 강화된 개인화)"""
    
    # 프로필 기반 추천은 특별 처리
    try:
        logger.info(f"사용자 프로필 기반 추천 요청: age={request.age}, sex={request.sex}")
        
        if cancer_engine is None:
            raise HTTPException(status_code=503, detail="암보험 추천 엔진이 초기화되지 않았습니다.")
        
        recommendations = cancer_engine.get_recommendations(request)
        
        # ProductRecommendation 형태로 변환
        product_recommendations = convert_to_product_recommendation(
            recommendations, 
            ProductRecommendation
        )
        
        logger.info(f"맞춤형 추천 상품 {len(product_recommendations)}개 반환")
        
        return RecommendationResponse(
            success=True,
            message=f"총 {len(product_recommendations)}개의 맞춤형 상품을 추천했습니다 (강화된 개인화 알고리즘 기반)",
            total_products=len(product_recommendations),
            recommendations=product_recommendations,
            request_params=request
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 프로필 기반 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")


@app.get("/analytics/summary")
async def get_analytics_summary():
    """암보험 분석 요약"""
    try:
        if cancer_engine is None or cancer_engine.df is None:
            return {
                "total_products": 0,
                "total_companies": 0,
                "average_coverage": 0,
                "status": "inactive"
            }
        
        df = cancer_engine.df
        summary = {
            "total_products": len(df),
            "total_companies": df['insurance_company'].nunique(),
            "average_coverage": int(df['coverage_amount'].mean()),
            "status": "active"
        }
        return summary
    except Exception as e:
        logger.error(f"분석 요약 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 요약 조회 중 오류가 발생했습니다: {str(e)}")


@app.get("/products/sample", response_model=List[ProductRecommendation])
async def get_sample_products():
    """샘플 상품 조회 (상위 5개)"""
    try:
        if simple_cancer_engine is None:
            raise HTTPException(status_code=503, detail="암보험 추천 엔진이 초기화되지 않았습니다.")
        
        request = RecommendationRequest(
            min_coverage=0,
            max_premium_avg=100000,
            prefer_non_renewal=True,
            require_sales_channel="",
            sex=None,
            monthly_budget=None,
            weights=(30.0, 50.0, 20.0),
            top_n=5
        )
        recommendations = simple_cancer_engine.get_recommendations(request)
        return recommendations
    except Exception as e:
        logger.error(f"샘플 상품 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"샘플 상품 조회 중 오류가 발생했습니다: {str(e)}")


# ============================================================
# 연금 보험 추천 엔드포인트
# ============================================================

@app.post("/savings/recommend", response_model=SavingsRecommendationResponse)
async def get_savings_recommendations(request: SavingsRecommendationRequest):
    """연금 보험 상품 추천"""
    try:
        logger.info(f"연금보험 추천 요청: 나이={request.age}, 예산={request.monthly_budget}, 목적={request.purpose}")
        
        if savings_engine is None:
            raise HTTPException(status_code=503, detail="연금보험 추천 엔진이 초기화되지 않았습니다.")
        
        # 연금 보험 추천 (개별 파라미터 전달)
        recommendations = savings_engine.get_recommendations(
            age=request.age,
            monthly_budget=request.monthly_budget,
            purpose=request.purpose.value,
            top_n=request.top_n
        )
        
        logger.info(f"연금보험 추천 완료: {len(recommendations)}개")
        
        return SavingsRecommendationResponse(
            success=True,
            message=f"연금보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"연금보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연금보험 추천 중 오류가 발생했습니다: {str(e)}")


@app.get("/savings/analytics")
async def get_savings_analytics():
    """연금 보험 분석 요약"""
    return handle_analytics_request(savings_engine, "연금보험")


# ============================================================
# 상해보험 추천 엔드포인트
# ============================================================

@app.post("/recommend/accident")
async def get_accident_recommendations(request: dict):
    """상해보험 추천"""
    try:
        age = request.get("age", 30)
        sex = request.get("sex", "male")
        top_n = request.get("top_n", 5)
        sort_by = request.get("sort_by", "default")
        
        logger.info(f"상해보험 추천 요청: 나이={age}, 성별={sex}, 상품수={top_n}")
        
        if accident_engine is None:
            raise HTTPException(status_code=503, detail="상해보험 추천 엔진이 초기화되지 않았습니다.")
        
        recommendations = accident_engine.get_recommendations(
            age=age,
            sex=sex,
            top_n=top_n,
            sort_by=sort_by
        )
        
        return {
            "success": True,
            "message": f"상해보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            "total_products": len(recommendations),
            "recommendations": recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상해보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상해보험 추천 중 오류가 발생했습니다: {str(e)}")


# ============================================================
# 저축성보험 추천 엔드포인트
# ============================================================

@app.post("/recommend/savings-insurance")
async def get_savings_insurance_recommendations(request: dict):
    """저축성보험 추천"""
    return handle_simple_dict_request(savings_engine, request, "저축성보험")


@app.get("/savings-insurance/analytics")
async def get_savings_insurance_analytics():
    """저축성보험 분석 요약"""
    return handle_analytics_request(savings_engine, "저축성보험")


# ============================================================
# 종신보험 KNN 추천 엔드포인트
# ============================================================

@app.post("/recommend/life", response_model=LifeInsuranceResponse)
async def recommend_life_insurance(request: LifeInsuranceRequest):
    """종신보험 KNN 추천 (머신러닝 기반)"""
    try:
        if life_engine is None:
            raise HTTPException(status_code=503, detail="종신보험 추천 엔진이 초기화되지 않았습니다.")
        
        logger.info(f"종신보험 추천 요청: 성별={request.gender}, 나이={request.age}, 직업={request.job}")
        
        recommendations = life_engine.recommend(
            gender_input=request.gender,
            premium=request.desiredPremium,
            coverage=request.desiredCoverage,
            age=request.age,
            job_text=request.job,
            k=request.topk,
            sort_by=request.sortBy
        )
        
        logger.info(f"종신보험 추천 성공: {len(recommendations)}개 상품")
        
        return LifeInsuranceResponse(
            success=True,
            message=f"종신보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            total_products=len(recommendations),
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"종신보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"종신보험 추천 중 오류가 발생했습니다: {str(e)}")


# ============================================================
# 관리자 기능
# ============================================================

@app.post("/admin/reload-data")
async def reload_data():
    """관리자용: 모든 엔진 데이터 재로딩"""
    global savings_engine, simple_cancer_engine, cancer_engine, accident_engine, life_engine
    
    try:
        logger.info("=" * 50)
        logger.info("관리자 요청: 데이터 재로딩 시작...")
        logger.info("=" * 50)
        
        reloaded_engines = []
        
        # 각 엔진별 재로딩
        engines_to_reload = [
            ('cancer_engine', 'PersonalizedCancerEngine', '암보험 추천 엔진'),
            ('savings_engine', 'SavingsInsuranceEngine', '저축성보험 추천 엔진'),
            ('pension_engine', 'SavingsRecommendationEngine', '연금보험 추천 엔진'),
            ('accident_engine', 'AccidentInsuranceEngine', '상해보험 추천 엔진'),
            ('life_engine', 'LifeInsuranceEngine', '종신보험 KNN 추천 엔진'),
        ]
        
        for module_name, class_name, display_name in engines_to_reload:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                
                module = __import__(module_name, fromlist=[class_name])
                engine_class = getattr(module, class_name)
                
                # 엔진별로 적절한 전역 변수에 할당
                if module_name == 'cancer_engine':
                    cancer_engine = engine_class()
                    simple_cancer_engine = engine_class()
                elif module_name == 'savings_engine':
                    savings_engine = engine_class()
                elif module_name == 'pension_engine':
                    savings_engine = engine_class()
                elif module_name == 'accident_engine':
                    accident_engine = engine_class()
                elif module_name == 'life_engine':
                    life_engine = engine_class()
                
                reloaded_engines.append(display_name)
                logger.info(f"✓ {display_name} 재로딩 완료")
                
            except Exception as e:
                logger.warning(f"✗ {display_name} 재로딩 실패: {e}")
        
        logger.info("=" * 50)
        logger.info(f"데이터 재로딩 완료! 재로딩된 엔진: {len(reloaded_engines)}개")
        logger.info("=" * 50)
        
        return {
            "success": True,
            "message": "데이터가 성공적으로 재로딩되었습니다.",
            "reloaded_engines": reloaded_engines,
            "total_reloaded": len(reloaded_engines)
        }
        
    except Exception as e:
        logger.error(f"데이터 재로딩 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 재로딩 중 오류가 발생했습니다: {str(e)}")


# ============================================================
# 메인 실행부
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
