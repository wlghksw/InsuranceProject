import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from data_loader import DataLoader
from models import ProductRecommendation, UserProfileRecommendationRequest

class RecommendationEngine:
    """암보험 상품 추천 엔진"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.df = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            self.df = self.data_loader.get_cancer_products_df()
            if self.df is not None and not self.df.empty:
                print(f"암보험 데이터 로드 완료: {len(self.df)}개 상품")
            else:
                print("암보험 데이터가 없습니다.")
        except Exception as e:
            print(f"데이터 로드 중 오류: {str(e)}")
            self.df = None
    
    def get_recommendations(self, request) -> List[ProductRecommendation]:
        """암보험 상품 추천"""
        if self.df is None or self.df.empty:
            print("데이터프레임이 비어있습니다.")
            return []
        
        print(f"전체 데이터: {len(self.df)}개")
        print(f"데이터 컬럼: {list(self.df.columns)}")
        
        try:
            # 기본 필터링
            filtered_df = self._apply_filters(self.df, request)
            print(f"필터링 후 데이터: {len(filtered_df)}개")
            
            if filtered_df.empty:
                print("필터링 후 데이터가 비어있습니다.")
                return []
            
            # 점수 계산 및 정렬
            scored_df = self._calculate_scores(filtered_df, request)
            
            # 상위 N개 추천
            top_products = scored_df.head(request.top_n)
            
            # ProductRecommendation 객체로 변환
            recommendations = []
            for _, row in top_products.iterrows():
                recommendation = ProductRecommendation(
                    product_id=str(row.get('product_id', '')),
                    company=str(row.get('company', '정보없음')),
                    product_name=str(row.get('product_name', '정보없음')),
                    product_type="암보험",
                    score=float(row.get('score', 0.0)),
                    coverage_amount=str(row.get('coverage_amount', '정보없음')),
                    monthly_premium=str(row.get('monthly_premium', '정보없음')),
                    renewal_type=str(row.get('renewal_type', '정보없음')),
                    sales_channel=str(row.get('sales_channel', '정보없음')),
                    coverage_details=self._get_coverage_details(row)
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"추천 처리 중 오류: {str(e)}")
            return []
    
    def _apply_filters(self, df: pd.DataFrame, request) -> pd.DataFrame:
        """기본 필터링 적용"""
        filtered_df = df.copy()
        
        # 보장금액 필터
        if hasattr(request, 'min_coverage') and request.min_coverage:
            # coverage_amount 컬럼이 문자열이므로 숫자로 변환
            def parse_coverage(amount_str):
                if pd.isna(amount_str):
                    return 0
                amount_str = str(amount_str).replace(',', '').replace('원', '').replace('억', '00000000').replace('천', '0000')
                try:
                    return float(amount_str)
                except:
                    return 0
            
            filtered_df['coverage_numeric'] = filtered_df['coverage_amount'].apply(parse_coverage)
            filtered_df = filtered_df[filtered_df['coverage_numeric'] >= request.min_coverage]
        
        # 보험료 필터
        if hasattr(request, 'max_premium_avg') and request.max_premium_avg:
            def parse_premium(premium_str):
                if pd.isna(premium_str):
                    return 0
                premium_str = str(premium_str).replace(',', '').replace('원', '')
                try:
                    return float(premium_str)
                except:
                    return 0
            
            filtered_df['premium_numeric'] = filtered_df['monthly_premium'].apply(parse_premium)
            filtered_df = filtered_df[filtered_df['premium_numeric'] <= request.max_premium_avg]
        
        # 갱신형/비갱신형 필터
        if hasattr(request, 'prefer_non_renewal') and request.prefer_non_renewal:
            filtered_df = filtered_df[filtered_df['renewal_type'].str.contains('비갱신', na=False)]
        
        # 판매채널 필터
        if hasattr(request, 'require_sales_channel') and request.require_sales_channel:
            filtered_df = filtered_df[filtered_df['sales_channel'].str.contains(request.require_sales_channel, na=False)]
        
        return filtered_df
    
    def _calculate_scores(self, df: pd.DataFrame, request) -> pd.DataFrame:
        """점수 계산"""
        scored_df = df.copy()
        
        # 기본 점수 계산
        scores = []
        for _, row in scored_df.iterrows():
            score = self._calculate_product_score(row, request)
            scores.append(score)
        
        scored_df['score'] = scores
        
        # 점수 순으로 정렬
        scored_df = scored_df.sort_values('score', ascending=False)
        
        return scored_df
    
    def _calculate_product_score(self, row, request) -> float:
        """개별 상품 점수 계산"""
        score = 50.0  # 기본 점수
        
        try:
            # 보장금액 점수
            coverage_amount = str(row.get('coverage_amount', '0')).replace(',', '').replace('원', '')
            if coverage_amount.isdigit():
                coverage = int(coverage_amount)
                if coverage >= 10000000:  # 1천만원 이상
                    score += 20
                elif coverage >= 5000000:  # 5백만원 이상
                    score += 10
            
            # 월 보험료 점수
            monthly_premium = str(row.get('monthly_premium', '0')).replace(',', '').replace('원', '')
            if monthly_premium.replace('.', '').isdigit():
                premium = float(monthly_premium)
                if premium <= 1000:  # 1,000원 이하
                    score += 30
                elif premium <= 2000:  # 2,000원 이하
                    score += 20
                elif premium <= 5000:  # 5,000원 이하
                    score += 10
            
            # 갱신형태 점수
            renewal_type = str(row.get('renewal_type', ''))
            if '비갱신' in renewal_type:
                score += 15
            
            # 판매채널 점수
            sales_channel = str(row.get('sales_channel', ''))
            if 'CM' in sales_channel:
                score += 10
            
        except Exception as e:
            print(f"점수 계산 중 오류: {str(e)}")
        
        return score
    
    def _get_coverage_details(self, row) -> List[str]:
        """보장 내용 조회"""
        try:
            coverage_details = []
            
            # 기본 보장 항목들
            coverage_items = [
                'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4', 'coverage_5'
            ]
            
            for item in coverage_items:
                if item in row and pd.notna(row[item]):
                    coverage = str(row[item]).strip()
                    if coverage and coverage != 'nan':
                        # 보장금액 추출
                        payment_amount = None
                        if item.replace('coverage', 'payment') in row:
                            payment_amount = str(row[item.replace('coverage', 'payment')]).strip()
                        
                        detail = coverage
                        if payment_amount and payment_amount != 'nan' and len(payment_amount) < 50:
                            detail += f" ({payment_amount})"
                        
                        coverage_details.append(detail)
            
            return coverage_details if coverage_details else ["상세 보장 내용은 약관을 참조하세요."]
            
        except Exception as e:
            print(f"보장 내용 조회 중 오류: {str(e)}")
            return ["보장 내용 조회 중 오류가 발생했습니다."]