import pandas as pd
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class SavingsRecommendationEngine:
    """사용자 프로필 기반 연금 보험 추천 엔진"""
    
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """연금 보험 데이터 로드"""
        try:
            csv_path = "../Product/savings_products_cleaned.csv"
            self.df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            if self.df is not None and not self.df.empty:
                logger.info(f"연금 보험 데이터 로드 완료: {len(self.df)}개 상품")
                self._preprocess_data()
            else:
                logger.warning("연금 보험 데이터가 없습니다.")
                self.df = None
                
        except Exception as e:
            logger.error(f"데이터 로드 중 오류: {str(e)}")
            self.df = None
    
    def _preprocess_data(self):
        """데이터 전처리"""
        if self.df is None:
            return
        
        try:
            # 숫자 데이터 정리
            numeric_columns = ['유지기간', '납입보험료', '계약자적립액', '적립률', '해약환급금']
            
            for col in numeric_columns:
                if col in self.df.columns:
                    # 문자열에서 숫자만 추출
                    self.df[col] = self.df[col].astype(str).str.replace(',', '').str.replace('원', '').str.replace('%', '').str.replace(' ', '')
                    # 빈 값이나 '-' 처리
                    self.df[col] = self.df[col].replace(['-', '', 'nan'], np.nan)
                    # 숫자로 변환
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # 금리 데이터 정리
            rate_columns = ['최저보증이율', '현재공시이율', '평균공시이율']
            for col in rate_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.replace('%', '').str.replace(' ', '')
                    self.df[col] = self.df[col].replace(['-', '', 'nan'], np.nan)
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # 상품 ID 생성
            self.df['product_id'] = self.df.index.astype(str).str.zfill(3)
            
            logger.info("데이터 전처리 완료")
            
        except Exception as e:
            logger.error(f"데이터 전처리 중 오류: {str(e)}")
    
    def get_recommendations(self, age: int, monthly_budget: int, purpose: str, top_n: int = 5) -> List[dict]:
        """사용자 프로필 기반 연금 보험 추천"""
        
        if self.df is None or self.df.empty:
            return []
        
        try:
            # 사용자 프로필에 따른 필터링 및 점수 계산
            filtered_df = self._filter_by_profile(age, monthly_budget, purpose)
            
            if filtered_df.empty:
                return []
            
            # 점수 계산 및 정렬
            scored_df = self._calculate_profile_score(filtered_df, age, monthly_budget, purpose)
            
            # 상위 N개 추천
            top_products = scored_df.head(top_n)
            
            # 추천 결과 포맷팅
            recommendations = []
            for _, row in top_products.iterrows():
                recommendation = self._format_recommendation(row, monthly_budget)
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"추천 처리 중 오류: {str(e)}")
            return []
    
    def _filter_by_profile(self, age: int, monthly_budget: int, purpose: str) -> pd.DataFrame:
        """사용자 프로필에 따른 기본 필터링 (관대한 조건)"""
        filtered_df = self.df.copy()
        
        try:
            # 예산 필터링을 더 관대하게 수정
            if monthly_budget > 0:
                # 월 예산을 연간 예산으로 변환 (12개월)
                annual_budget = monthly_budget * 12
                
                # 납입보험료가 예산의 50%~200% 범위 내인 상품 필터링 (더 넓은 범위)
                budget_min = annual_budget * 0.5
                budget_max = annual_budget * 2.0
                
                # 납입보험료가 예산 범위 내인 상품만 선택
                filtered_df = filtered_df[
                    (filtered_df['납입보험료'] >= budget_min) & 
                    (filtered_df['납입보험료'] <= budget_max)
                ]
            
            # 목적에 따른 필터링을 더 관대하게 수정
            if purpose == "연금준비":
                # 장기 유지기간(3년 이상) 우선 (5년에서 3년으로 완화)
                filtered_df = filtered_df[filtered_df['유지기간'] >= 3]
            elif purpose == "단기저축":
                # 단기 유지기간(5년 이하) 우선 (3년에서 5년으로 완화)
                filtered_df = filtered_df[filtered_df['유지기간'] <= 5]
            elif purpose == "세제혜택":
                # 유니버셜 상품이 있으면 우선, 없으면 전체
                universal_products = filtered_df[filtered_df['유니버셜여부'] == '유니버셜']
                if len(universal_products) > 0:
                    filtered_df = universal_products
                # 유니버셜 상품이 없으면 전체 상품 유지
            
            # 나이에 따른 필터링을 더 관대하게 수정
            if age < 30:
                # 젊은 연령대는 높은 수익률 상품 우선 (조건 완화)
                high_rate_products = filtered_df[filtered_df['현재공시이율'] >= 1.0]
                if len(high_rate_products) > 0:
                    filtered_df = high_rate_products
            elif age > 50:
                # 중장년층은 안정성 우선 (조건 완화)
                stable_products = filtered_df[filtered_df['최저보증이율'] >= 0.0]
                if len(stable_products) > 0:
                    filtered_df = stable_products
            
        except Exception as e:
            logger.error(f"필터링 중 오류: {str(e)}")
            # 오류 발생 시 전체 데이터 반환
            return self.df.copy()
        
        # 필터링 결과가 비어있으면 전체 데이터 반환
        if filtered_df.empty:
            logger.warning("필터링 결과가 비어있어 전체 데이터를 반환합니다.")
            return self.df.copy()
        
        return filtered_df
    
    def _calculate_profile_score(self, df: pd.DataFrame, age: int, monthly_budget: int, purpose: str) -> pd.DataFrame:
        """사용자 프로필 기반 점수 계산"""
        scored_df = df.copy()
        scores = []
        
        for _, row in scored_df.iterrows():
            score = 0.0
            
            try:
                # 1. 수익률 점수 (40%)
                rate_score = self._calculate_rate_score(row)
                score += rate_score * 0.4
                
                # 2. 목적 적합성 점수 (30%)
                purpose_score = self._calculate_purpose_score(row, purpose)
                score += purpose_score * 0.3
                
                # 3. 나이 적합성 점수 (20%)
                age_score = self._calculate_age_score(row, age)
                score += age_score * 0.2
                
                # 4. 예산 적합성 점수 (10%)
                budget_score = self._calculate_budget_score(row, monthly_budget)
                score += budget_score * 0.1
                
            except Exception as e:
                logger.error(f"점수 계산 중 오류: {str(e)}")
                score = 50.0  # 기본 점수
            
            scores.append(score)
        
        scored_df['score'] = scores
        return scored_df.sort_values('score', ascending=False)
    
    def _calculate_rate_score(self, row) -> float:
        """수익률 점수 계산"""
        score = 0.0
        
        # 현재공시이율 점수 (60%)
        current_rate = row.get('현재공시이율', 0)
        if pd.notna(current_rate):
            score += min(current_rate * 10, 60)  # 최대 60점
        
        # 최저보증이율 점수 (40%)
        guaranteed_rate = row.get('최저보증이율', 0)
        if pd.notna(guaranteed_rate):
            score += min(guaranteed_rate * 15, 40)  # 최대 40점
        
        return score
    
    def _calculate_purpose_score(self, row, purpose: str) -> float:
        """목적 적합성 점수 계산"""
        score = 0.0
        
        if purpose == "연금준비":
            # 장기 유지기간, 높은 적립률
            term = row.get('유지기간', 0)
            if pd.notna(term) and term >= 5:
                score += 30
            elif pd.notna(term) and term >= 3:
                score += 15
            
            # 적립률 점수
            accumulation_rate = row.get('적립률', 0)
            if pd.notna(accumulation_rate) and accumulation_rate >= 100:
                score += 50
            elif pd.notna(accumulation_rate) and accumulation_rate >= 90:
                score += 30
        
        elif purpose == "단기저축":
            # 단기 유지기간, 빠른 회수
            term = row.get('유지기간', 0)
            if pd.notna(term) and term <= 3:
                score += 40
            elif pd.notna(term) and term <= 5:
                score += 20
            
            # 해약환급금 점수
            surrender_value = row.get('해약환급금', 0)
            if pd.notna(surrender_value) and surrender_value > 0:
                score += 30
        
        elif purpose == "세제혜택":
            # 유니버셜 상품 우선
            if row.get('유니버셜여부') == '유니버셜':
                score += 60
            
            # 납입방법 유연성
            payment_method = str(row.get('납입방법', ''))
            if '월납' in payment_method:
                score += 20
        
        return score
    
    def _calculate_age_score(self, row, age: int) -> float:
        """나이 적합성 점수 계산"""
        score = 0.0
        
        if age < 30:
            # 젊은 연령대: 높은 수익률, 장기 투자
            current_rate = row.get('현재공시이율', 0)
            if pd.notna(current_rate) and current_rate >= 3.0:
                score += 50
            
            term = row.get('유지기간', 0)
            if pd.notna(term) and term >= 5:
                score += 30
        
        elif age >= 50:
            # 중장년층: 안정성, 보장성
            guaranteed_rate = row.get('최저보증이율', 0)
            if pd.notna(guaranteed_rate) and guaranteed_rate >= 2.0:
                score += 50
            
            # 유니버셜 상품 선호
            if row.get('유니버셜여부') == '유니버셜':
                score += 30
        
        else:
            # 중년층: 균형잡힌 접근
            score += 40
        
        return score
    
    def _calculate_budget_score(self, row, monthly_budget: int) -> float:
        """예산 적합성 점수 계산"""
        score = 0.0
        
        premium = row.get('납입보험료', 0)
        if pd.notna(premium) and monthly_budget > 0:
            annual_budget = monthly_budget * 12
            # 예산 대비 적절한 보험료
            if premium <= annual_budget:
                score += 50
            elif premium <= annual_budget * 1.2:
                score += 30
        
        return score
    
    def _format_recommendation(self, row, monthly_budget: int) -> dict:
        """추천 결과 포맷팅"""
        try:
            # 월 예상 납입액 계산
            premium = row.get('납입보험료', 0)
            monthly_premium = premium / 12 if pd.notna(premium) and premium > 0 else monthly_budget
            
            # 적립률 계산
            accumulation_rate = row.get('적립률', 0)
            accumulation_rate_str = f"{accumulation_rate:.1f}%" if pd.notna(accumulation_rate) else "정보없음"
            
            # 현재공시이율
            current_rate = row.get('현재공시이율', 0)
            current_rate_str = f"{current_rate:.2f}%" if pd.notna(current_rate) else "정보없음"
            
            # 해약환급금
            surrender_value = row.get('해약환급금', 0)
            surrender_value_str = f"{surrender_value:,.0f}원" if pd.notna(surrender_value) and surrender_value > 0 else "정보없음"
            
            return {
                "product_id": row.get('product_id', ''),
                "company": str(row.get('보험회사명', '정보없음')),
                "product_name": str(row.get('상품명', '정보없음')),
                "product_type": "연금보험",
                "score": float(row.get('score', 0.0)),
                "monthly_premium": f"{monthly_premium:,.0f}원",
                "term": f"{row.get('유지기간', 0)}년",
                "accumulation_rate": accumulation_rate_str,
                "current_rate": current_rate_str,
                "guaranteed_rate": f"{row.get('최저보증이율', 0):.2f}%" if pd.notna(row.get('최저보증이율')) else "정보없음",
                "surrender_value": surrender_value_str,
                "payment_method": str(row.get('납입방법', '정보없음')),
                "universal": str(row.get('유니버셜여부', '정보없음')),
                "sales_channel": str(row.get('판매채널', '정보없음')),
                "recommendation_reason": self._get_recommendation_reason(row, monthly_budget)
            }
            
        except Exception as e:
            logger.error(f"추천 결과 포맷팅 중 오류: {str(e)}")
            return {
                "product_id": "error",
                "company": "정보없음",
                "product_name": "정보없음",
                "product_type": "연금보험",
                "score": 0.0,
                "recommendation_reason": "데이터 처리 중 오류가 발생했습니다."
            }
    
    def _get_recommendation_reason(self, row, monthly_budget: int) -> str:
        """추천 이유 생성"""
        reasons = []
        
        try:
            # 수익률 관련
            current_rate = row.get('현재공시이율', 0)
            if pd.notna(current_rate) and current_rate >= 3.0:
                reasons.append(f"높은 현재공시이율({current_rate:.2f}%)")
            
            # 적립률 관련
            accumulation_rate = row.get('적립률', 0)
            if pd.notna(accumulation_rate) and accumulation_rate >= 100:
                reasons.append(f"우수한 적립률({accumulation_rate:.1f}%)")
            
            # 유지기간 관련
            term = row.get('유지기간', 0)
            if pd.notna(term):
                if term >= 5:
                    reasons.append(f"장기 안정성({term}년)")
                elif term <= 3:
                    reasons.append(f"단기 유연성({term}년)")
            
            # 유니버셜 관련
            if row.get('유니버셜여부') == '유니버셜':
                reasons.append("유니버셜 상품(유연한 납입)")
            
            # 예산 적합성
            if monthly_budget > 0:
                reasons.append(f"월 {monthly_budget:,}원 예산에 적합")
            
        except Exception as e:
            logger.error(f"추천 이유 생성 중 오류: {str(e)}")
        
        if not reasons:
            reasons.append("사용자 프로필에 적합한 상품")
        
        return " | ".join(reasons)
    
    def get_analytics_summary(self) -> dict:
        """연금 보험 분석 요약 정보"""
        if self.df is None or self.df.empty:
            return {"error": "데이터가 없습니다."}
        
        try:
            return {
                "total_products": len(self.df),
                "companies": self.df['보험회사명'].nunique(),
                "avg_current_rate": f"{self.df['현재공시이율'].mean():.2f}%",
                "avg_guaranteed_rate": f"{self.df['최저보증이율'].mean():.2f}%",
                "avg_accumulation_rate": f"{self.df['적립률'].mean():.1f}%",
                "universal_products": len(self.df[self.df['유니버셜여부'] == '유니버셜']),
                "status": "active"
            }
        except Exception as e:
            logger.error(f"분석 요약 생성 중 오류: {str(e)}")
            return {"error": f"분석 중 오류: {str(e)}"}
