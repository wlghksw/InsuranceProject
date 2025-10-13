"""
상해보험 추천 엔진
"""
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


class AccidentInsuranceEngine:
    """상해보험 추천 엔진 클래스"""
    
    def __init__(self):
        """초기화 및 데이터 로드"""
        self.df = None
        self.load_data()
    
    def load_data(self):
        """CSV 파일에서 상해보험 데이터 로드"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_path, "data", "csv", "accident.csv")
            
            logger.info(f"상해보험 데이터 로드 중: {csv_path}")
            
            if not os.path.exists(csv_path):
                logger.error(f"상해보험 데이터 파일을 찾을 수 없습니다: {csv_path}")
                self.df = None
                return
            
            self.df = pd.read_csv(csv_path)
            logger.info(f"상해보험 데이터 로드 완료: {len(self.df)}개 상품")
            
        except Exception as e:
            logger.error(f"상해보험 데이터 로드 중 오류: {str(e)}")
            self.df = None
    
    def get_recommendations(self, age: int = 30, sex: str = "male", 
                          top_n: int = 5, sort_by: str = "default"):
        """
        상해보험 추천
        
        Args:
            age: 나이
            sex: 성별 ("male" 또는 "female")
            top_n: 추천 상품 개수
            sort_by: 정렬 기준 ("default", "premium", "coverage")
        
        Returns:
            추천 상품 리스트
        """
        if self.df is None or self.df.empty:
            logger.error("상해보험 데이터가 로드되지 않았습니다")
            return []
        
        try:
            # 데이터 복사
            df = self.df.copy()
            
            # 나이 필터링 (현재는 모든 상품 포함)
            df = df[df['male_premium'] > 0]
            
            # 성별에 따른 보험료 선택
            if sex.lower() == 'male':
                df['selected_premium'] = df['male_premium']
            else:
                df['selected_premium'] = df['female_premium']
            
            # 평균 보험료 계산
            df['avg_premium'] = (df['male_premium'] + df['female_premium']) / 2
            
            # 추천 점수 계산
            df['coverage_score'] = df['coverage_amount'] / df['coverage_amount'].max()
            df['value_score'] = 1 - (df['avg_premium'] / df['avg_premium'].max())
            df['stability_score'] = df['renewal_cycle'].apply(
                lambda x: 1.0 if '비갱신' in str(x) else 0.5
            )
            df['final_score'] = (
                df['coverage_score'] * 0.5 + 
                df['value_score'] * 0.4 + 
                df['stability_score'] * 0.1
            )
            
            # 정렬
            if sort_by == "premium":
                df = df.sort_values('avg_premium')
            elif sort_by == "coverage":
                df = df.sort_values('coverage_amount', ascending=False)
            else:
                df = df.sort_values('final_score', ascending=False)
            
            # 상위 N개 선택
            df = df.head(top_n)
            
            # 결과를 딕셔너리 리스트로 변환
            recommendations = []
            for idx, row in df.iterrows():
                rec = {
                    "policy_id": int(idx),
                    "insurance_company": str(row['insurance_company']),
                    "product_name": str(row['product_name']),
                    "coverage_amount": int(row['coverage_amount']),
                    "male_premium": float(row['male_premium']),
                    "female_premium": float(row['female_premium']),
                    "avg_premium": float(row['avg_premium']),
                    "renewal_cycle": str(row['renewal_cycle']),
                    "surrender_value": "N/A",
                    "sales_channel": "온라인",
                    "coverage_score": float(row['coverage_score']),
                    "value_score": float(row['value_score']),
                    "stability_score": float(row['stability_score']),
                    "final_score": float(row['final_score'])
                }
                recommendations.append(rec)
            
            logger.info(f"상해보험 추천 완료: {len(recommendations)}개 상품")
            return recommendations
            
        except Exception as e:
            logger.error(f"상해보험 추천 중 오류: {str(e)}")
            return []

