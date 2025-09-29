import pandas as pd
import numpy as np
from typing import List
from models import ProductRecommendation

class SimpleCancerEngine:
    """간단한 암보험 추천 엔진"""
    
    def __init__(self, data_dir: str = "products"):
        self.data_dir = data_dir
        self.df = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            # 암보험 정책 데이터 로드 - 절대 경로 사용
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, self.data_dir)
            file_path = os.path.join(data_path, "cancer_policies.csv")
            policies_df = pd.read_csv(file_path)
            
            # 간단한 데이터프레임 생성
            self.df = policies_df.copy()
            
            # 필요한 컬럼들 추가/변환
            self.df['product_id'] = self.df['policy_id'].astype(str)
            self.df['company'] = self.df['insurance_company']
            self.df['product_name'] = self.df['product_name']
            self.df['product_type'] = '암보험'
            self.df['coverage_amount'] = self.df['coverage_amount']
            self.df['monthly_premium'] = self.df['male_premium'].astype(str) + '원'
            self.df['renewal_type'] = self.df['renewal_cycle']
            self.df['sales_channel'] = self.df['sales_channel']
            self.df['coverage_details'] = self.df.apply(lambda row: f"{row['product_name']}의 보장 내용은 {row['coverage_amount']}입니다.", axis=1)
            self.df['score'] = 100.0  # 임시 점수
            
            print(f"암보험 데이터 로드 완료: {len(self.df)}개 상품")
            print(f"컬럼: {list(self.df.columns)}")
            
        except Exception as e:
            print(f"데이터 로드 중 오류: {str(e)}")
            self.df = None
    
    def get_recommendations(self, request) -> List[ProductRecommendation]:
        """암보험 상품 추천"""
        if self.df is None or self.df.empty:
            print("데이터프레임이 비어있습니다.")
            return []
        
        print(f"전체 데이터: {len(self.df)}개")
        
        try:
            # 필터링 적용
            filtered_df = self._apply_filters(self.df, request)
            print(f"필터링 후 데이터: {len(filtered_df)}개")
            
            if filtered_df.empty:
                print("필터링 후 데이터가 비어있습니다. 전체 데이터를 반환합니다.")
                filtered_df = self.df.copy()
            
            # 점수 계산
            scored_df = self._calculate_scores(filtered_df, request)
            
            # 상위 N개 추천
            top_products = scored_df.head(request.top_n)
            
            # ProductRecommendation 객체로 변환
            recommendations = []
            for _, row in top_products.iterrows():
                # coverage_amount를 정수로 변환
                coverage_str = str(row.get('coverage_amount', '0'))
                coverage_amount = 0
                try:
                    if '만원' in coverage_str:
                        coverage_amount = int(float(coverage_str.replace(',', '').replace('만원', '')) * 10000)
                    elif '천원' in coverage_str:
                        coverage_amount = int(float(coverage_str.replace(',', '').replace('천원', '')) * 1000)
                    else:
                        coverage_amount = int(float(coverage_str.replace(',', '')))
                except:
                    coverage_amount = 0
                
                # premium을 float로 변환
                male_premium = float(row.get('male_premium', 0)) if row.get('male_premium') else 0.0
                female_premium = float(row.get('female_premium', 0)) if row.get('female_premium') else 0.0
                avg_premium = (male_premium + female_premium) / 2 if male_premium and female_premium else male_premium or female_premium
                
                recommendation = ProductRecommendation(
                    policy_id=int(row.get('policy_id', 0)),
                    insurance_company=str(row.get('insurance_company', '정보없음')),
                    product_name=str(row.get('product_name', '정보없음')),
                    coverage_amount=coverage_amount,
                    male_premium=male_premium,
                    female_premium=female_premium,
                    avg_premium=avg_premium,
                    renewal_cycle=str(row.get('renewal_cycle', '정보없음')),
                    surrender_value=str(row.get('surrender_value', '정보없음')),
                    sales_channel=str(row.get('sales_channel', '정보없음')),
                    coverage_score=80.0,
                    value_score=75.0,
                    stability_score=85.0,
                    final_score=80.0,
                    coverage_details=["암진단금", "암입원금", "암수술금"]
                )
                recommendations.append(recommendation)
            
            print(f"추천 상품 {len(recommendations)}개 생성")
            return recommendations
            
        except Exception as e:
            print(f"추천 처리 중 오류: {str(e)}")
            return []
    
    def _apply_filters(self, df: pd.DataFrame, request) -> pd.DataFrame:
        """기본 필터링 적용"""
        filtered_df = df.copy()
        
        # 보장금액 필터
        if hasattr(request, 'min_coverage') and request.min_coverage:
            def parse_coverage(amount_str):
                if pd.isna(amount_str):
                    return 0
                amount_str = str(amount_str).replace(',', '').replace('원', '').replace('만', '0000')
                try:
                    return float(amount_str)
                except:
                    return 0
            
            filtered_df['coverage_numeric'] = filtered_df['coverage_amount'].apply(parse_coverage)
            filtered_df = filtered_df[filtered_df['coverage_numeric'] >= request.min_coverage]
        
        # 보험료 필터
        if hasattr(request, 'max_premium_avg') and request.max_premium_avg:
            filtered_df = filtered_df[filtered_df['male_premium'] <= request.max_premium_avg]
        
        # 갱신형/비갱신형 필터
        if hasattr(request, 'prefer_non_renewal') and request.prefer_non_renewal:
            filtered_df = filtered_df[filtered_df['renewal_cycle'].str.contains('비갱신', na=False)]
        
        return filtered_df
    
    def _calculate_scores(self, df: pd.DataFrame, request) -> pd.DataFrame:
        """점수 계산"""
        scored_df = df.copy()
        
        # 기본 점수 계산 (50점부터 시작)
        scores = []
        for _, row in scored_df.iterrows():
            score = 50.0
            
            # 보장금액 점수 (10점 만점)
            coverage_amount = str(row.get('coverage_amount', '0')).replace(',', '').replace('원', '').replace('만', '0000')
            try:
                coverage_num = float(coverage_amount)
                if coverage_num > 0:
                    score += min(10, coverage_num / 10000000)  # 1000만원당 1점
            except:
                pass
            
            # 보험료 점수 (10점 만점) - 낮을수록 좋음
            premium = row.get('male_premium', 0)
            if premium > 0:
                score += min(10, 100000 / premium)  # 보험료가 낮을수록 높은 점수
            
            # 갱신형 점수 (5점 만점)
            renewal_type = str(row.get('renewal_cycle', ''))
            if '비갱신' in renewal_type:
                score += 5  # 비갱신형 선호
            
            scores.append(score)
        
        scored_df['score'] = scores
        
        # 점수 순으로 정렬
        scored_df = scored_df.sort_values('score', ascending=False)
        
        return scored_df
