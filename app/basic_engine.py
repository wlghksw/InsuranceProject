import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimpleRecommendationEngine:
    """간단한 사용자 프로필 기반 추천 시스템"""
    
    def __init__(self):
        self.user_profiles = None
        self.products = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            # 개선된 사용자 프로필 데이터 로드
            self.user_profiles = pd.read_csv('../data/csv/users_improved.csv')
            logger.info(f"개선된 사용자 프로필 데이터 로드 완료: {len(self.user_profiles)}명")
            
            # 상품 데이터 로드
            from data_loader import DataLoader
            data_loader = DataLoader()
            self.products = data_loader.products
            
            # 상품 ID를 키로 하는 딕셔너리 생성
            self.product_dict = {product.get('policy_id', 0): product for product in self.products}
            
            logger.info(f"상품 데이터 로드 완료: {len(self.products)}개")
            
        except Exception as e:
            logger.error(f"데이터 로드 실패: {str(e)}")
            raise e
    
    def calculate_user_similarity(self, target_user: Dict[str, Any]) -> pd.Series:
        """사용자 유사도 계산"""
        # 타겟 사용자 프로필 정규화
        target_age = target_user['age']
        target_sex = 1 if target_user['sex'] == 'M' else 0
        target_budget = target_user['monthly_budget']
        target_family = 1 if target_user['family_cancer_history'] else 0
        
        # 보장기간 인코딩
        period_mapping = {'10년': 1, '20년': 2, '종신': 3}
        target_period = period_mapping.get(target_user['preferred_coverage_period'], 0)
        
        # 기존 사용자들과의 유사도 계산
        similarities = []
        
        for _, user in self.user_profiles.iterrows():
            # 나이 유사도 (나이 차이가 적을수록 높은 점수)
            age_diff = abs(user['age'] - target_age)
            age_similarity = max(0, 1 - age_diff / 50)  # 50세 차이면 0점
            
            # 성별 일치도
            user_sex = 1 if user['sex'] == 'M' else 0
            sex_similarity = 1 if target_sex == user_sex else 0.3  # 성별이 다르면 30% 점수
            
            # 예산 유사도 (예산 차이가 적을수록 높은 점수)
            budget_diff = abs(user['monthly_budget'] - target_budget)
            budget_similarity = max(0, 1 - budget_diff / 50000)  # 5만원 차이면 0점
            
            # 가족암병력 일치도
            user_family = 1 if user['family_cancer_history'] else 0
            family_similarity = 1 if target_family == user_family else 0.5  # 다르면 50% 점수
            
            # 보장기간 일치도
            user_period = period_mapping.get(user['preferred_coverage_period'], 0)
            period_similarity = 1 if target_period == user_period else 0.6  # 다르면 60% 점수
            
            # 가중 평균 유사도 계산
            # 가중치: 나이(50%) + 성별(15%) + 예산(20%) + 가족암병력(10%) + 보장기간(5%)
            # 나이를 더 중요하게 반영하여 나이별 차별화 강화
            similarity = (age_similarity * 0.5 + 
                         sex_similarity * 0.15 + 
                         budget_similarity * 0.2 + 
                         family_similarity * 0.1 + 
                         period_similarity * 0.05)
            
            similarities.append(similarity)
        
        # 유사도 시리즈 반환
        return pd.Series(similarities, index=self.user_profiles.index)
    
    def get_recommendations(self, 
                          age: int, 
                          sex: str, 
                          monthly_budget: int,
                          family_cancer_history: bool,
                          preferred_coverage_period: str,
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """추천 상품 반환"""
        
        target_user = {
            'age': age,
            'sex': sex,
            'monthly_budget': monthly_budget,
            'family_cancer_history': family_cancer_history,
            'preferred_coverage_period': preferred_coverage_period
        }
        
        logger.info(f"추천 요청: 나이={age}, 성별={sex}, 예산={monthly_budget}, 가족암병력={family_cancer_history}, 보장기간={preferred_coverage_period}")
        
        # 사용자 유사도 계산
        similarities = self.calculate_user_similarity(target_user)
        
        # 상위 유사한 사용자들 선택 (유사도 0.7 이상으로 더 엄격하게)
        similar_users = similarities[similarities >= 0.7].sort_values(ascending=False)
        
        logger.info(f"유사한 사용자 수: {len(similar_users)}명")
        
        if len(similar_users) == 0:
            logger.warning("유사한 사용자가 없어 기본 추천을 사용합니다")
            return self._get_fallback_recommendations(target_user, top_n)
        
        # 유사한 사용자들이 선택한 상품들 수집
        product_scores = {}
        
        for user_idx, similarity in similar_users.items():
            user = self.user_profiles.iloc[user_idx]
            selected_policy_id = user['selected_policy_id']
            
            if selected_policy_id > 0 and selected_policy_id in self.product_dict:
                if selected_policy_id not in product_scores:
                    product_scores[selected_policy_id] = 0
                product_scores[selected_policy_id] += similarity
        
        # 상품별 점수로 정렬
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 N개 상품 선택 (같은 회사 중복 방지)
        recommendations = []
        selected_companies = set()
        
        for policy_id, score in sorted_products:
            if len(recommendations) >= top_n:
                break
                
            product = self.product_dict[policy_id]
            company = product.get('insurance_company', '')
            
            # 같은 회사가 이미 선택되었으면 스킵
            if company in selected_companies:
                continue
            
            # 보험료 설정
            if sex == 'M':
                premium = product.get('male_premium', 0)
            else:
                premium = product.get('female_premium', 0)
            
            if premium > 0:
                recommendation = {
                    'insurance_company': company,
                    'product_name': product.get('product_name', ''),
                    'coverage_amount': product.get('coverage_amount', 0),
                    'male_premium': product.get('male_premium', 0),
                    'female_premium': product.get('female_premium', 0),
                    'renewal_cycle': product.get('renewal_cycle', ''),
                    'sales_channel': product.get('sales_channel', ''),
                    'recommendation_score': round(score, 2)
                }
                recommendations.append(recommendation)
                selected_companies.add(company)
        
        logger.info(f"추천 상품 {len(recommendations)}개 반환")
        return recommendations
    
    def _get_fallback_recommendations(self, target_user: Dict[str, Any], top_n: int) -> List[Dict[str, Any]]:
        """기본 추천 (유사한 사용자가 없을 때)"""
        age = target_user['age']
        sex = target_user['sex']
        monthly_budget = target_user['monthly_budget']
        
        # 조건에 맞는 상품들 필터링
        suitable_products = []
        
        for product in self.products:
            premium = product.get('male_premium' if sex == 'M' else 'female_premium', 0)
            
            if premium == 0 or premium > monthly_budget * 1.5:
                continue
            
            # 나이별 기본 필터링
            if age <= 25 and premium > monthly_budget * 0.8:
                continue
            elif age <= 35 and premium > monthly_budget:
                continue
            elif age <= 45 and premium > monthly_budget * 1.2:
                continue
            
            suitable_products.append(product)
        
        # 상품을 가성비로 정렬 (보장금액 / 보험료)
        def calculate_value_score(product):
            coverage = product.get('coverage_amount', 0)
            premium = product.get('male_premium' if sex == 'M' else 'female_premium', 0)
            return coverage / premium if premium > 0 else 0
        
        suitable_products.sort(key=calculate_value_score, reverse=True)
        
        # 상위 N개 반환 (같은 회사 중복 방지)
        recommendations = []
        selected_companies = set()
        
        for product in suitable_products:
            if len(recommendations) >= top_n:
                break
                
            company = product.get('insurance_company', '')
            
            # 같은 회사가 이미 선택되었으면 스킵
            if company in selected_companies:
                continue
            
            recommendation = {
                'insurance_company': company,
                'product_name': product.get('product_name', ''),
                'coverage_amount': product.get('coverage_amount', 0),
                'male_premium': product.get('male_premium', 0),
                'female_premium': product.get('female_premium', 0),
                'renewal_cycle': product.get('renewal_cycle', ''),
                'sales_channel': product.get('sales_channel', ''),
                'recommendation_score': 0.5  # 기본 점수
            }
            recommendations.append(recommendation)
            selected_companies.add(company)
        
        return recommendations
