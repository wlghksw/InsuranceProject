from fastapi import FastAPI, HTTPException, Depends
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
# from data_loader import DataLoader
# from basic_engine import SimpleRecommendationEngine
# from pension_engine import SavingsRecommendationEngine
# from simple_cancer_fix import SimpleCancerFix

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
simple_engine = None
savings_engine = None
savings_engine = None  # 저축성보험 추천 엔진
cancer_engine = None
cancer_engine = None  # 맞춤형 추천 전용 엔진
simple_cancer_engine = None  # 간단한 암보험 추천 엔진
accident_engine = None  # 상해보험 추천 엔진
life_engine = None  # 종신보험 KNN 추천 엔진

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 로드"""
    global data_loader, simple_engine, savings_engine, savings_engine, simple_cancer_engine, cancer_engine, life_engine
    try:
        logger.info("데이터 로딩 시작...")
        # data_loader 초기화
        try:
            from data_loader import DataLoader
            data_loader = DataLoader()
        except Exception as e:
            logger.warning(f"데이터 로더 초기화 실패: {e}")
            data_loader = None
        
        # 간단한 추천 엔진 초기화
        try:
            from basic_engine import SimpleRecommendationEngine
            simple_engine = SimpleRecommendationEngine()
        except Exception as e:
            logger.warning(f"간단한 추천 엔진 초기화 실패: {e}")
            simple_engine = None
        
        # 연금 보험 추천 엔진 초기화
        try:
            from pension_engine import SavingsRecommendationEngine
            savings_engine = SavingsRecommendationEngine()
        except Exception as e:
            logger.warning(f"연금 보험 추천 엔진 초기화 실패: {e}")
            savings_engine = None
        
        # 간단한 암보험 추천 엔진 초기화 (보장금액 추천용)
        logger.info("암보험 추천 엔진 초기화 시작...")
        try:
            from cancer_engine import PersonalizedCancerEngine
            cancer_engine = PersonalizedCancerEngine()
            logger.info("암보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"암보험 추천 엔진 초기화 실패: {e}")
            cancer_engine = None
        
        # 맞춤형 암보험 추천 엔진 초기화 (맞춤형 추천용)
        logger.info("맞춤형 암보험 추천 엔진 초기화 시작...")
        try:
            from cancer_engine import PersonalizedCancerEngine
            cancer_engine = PersonalizedCancerEngine()
            simple_cancer_engine = PersonalizedCancerEngine()  # 간단한 추천용으로도 사용
            logger.info("맞춤형 암보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"맞춤형 암보험 추천 엔진 초기화 실패: {e}")
            cancer_engine = None
            simple_cancer_engine = None
        
        # 저축성보험 추천 엔진 초기화
        logger.info("저축성보험 추천 엔진 초기화 시작...")
        try:
            from savings_engine import SavingsInsuranceEngine
            savings_engine = SavingsInsuranceEngine()
            logger.info("저축성보험 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"저축성보험 추천 엔진 초기화 실패: {e}")
            savings_engine = None
        
        # 종신보험 KNN 엔진 초기화
        try:
            from life_engine import LifeInsuranceEngine
            life_engine = LifeInsuranceEngine()
            logger.info("종신보험 KNN 추천 엔진 초기화 완료")
        except Exception as e:
            logger.warning(f"종신보험 KNN 추천 엔진 초기화 실패: {e}")
            life_engine = None
        
        logger.info("데이터 로딩 완료")
    except Exception as e:
        logger.error(f"데이터 로딩 실패: {str(e)}")
        raise e



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
async def recommend_products(request: RecommendationRequest):
    """
    암보험 상품 추천
    
    사용자의 조건에 맞는 암보험 상품을 추천합니다.
    """
    try:
        logger.info(f"추천 요청 받음: {request.dict()}")
        
        # 추천 상품 조회 (새로운 간단한 엔진 사용)
        if simple_cancer_engine is None:
            logger.error("SimpleCancerEngine이 초기화되지 않았습니다.")
            raise HTTPException(status_code=503, detail="암보험 추천 엔진이 초기화되지 않았습니다.")
        
        recommendations = simple_cancer_engine.get_recommendations(request)
        
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
    request: UserProfileRecommendationRequest
):
    """
    사용자 특성 기반 추천 (사용자 행동 데이터 활용)
    
    나이, 성별, 흡연여부, 직업, 예산 등 사용자 특성을 직접 입력받아 
    실제 사용자 행동 데이터를 기반으로 한 맞춤형 암보험 상품을 추천합니다.
    """
    try:
        logger.info(f"사용자 특성 기반 추천 요청 받음: age={request.age}, sex={request.sex}, {request.dict()}")
        
        # 맞춤형 추천 엔진 사용
        if cancer_engine is None:
            raise HTTPException(status_code=503, detail="맞춤형 추천 엔진이 초기화되지 않았습니다.")
        
        # 맞춤형 암보험 추천 엔진을 사용하여 개인화된 추천 생성
        recommendations = cancer_engine.get_recommendations(request)
        
        # ProductRecommendation 형태로 변환
        product_recommendations = []
        for rec in recommendations:
            # rec이 이미 ProductRecommendation 객체인 경우 그대로 사용
            if hasattr(rec, 'policy_id'):
                product_recommendations.append(rec)
            else:
                # 딕셔너리인 경우 ProductRecommendation으로 변환
                avg_premium = (rec.get('male_premium', 0) + rec.get('female_premium', 0)) / 2
                
                product_recommendations.append(ProductRecommendation(
                    policy_id=0,
                    insurance_company=rec.get('insurance_company'),
                    product_name=rec.get('product_name'),
                    coverage_amount=rec.get('coverage_amount'),
                    male_premium=rec.get('male_premium'),
                    female_premium=rec.get('female_premium'),
                    avg_premium=avg_premium,
                    renewal_cycle=rec.get('renewal_cycle'),
                    surrender_value='',
                    sales_channel=rec.get('sales_channel'),
                    coverage_score=0.0,
                    value_score=0.0,
                    stability_score=0.0,
                    final_score=rec.get('recommendation_score', 0),
                    coverage_details=[]
                ))
        
        logger.info(f"맞춤형 추천 상품 {len(product_recommendations)}개 반환")
        
        return RecommendationResponse(
            success=True,
            message=f"총 {len(product_recommendations)}개의 맞춤형 상품을 추천했습니다 (강화된 개인화 알고리즘 기반)",
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
async def get_sample_products():
    """
    샘플 상품 조회 (모든 조건 없이 상위 5개)
    """
    try:
        if simple_cancer_engine is None:
            raise HTTPException(status_code=503, detail="암보험 추천 엔진이 초기화되지 않았습니다.")
        
        # 기본 요청으로 샘플 상품 조회
        from models import RecommendationRequest
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
        logger.error(f"샘플 상품 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"샘플 상품 조회 중 오류가 발생했습니다: {str(e)}")



@app.post("/recommend/simple", response_model=RecommendationResponse)
async def get_simple_recommendations(request: UserProfileRecommendationRequest):
    """간단한 사용자 프로필 기반 추천"""
    try:
        logger.info(f"간단한 추천 요청: 나이={request.age}, 성별={request.sex}, 예산={request.monthly_budget}")
        
        # 간단한 추천 엔진 사용
        recommendations = simple_engine.get_recommendations(
            age=request.age,
            sex=request.sex,
            monthly_budget=request.monthly_budget,
            family_cancer_history=request.family_cancer_history,
            preferred_coverage_period=request.preferred_coverage_period,
            top_n=request.top_n
        )
        
        # 추천 결과를 ProductRecommendation 객체로 변환
        product_recommendations = []
        for rec in recommendations:
            # 평균 보험료 계산
            avg_premium = (rec.get('male_premium', 0) + rec.get('female_premium', 0)) / 2
            
            product_rec = ProductRecommendation(
                policy_id=0,  # 간단한 추천에서는 policy_id 없음
                insurance_company=rec.get('insurance_company', ''),
                product_name=rec.get('product_name', ''),
                coverage_amount=rec.get('coverage_amount', 0),
                male_premium=rec.get('male_premium', 0),
                female_premium=rec.get('female_premium', 0),
                avg_premium=avg_premium,
                renewal_cycle=rec.get('renewal_cycle', ''),
                sales_channel=rec.get('sales_channel', ''),
                surrender_value='',
                final_score=rec.get('recommendation_score', 0.0),
                coverage_score=0.0,
                value_score=0.0,
                stability_score=0.0,
                coverage_details=[]
            )
            product_recommendations.append(product_rec)
        
        logger.info(f"간단한 추천 상품 {len(product_recommendations)}개 반환")
        return RecommendationResponse(
            recommendations=product_recommendations,
            success=True,
            message="추천이 성공적으로 생성되었습니다",
            total_products=len(product_recommendations),
            request_params={
                "age": request.age,
                "sex": request.sex,
                "monthly_budget": request.monthly_budget,
                "family_cancer_history": request.family_cancer_history,
                "preferred_coverage_period": request.preferred_coverage_period
            }
        )
        
    except Exception as e:
        logger.error(f"간단한 추천 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")

# 연금 보험 추천 엔드포인트
@app.post("/savings/recommend", response_model=SavingsRecommendationResponse)
async def get_savings_recommendations(request: SavingsRecommendationRequest):
    """연금 보험 상품 추천"""
    try:
        logger.info(f"연금 보험 추천 요청: 나이={request.age}, 예산={request.monthly_budget}, 목적={request.purpose}")
        
        if not savings_engine:
            raise HTTPException(status_code=503, detail="연금 보험 추천 엔진이 초기화되지 않았습니다.")
        
        # 연금 보험 추천 로직
        recommendations = savings_engine.get_recommendations(
            age=request.age,
            monthly_budget=request.monthly_budget,
            purpose=request.purpose.value,
            top_n=request.top_n
        )
        
        response = SavingsRecommendationResponse(
            success=True,
            message=f"연금 보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
        
        logger.info(f"연금 보험 추천 상품 {len(recommendations)}개 반환")
        return response
        
    except Exception as e:
        logger.error(f"연금 보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연금 보험 추천 중 오류가 발생했습니다: {str(e)}")

@app.get("/savings/analytics")
async def get_savings_analytics():
    """연금 보험 분석 요약 정보"""
    try:
        if not savings_engine:
            raise HTTPException(status_code=503, detail="연금 보험 추천 엔진이 초기화되지 않았습니다.")
        
        analytics = savings_engine.get_analytics_summary()
        return analytics
        
    except Exception as e:
        logger.error(f"연금 보험 분석 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연금 보험 분석 조회 중 오류가 발생했습니다: {str(e)}")

@app.post("/recommend/accident")
async def get_accident_recommendations(request: dict):
    """상해보험 추천 - app2의 실제 데이터 사용"""
    try:
        age = request.get("age", 30)
        sex = request.get("sex", "male")
        top_n = request.get("top_n", 5)
        sort_by = request.get("sort_by", "default")
        
        logger.info(f"상해보험 추천 요청: 나이={age}, 성별={sex}, 상품수={top_n}")
        
        # 실제 상해보험 데이터 사용 (CSV 파일 직접 읽기)
        import pandas as pd
        import os
        
        # 상해보험 CSV 파일 경로
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'csv', 'accident.csv')
        
        try:
            # CSV 파일 읽기
            df = pd.read_csv(csv_path)
            
            # 나이 필터링 (간단한 로직)
            if age < 20:
                df = df[df['male_premium'] > 0]  # 20세 미만은 모든 상품
            elif age > 60:
                df = df[df['male_premium'] > 0]  # 60세 초과는 모든 상품
            else:
                df = df[df['male_premium'] > 0]  # 기본적으로 모든 상품
            
            # 성별에 따른 보험료 선택
            if sex.lower() == 'male':
                df['selected_premium'] = df['male_premium']
            else:
                df['selected_premium'] = df['female_premium']
            
            # 평균 보험료 계산
            df['avg_premium'] = (df['male_premium'] + df['female_premium']) / 2
            
            # 추천 점수 계산 (간단한 로직)
            df['coverage_score'] = df['coverage_amount'] / df['coverage_amount'].max()
            df['value_score'] = 1 - (df['avg_premium'] / df['avg_premium'].max())
            df['stability_score'] = df['renewal_cycle'].apply(lambda x: 1.0 if '비갱신' in str(x) else 0.5)
            df['final_score'] = (df['coverage_score'] * 0.5 + df['value_score'] * 0.4 + df['stability_score'] * 0.1)
            
            # 정렬
            if sort_by == "premium":
                df = df.sort_values('avg_premium')
            elif sort_by == "coverage":
                df = df.sort_values('coverage_amount', ascending=False)
            else:
                df = df.sort_values('final_score', ascending=False)
            
            # 상위 N개 선택
            df = df.head(top_n)
            
            # 결과를 딕셔너리로 변환
            recommendations_dict = []
            for idx, row in df.iterrows():
                rec_dict = {
                    "policy_id": idx,
                    "insurance_company": row['insurance_company'],
                    "product_name": row['product_name'],
                    "coverage_amount": int(row['coverage_amount']),
                    "male_premium": float(row['male_premium']),
                    "female_premium": float(row['female_premium']),
                    "avg_premium": float(row['avg_premium']),
                    "renewal_cycle": row['renewal_cycle'],
                    "surrender_value": "N/A",
                    "sales_channel": "온라인",
                    "coverage_score": float(row['coverage_score']),
                    "value_score": float(row['value_score']),
                    "stability_score": float(row['stability_score']),
                    "final_score": float(row['final_score'])
                }
                recommendations_dict.append(rec_dict)
                
        except Exception as e:
            logger.error(f"상해보험 데이터 로드 실패: {e}")
            # 샘플 데이터로 대체
            recommendations_dict = [
                {
                    "policy_id": 1,
                    "insurance_company": "삼성생명",
                    "product_name": "삼성 슬기로운 취미생활 상해보험",
                    "coverage_amount": 10000000,
                    "male_premium": 900.0,
                    "female_premium": 900.0,
                    "avg_premium": 900.0,
                    "renewal_cycle": "비갱신형",
                    "surrender_value": "N/A",
                    "sales_channel": "온라인",
                    "coverage_score": 0.8,
                    "value_score": 0.9,
                    "stability_score": 1.0,
                    "final_score": 0.85
                },
                {
                    "policy_id": 2,
                    "insurance_company": "ABL생명",
                    "product_name": "ABL건강N더보장종합보험",
                    "coverage_amount": 1000000,
                    "male_premium": 33.0,
                    "female_premium": 14.0,
                    "avg_premium": 23.5,
                    "renewal_cycle": "갱신형",
                    "surrender_value": "N/A",
                    "sales_channel": "온라인",
                    "coverage_score": 0.6,
                    "value_score": 0.95,
                    "stability_score": 0.5,
                    "final_score": 0.7
                }
            ]
        
        return {
            "success": True,
            "message": f"상해보험 추천 상품 {len(recommendations_dict)}개를 반환했습니다.",
            "total_products": len(recommendations_dict),
            "recommendations": recommendations_dict
        }
        
    except Exception as e:
        logger.error(f"상해보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상해보험 추천 중 오류가 발생했습니다: {str(e)}")

@app.post("/recommend/savings-insurance")
async def get_savings_insurance_recommendations(request: dict):
    """저축성보험 추천 - CSV 데이터 기반"""
    try:
        age = request.get("age", 30)
        monthly_budget = request.get("monthly_budget", 300000)
        purpose = request.get("purpose", "단기저축")
        min_guaranteed_rate = request.get("min_guaranteed_rate", None)
        top_n = request.get("top_n", 5)
        
        logger.info(f"저축성보험 추천 요청: 나이={age}, 예산={monthly_budget}, 목적={purpose}")
        
        if savings_engine is None:
            raise HTTPException(status_code=503, detail="저축성보험 추천 엔진이 초기화되지 않았습니다.")
        
        # 저축성보험 추천 로직
        recommendations = savings_engine.get_recommendations(
            age=age,
            monthly_budget=monthly_budget,
            purpose=purpose,
            min_guaranteed_rate=min_guaranteed_rate,
            top_n=top_n
        )
        
        return {
            "success": True,
            "message": f"저축성보험 추천 상품 {len(recommendations)}개를 반환했습니다.",
            "total_products": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"저축성보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저축성보험 추천 중 오류가 발생했습니다: {str(e)}")

@app.get("/savings-insurance/analytics")
async def get_savings_insurance_analytics():
    """저축성보험 분석 요약 정보"""
    try:
        if savings_engine is None:
            raise HTTPException(status_code=503, detail="저축성보험 추천 엔진이 초기화되지 않았습니다.")
        
        analytics = savings_engine.get_analytics_summary()
        return analytics
        
    except Exception as e:
        logger.error(f"저축성보험 분석 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저축성보험 분석 조회 중 오류가 발생했습니다: {str(e)}")

# === 종신보험 KNN 추천 엔드포인트 ===
@app.post("/recommend/life", response_model=LifeInsuranceResponse)
async def recommend_life_insurance(request: LifeInsuranceRequest):
    """
    종신보험 KNN 추천
    
    K-Nearest Neighbors 알고리즘을 사용하여 사용자와 유사한 보험 상품을 추천합니다.
    성별별로 분리된 모델을 사용하며, 5차원 특징 벡터 기반으로 유사도를 계산합니다.
    """
    try:
        if life_engine is None:
            raise HTTPException(status_code=503, detail="종신보험 추천 엔진이 초기화되지 않았습니다.")
        
        logger.info(f"종신보험 추천 요청: 성별={request.gender}, 나이={request.age}, 직업={request.job}")
        
        # 추천 실행
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
        
    except Exception as e:
        logger.error(f"종신보험 추천 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"종신보험 추천 중 오류가 발생했습니다: {str(e)}")

@app.post("/admin/reload-data")
async def reload_data():
    """관리자용: CSV 데이터 재로딩"""
    global data_loader, simple_engine, savings_engine, savings_engine, simple_cancer_engine, cancer_engine, accident_engine
    try:
        logger.info("관리자 요청: 데이터 재로딩 시작...")
        
        # 각 엔진 재초기화
        reloaded_engines = []
        
        # 1. 암보험 추천 엔진 재로딩
        try:
            # 모듈 캐시 제거 및 재로드
            if 'simple_cancer_fix' in sys.modules:
                importlib.reload(sys.modules['simple_cancer_fix'])
            from cancer_engine import PersonalizedCancerEngine
            cancer_engine = PersonalizedCancerEngine()
            reloaded_engines.append("암보험 추천 엔진")
            logger.info("암보험 추천 엔진 재로딩 완료")
        except Exception as e:
            logger.warning(f"암보험 추천 엔진 재로딩 실패: {e}")
        
        # 2. 맞춤형 암보험 추천 엔진 재로딩
        try:
            if 'cancer_engine' in sys.modules:
                importlib.reload(sys.modules['cancer_engine'])
            from cancer_engine import PersonalizedCancerEngine
            cancer_engine = PersonalizedCancerEngine()
            reloaded_engines.append("맞춤형 암보험 추천 엔진")
            logger.info("맞춤형 암보험 추천 엔진 재로딩 완료")
        except Exception as e:
            logger.warning(f"맞춤형 암보험 추천 엔진 재로딩 실패: {e}")
        
        # 3. 저축성보험 추천 엔진 재로딩
        try:
            if 'savings_engine' in sys.modules:
                importlib.reload(sys.modules['savings_engine'])
            from savings_engine import SavingsInsuranceEngine
            savings_engine = SavingsInsuranceEngine()
            reloaded_engines.append("저축성보험 추천 엔진")
            logger.info("저축성보험 추천 엔진 재로딩 완료")
        except Exception as e:
            logger.warning(f"저축성보험 추천 엔진 재로딩 실패: {e}")
        
        # 4. 연금보험 추천 엔진 재로딩
        try:
            if 'pension_engine' in sys.modules:
                importlib.reload(sys.modules['pension_engine'])
            from pension_engine import SavingsRecommendationEngine
            savings_engine = SavingsRecommendationEngine()
            reloaded_engines.append("연금보험 추천 엔진")
            logger.info("연금보험 추천 엔진 재로딩 완료")
        except Exception as e:
            logger.warning(f"연금보험 추천 엔진 재로딩 실패: {e}")
        
        # 5. 간단한 추천 엔진 재로딩
        try:
            if 'basic_engine' in sys.modules:
                importlib.reload(sys.modules['basic_engine'])
            from basic_engine import SimpleRecommendationEngine
            simple_engine = SimpleRecommendationEngine()
            reloaded_engines.append("간단한 추천 엔진")
            logger.info("간단한 추천 엔진 재로딩 완료")
        except Exception as e:
            logger.warning(f"간단한 추천 엔진 재로딩 실패: {e}")
        
        # 6. DataLoader 재로딩
        try:
            if 'data_loader' in sys.modules:
                importlib.reload(sys.modules['data_loader'])
            from data_loader import DataLoader
            data_loader = DataLoader()
            reloaded_engines.append("DataLoader")
            logger.info("DataLoader 재로딩 완료")
        except Exception as e:
            logger.warning(f"DataLoader 재로딩 실패: {e}")
        
        # 상해보험은 엔진을 사용하지 않고 직접 CSV를 읽으므로 재로딩 불필요
        reloaded_engines.append("상해보험 (CSV 직접 읽기 - 자동 반영)")
        
        logger.info(f"데이터 재로딩 완료! 재로딩된 엔진: {', '.join(reloaded_engines)}")
        
        return {
            "success": True,
            "message": "데이터가 성공적으로 재로딩되었습니다.",
            "reloaded_engines": reloaded_engines,
            "total_reloaded": len(reloaded_engines)
        }
        
    except Exception as e:
        logger.error(f"데이터 재로딩 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 재로딩 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
