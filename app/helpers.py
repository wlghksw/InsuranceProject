"""
공통 헬퍼 함수들
"""
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def handle_recommendation_request(
    engine,
    request,
    engine_name: str,
    response_class,
    transform_func=None
):
    """
    공통 추천 요청 처리 로직
    
    Args:
        engine: 추천 엔진 인스턴스
        request: 요청 객체
        engine_name: 엔진 이름 (로깅용)
        response_class: 응답 클래스
        transform_func: 추천 결과 변환 함수 (선택)
    
    Returns:
        응답 객체
    """
    try:
        logger.info(f"{engine_name} 추천 요청 받음")
        
        # 엔진 존재 확인
        if engine is None:
            logger.error(f"{engine_name} 엔진이 초기화되지 않았습니다")
            raise HTTPException(
                status_code=503, 
                detail=f"{engine_name} 추천 엔진이 초기화되지 않았습니다."
            )
        
        # 추천 실행
        recommendations = engine.get_recommendations(request)
        
        # 결과 변환 (필요시)
        if transform_func:
            recommendations = transform_func(recommendations)
        
        logger.info(f"{engine_name} 추천 상품 {len(recommendations)}개 반환")
        
        # 응답 생성
        return response_class(
            success=True,
            message=f"총 {len(recommendations)}개의 상품을 추천했습니다",
            total_products=len(recommendations),
            recommendations=recommendations,
            request_params=request
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"{engine_name} 추천 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"{engine_name} 추천 처리 중 오류가 발생했습니다: {str(e)}"
        )


def handle_simple_dict_request(
    engine,
    request_dict: dict,
    engine_name: str
):
    """
    딕셔너리 형태 요청 처리 (간단한 API용)
    
    Args:
        engine: 추천 엔진 인스턴스
        request_dict: 요청 딕셔너리
        engine_name: 엔진 이름
    
    Returns:
        딕셔너리 응답
    """
    try:
        logger.info(f"{engine_name} 추천 요청: {request_dict}")
        
        # 엔진 존재 확인
        if engine is None:
            logger.error(f"{engine_name} 엔진이 초기화되지 않았습니다")
            raise HTTPException(
                status_code=503, 
                detail=f"{engine_name} 추천 엔진이 초기화되지 않았습니다."
            )
        
        # 파라미터 추출
        age = request_dict.get("age", 30)
        monthly_budget = request_dict.get("monthly_budget", 300000)
        purpose = request_dict.get("purpose", "단기저축")
        top_n = request_dict.get("top_n", 5)
        
        # 추천 실행
        recommendations = engine.get_recommendations(
            age=age,
            monthly_budget=monthly_budget,
            purpose=purpose,
            top_n=top_n
        )
        
        logger.info(f"{engine_name} 추천 완료: {len(recommendations)}개")
        
        return {
            "success": True,
            "message": f"{engine_name} 추천 상품 {len(recommendations)}개를 반환했습니다.",
            "total_products": len(recommendations),
            "recommendations": recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"{engine_name} 추천 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"{engine_name} 추천 중 오류가 발생했습니다: {str(e)}"
        )


def handle_analytics_request(engine, engine_name: str):
    """
    분석 요약 정보 조회 처리
    
    Args:
        engine: 추천 엔진 인스턴스
        engine_name: 엔진 이름
    
    Returns:
        분석 요약 딕셔너리
    """
    try:
        if engine is None:
            raise HTTPException(
                status_code=503, 
                detail=f"{engine_name} 추천 엔진이 초기화되지 않았습니다."
            )
        
        analytics = engine.get_analytics_summary()
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"{engine_name} 분석 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"{engine_name} 분석 조회 중 오류가 발생했습니다: {str(e)}"
        )


def convert_to_product_recommendation(recommendations, ProductRecommendation):
    """
    딕셔너리 추천 결과를 ProductRecommendation 객체로 변환
    
    Args:
        recommendations: 추천 결과 리스트
        ProductRecommendation: ProductRecommendation 클래스
    
    Returns:
        ProductRecommendation 객체 리스트
    """
    product_recommendations = []
    
    for rec in recommendations:
        # 이미 객체인 경우
        if hasattr(rec, 'policy_id'):
            product_recommendations.append(rec)
            continue
        
        # 딕셔너리인 경우 변환
        avg_premium = (rec.get('male_premium', 0) + rec.get('female_premium', 0)) / 2
        
        product_rec = ProductRecommendation(
            policy_id=rec.get('policy_id', 0),
            insurance_company=rec.get('insurance_company', ''),
            product_name=rec.get('product_name', ''),
            coverage_amount=rec.get('coverage_amount', 0),
            male_premium=rec.get('male_premium', 0),
            female_premium=rec.get('female_premium', 0),
            avg_premium=avg_premium,
            renewal_cycle=rec.get('renewal_cycle', ''),
            sales_channel=rec.get('sales_channel', ''),
            surrender_value=rec.get('surrender_value', ''),
            final_score=rec.get('recommendation_score', rec.get('final_score', 0.0)),
            coverage_score=rec.get('coverage_score', 0.0),
            value_score=rec.get('value_score', 0.0),
            stability_score=rec.get('stability_score', 0.0),
            coverage_details=rec.get('coverage_details', [])
        )
        product_recommendations.append(product_rec)
    
    return product_recommendations

