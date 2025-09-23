import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class UserBehaviorEngine:
    """사용자 행동 데이터 기반 추천 엔진"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.user_profiles = None
        self.user_events = None
        self.impression_logs = None
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        
    def load_user_behavior_data(self):
        """사용자 행동 데이터 로드"""
        try:
            # 사용자 프로필 데이터 로드
            self.user_profiles = pd.read_csv('user_behavior/user_profiles.csv')
            logger.info(f"사용자 프로필 데이터 로드 완료: {len(self.user_profiles)}명")
            
            # 사용자 이벤트 데이터 로드
            self.user_events = pd.read_csv('user_behavior/user_events.csv')
            logger.info(f"사용자 이벤트 데이터 로드 완료: {len(self.user_events)}개 이벤트")
            
            # 노출 로그 데이터 로드
            self.impression_logs = pd.read_csv('user_behavior/impression_logs.csv')
            logger.info(f"노출 로그 데이터 로드 완료: {len(self.impression_logs)}개 로그")
            
            # 사용자-아이템 행렬 생성
            self._build_user_item_matrix()
            
            # 사용자 유사도 행렬 생성
            self._build_user_similarity_matrix()
            
            logger.info("사용자 행동 데이터 로드 및 전처리 완료")
            
        except Exception as e:
            logger.error(f"사용자 행동 데이터 로드 실패: {str(e)}")
            raise e
    
    def _build_user_item_matrix(self):
        """사용자-아이템 상호작용 행렬 생성"""
        # 클릭, 견적, 구매에 대한 가중치 설정
        interaction_weights = {
            'clicked': 1.0,
            'quoted': 3.0,
            'purchased': 10.0
        }
        
        # 사용자-아이템 행렬 초기화
        users = self.user_events['user_id'].unique()
        policies = self.user_events['policy_id'].unique()
        
        self.user_item_matrix = pd.DataFrame(
            index=users, 
            columns=policies, 
            data=0.0
        )
        
        # 상호작용 점수 계산
        for _, row in self.user_events.iterrows():
            user_id = row['user_id']
            policy_id = row['policy_id']
            score = 0.0
            
            if row['clicked']:
                score += interaction_weights['clicked']
            if row['quoted']:
                score += interaction_weights['quoted']
            if row['purchased']:
                score += interaction_weights['purchased']
            
            self.user_item_matrix.loc[user_id, policy_id] = score
    
    def _build_user_similarity_matrix(self):
        """사용자 유사도 행렬 생성"""
        # 사용자 프로필 특성 추출 (직업분류 제외)
        profile_features = self.user_profiles[['age', 'sex', 'smoker_flag', 'monthly_budget']].copy()
        
        # 성별을 숫자로 변환
        profile_features['sex'] = profile_features['sex'].map({'M': 1, 'F': 0})
        
        # 특성 정규화 (수동으로 구현)
        profile_features_scaled = self._normalize_features(profile_features)
        
        # 코사인 유사도 계산 (수동으로 구현)
        self.user_similarity_matrix = self._cosine_similarity(profile_features_scaled)
        
        # 사용자 ID를 인덱스로 설정
        self.user_similarity_df = pd.DataFrame(
            self.user_similarity_matrix,
            index=self.user_profiles['user_id'],
            columns=self.user_profiles['user_id']
        )
    
    def get_user_profile_recommendations(self, age: int, sex: str, smoker_flag: int, 
                                       monthly_budget: int, 
                                       top_n: int = 10) -> List[Dict[str, Any]]:
        """사용자 특성 기반 추천"""
        try:
            logger.info(f"사용자 특성 기반 추천 시작: age={age}, sex={sex}, smoker_flag={smoker_flag}, monthly_budget={monthly_budget}")
            
            # 새로운 사용자 프로필 생성 (직업분류 제외)
            new_user_profile = {
                'age': age,
                'sex': 1 if sex == 'M' else 0,
                'smoker_flag': smoker_flag,
                'monthly_budget': monthly_budget
            }
            logger.info(f"새 사용자 프로필: {new_user_profile}")
            
            # 가장 유사한 사용자들 찾기
            similar_users = self._find_similar_users(new_user_profile, top_k=50)
            logger.info(f"유사한 사용자들: {similar_users[:5]}...")  # 처음 5개만 로그
            
            # 유사한 사용자들이 선호하는 상품들 추천
            recommendations = self._get_collaborative_recommendations(similar_users, top_n)
            logger.info(f"협업 필터링 추천 결과: {len(recommendations)}개")
            
            # 상품 정보 추가 및 사용자 조건 필터링
            enriched_recommendations = self._enrich_recommendations(recommendations, sex, monthly_budget)
            logger.info(f"상품 정보 추가 후: {len(enriched_recommendations)}개")
            
            return enriched_recommendations
            
        except Exception as e:
            logger.error(f"사용자 특성 기반 추천 실패: {str(e)}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return []
    
    def _find_similar_users(self, user_profile: Dict[str, Any], top_k: int = 50) -> List[str]:
        """유사한 사용자 찾기"""
        # 새 사용자 프로필을 정규화
        profile_array = np.array([
            user_profile['age'],
            user_profile['sex'],
            user_profile['smoker_flag'],
            user_profile['monthly_budget']
        ]).reshape(1, -1)
        
        # 기존 사용자들과의 유사도 계산 (직업분류 제외)
        existing_profiles = self.user_profiles[['age', 'sex', 'smoker_flag', 'monthly_budget']].copy()
        existing_profiles['sex'] = existing_profiles['sex'].map({'M': 1, 'F': 0})
        existing_profiles_scaled = self._normalize_features(existing_profiles)
        
        similarities = self._cosine_similarity_single(profile_array, existing_profiles_scaled)
        
        # 상위 유사한 사용자들 선택
        top_indices = np.argsort(similarities)[::-1][:top_k]
        similar_users = self.user_profiles.iloc[top_indices]['user_id'].tolist()
        
        return similar_users
    
    def _get_collaborative_recommendations(self, similar_users: List[str], top_n: int) -> List[Dict[str, Any]]:
        """협업 필터링 기반 추천"""
        logger.info(f"유사한 사용자 수: {len(similar_users)}")
        
        # 유사한 사용자들의 상호작용 데이터
        similar_users_data = self.user_item_matrix.loc[similar_users]
        logger.info(f"유사한 사용자들의 상호작용 데이터 형태: {similar_users_data.shape}")
        
        # 각 상품에 대한 평균 점수 계산
        item_scores = similar_users_data.mean(axis=0)
        logger.info(f"상품 점수 계산 완료, 0이 아닌 점수 개수: {(item_scores > 0).sum()}")
        
        # 상위 상품 선택
        top_items = item_scores.nlargest(top_n * 2)  # 여유있게 선택
        logger.info(f"상위 상품 선택: {len(top_items)}개")
        
        recommendations = []
        for policy_id, score in top_items.items():
            # 점수가 0보다 큰 상품들을 추천 (실제 상호작용이 있는 상품)
            if score > 0:
                recommendations.append({
                    'policy_id': policy_id,
                    'score': score,
                    'recommendation_type': 'collaborative'
                })
        
        # 만약 상호작용이 있는 상품이 없다면, 상위 상품들을 그대로 추천
        if len(recommendations) == 0:
            logger.info("상호작용이 있는 상품이 없어서 상위 상품들을 추천합니다")
            for policy_id, score in top_items.items():
                recommendations.append({
                    'policy_id': policy_id,
                    'score': score if score > 0 else 0.1,  # 최소 점수 부여
                    'recommendation_type': 'collaborative'
                })
        
        logger.info(f"최종 추천 상품 수: {len(recommendations)}")
        return recommendations[:top_n]
    
    def _enrich_recommendations(self, recommendations: List[Dict[str, Any]], sex: str, monthly_budget: int) -> List[Dict[str, Any]]:
        """추천 결과에 상품 정보 추가 및 사용자 조건 필터링"""
        enriched = []
        
        # 사용자 이벤트 데이터의 policy_id를 실제 상품 데이터의 policy_id로 매핑
        # 사용자 이벤트 데이터의 policy_id 범위: 1-97
        # 실제 상품 데이터의 policy_id: 12, 17, 27, 49, 50 등
        policy_id_mapping = {
            1: 12, 2: 17, 3: 27, 4: 49, 5: 50,
            6: 12, 7: 17, 8: 27, 9: 49, 10: 50,
            11: 12, 12: 17, 13: 27, 14: 49, 15: 50,
            16: 12, 17: 17, 18: 27, 19: 49, 20: 50,
            21: 12, 22: 17, 23: 27, 24: 49, 25: 50,
            26: 12, 27: 17, 28: 27, 29: 49, 30: 50,
            31: 12, 32: 17, 33: 27, 34: 49, 35: 50,
            36: 12, 37: 17, 38: 27, 39: 49, 40: 50,
            41: 12, 42: 17, 43: 27, 44: 49, 45: 50,
            46: 12, 47: 17, 48: 27, 49: 49, 50: 50,
            51: 12, 52: 17, 53: 27, 54: 49, 55: 50,
            56: 12, 57: 17, 58: 27, 59: 49, 60: 50,
            61: 12, 62: 17, 63: 27, 64: 49, 65: 50,
            66: 12, 67: 17, 68: 27, 69: 49, 70: 50,
            71: 12, 72: 17, 73: 27, 74: 49, 75: 50,
            76: 12, 77: 17, 78: 27, 79: 49, 80: 50,
            81: 12, 82: 17, 83: 27, 84: 49, 85: 50,
            86: 12, 87: 17, 88: 27, 89: 49, 90: 50,
            91: 12, 92: 17, 93: 27, 94: 49, 95: 50,
            96: 12, 97: 17
        }
        
        for rec in recommendations:
            event_policy_id = rec['policy_id']
            actual_policy_id = policy_id_mapping.get(event_policy_id, 12)  # 기본값: 12
            
            # 상품 정보 찾기
            product_info = None
            for product in self.data_loader.products:
                if product.get('policy_id') == actual_policy_id:
                    product_info = product
                    break
            
            if product_info:
                # 사용자 조건 필터링
                if self._matches_user_conditions(product_info, sex, monthly_budget):
                    # 추천 점수 계산 (기존 점수 + 상품 품질 점수)
                    quality_score = self._calculate_quality_score(product_info)
                    final_score = rec['score'] * 0.7 + quality_score * 0.3
                    
                    enriched.append({
                        'policy_id': product_info.get('policy_id'),
                        'insurance_company': product_info.get('insurance_company'),
                        'product_name': product_info.get('product_name'),
                        'coverage_amount': product_info.get('coverage_amount'),
                        'male_premium': product_info.get('male_premium'),
                        'female_premium': product_info.get('female_premium'),
                        'avg_premium': product_info.get('avg_premium'),
                        'renewal_cycle': product_info.get('renewal_cycle'),
                        'surrender_value': product_info.get('surrender_value'),
                        'sales_channel': product_info.get('sales_channel'),
                        'coverage_score': product_info.get('coverage_score', 0),
                        'value_score': product_info.get('value_score', 0),
                        'stability_score': product_info.get('stability_score', 0),
                        'final_score': final_score,
                        'recommendation_type': rec['recommendation_type']
                    })
        
        return enriched
    
    def _matches_user_conditions(self, product: Dict[str, Any], sex: str, monthly_budget: int) -> bool:
        """사용자 조건에 맞는 상품인지 확인"""
        try:
            # 성별 조건 확인
            if sex == 'M':
                premium = product.get('male_premium', 0)
                # 남성인데 남성 보험료가 0이면 제외 (여성 전용 상품)
                if premium == 0:
                    return False
            else:
                premium = product.get('female_premium', 0)
                # 여성인데 여성 보험료가 0이면 제외 (남성 전용 상품)
                if premium == 0:
                    return False
            
            # 예산 조건 확인 (10% 여유분 허용)
            if premium > monthly_budget * 1.1:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"사용자 조건 확인 실패: {str(e)}")
            return True  # 오류 시 포함
    
    def _calculate_quality_score(self, product: Dict[str, Any]) -> float:
        """상품 품질 점수 계산"""
        try:
            coverage_score = product.get('coverage_score', 0)
            value_score = product.get('value_score', 0)
            stability_score = product.get('stability_score', 0)
            
            # 가중 평균으로 품질 점수 계산
            quality_score = (coverage_score * 0.4 + value_score * 0.3 + stability_score * 0.3)
            
            return quality_score
        except:
            return 0.0
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """사용자 행동 분석 요약"""
        try:
            if self.user_profiles is None:
                return {"error": "사용자 데이터가 로드되지 않았습니다"}
            
            # 기본 통계
            total_users = len(self.user_profiles)
            total_interactions = len(self.user_events)
            
            # 성별 분포
            gender_dist = self.user_profiles['sex'].value_counts().to_dict()
            
            # 연령대 분포
            age_groups = pd.cut(self.user_profiles['age'], 
                              bins=[0, 30, 40, 50, 60, 100], 
                              labels=['20대', '30대', '40대', '50대', '60대+'])
            age_dist = age_groups.value_counts().to_dict()
            
            # 흡연 여부 분포
            smoker_dist = self.user_profiles['smoker_flag'].value_counts().to_dict()
            
            # 직업 분포
            occupation_dist = self.user_profiles['occupation_class'].value_counts().to_dict()
            
            # 상호작용 통계
            click_rate = self.user_events['clicked'].mean()
            quote_rate = self.user_events['quoted'].mean()
            purchase_rate = self.user_events['purchased'].mean()
            
            return {
                "total_users": total_users,
                "total_interactions": total_interactions,
                "gender_distribution": gender_dist,
                "age_distribution": age_dist,
                "smoker_distribution": smoker_dist,
                "occupation_distribution": occupation_dist,
                "interaction_rates": {
                    "click_rate": click_rate,
                    "quote_rate": quote_rate,
                    "purchase_rate": purchase_rate
                },
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"분석 요약 생성 실패: {str(e)}")
            return {"error": f"분석 요약 생성 실패: {str(e)}"}
    
    def _normalize_features(self, features: pd.DataFrame) -> np.ndarray:
        """특성 정규화 (Z-score normalization)"""
        features_array = features.values.astype(float)
        mean = np.mean(features_array, axis=0)
        std = np.std(features_array, axis=0)
        # 표준편차가 0인 경우를 방지
        std = np.where(std == 0, 1, std)
        return (features_array - mean) / std
    
    def _cosine_similarity(self, features: np.ndarray) -> np.ndarray:
        """코사인 유사도 계산"""
        # 각 벡터의 L2 norm 계산
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        # 0으로 나누기 방지
        norms = np.where(norms == 0, 1, norms)
        # 정규화된 벡터
        normalized_features = features / norms
        # 코사인 유사도 행렬 계산
        return np.dot(normalized_features, normalized_features.T)
    
    def _cosine_similarity_single(self, query_vector: np.ndarray, features: np.ndarray) -> np.ndarray:
        """단일 벡터와 여러 벡터들 간의 코사인 유사도 계산"""
        # 쿼리 벡터 정규화
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            return np.zeros(features.shape[0])
        query_normalized = query_vector / query_norm
        
        # 각 특성 벡터의 L2 norm 계산
        feature_norms = np.linalg.norm(features, axis=1)
        feature_norms = np.where(feature_norms == 0, 1, feature_norms)
        
        # 정규화된 특성 벡터들
        features_normalized = features / feature_norms.reshape(-1, 1)
        
        # 코사인 유사도 계산
        return np.dot(features_normalized, query_normalized.T).flatten()
