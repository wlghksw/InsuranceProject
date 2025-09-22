from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from .models import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthCheckResponse,
    ProductRecommendation
)
from .data_loader import DataLoader
from .recommendation_engine import RecommendationEngine

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

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 로드"""
    global data_loader, recommendation_engine
    try:
        logger.info("데이터 로딩 시작...")
        data_loader = DataLoader()
        recommendation_engine = RecommendationEngine(data_loader)
        logger.info("데이터 로딩 완료")
    except Exception as e:
        logger.error(f"데이터 로딩 실패: {str(e)}")
        raise e

def get_recommendation_engine() -> RecommendationEngine:
    """추천 엔진 의존성 주입"""
    if recommendation_engine is None:
        raise HTTPException(status_code=500, detail="추천 엔진이 초기화되지 않았습니다")
    return recommendation_engine

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
