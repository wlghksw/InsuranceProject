import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
import re
import os

logger = logging.getLogger(__name__)

class SavingsPurpose(Enum):
    """저축 목적"""
    SHORT_TERM_SAVINGS = "단기저축"
    MEDIUM_TERM_SAVINGS = "중기저축"
    LONG_TERM_SAVINGS = "장기저축"
    EDUCATION_FUND = "교육자금"
    HOUSING_FUND = "주택자금"
    RETIREMENT_FUND = "노후자금"

class SavingsInsuranceEngine:
    """저축성보험 추천 엔진"""
    
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """저축성보험 데이터 로드"""
        try:
            # 절대 경로로 데이터 로드
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_path, "data", "csv", "savings_comparison.csv")
            self.df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            if self.df is not None and not self.df.empty:
                logger.info(f"저축성보험 데이터 로드 완료: {len(self.df)}개 상품")
                self._preprocess_data()
            else:
                logger.warning("저축성보험 데이터가 없습니다.")
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
            numeric_columns = ['유지기간', '납입보험료', '계약자적립액', '적립률', '해약환급금', 
                             '계약자적립액_1', '적립률_1', '해약환급금_1', '최저보증이율', 
                             '현재공시이율', '평균공시이율', '확정이율', '사업비율', '위험보장']
            
            for col in numeric_columns:
                if col in self.df.columns:
                    # 숫자에서 쉼표, 공백, "원" 제거
                    self.df[col] = self.df[col].astype(str).str.replace(',', '').str.replace(' ', '').str.replace('원', '')
                    # 퍼센트 기호 제거
                    self.df[col] = self.df[col].str.replace('%', '')
                    # 숫자로 변환 (오류 시 NaN)
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # 상품 ID 생성
            self.df['product_id'] = range(1, len(self.df) + 1)
            
            # 숫자 컬럼만 결측값 처리
            numeric_cols = ['납입보험료', '해약환급금', '적립률', '현재공시이율', '최저보증이율', '유지기간']
            for col in numeric_cols:
                if col in self.df.columns:
                    self.df[col] = self.df[col].fillna(0)
            
            logger.info("저축성보험 데이터 전처리 완료")
            
        except Exception as e:
            logger.error(f"데이터 전처리 중 오류: {str(e)}")
    
    def get_recommendations(self, age: int, monthly_budget: int, purpose: str, 
                          min_guaranteed_rate: Optional[float] = None,
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """저축성보험 추천"""
        if self.df is None:
            logger.warning("데이터가 로드되지 않았습니다.")
            return []
        
        try:
            # 기본 필터링 (회사 배제 없음)
            filtered_df = self.df.copy()
            
            # 납입금 계산 (납입방법에 따라 다르게 처리)
            def calculate_monthly_premium(row):
                """월 납입금 계산 - 일시납과 월납을 구분하여 처리"""
                if row['납입방법'] == '일시납':
                    # 일시납은 월 납입 개념이 없으므로 총액을 그대로 반환
                    return row['납입보험료'] 
                else:
                    # 월납 상품의 납입기간이 유지기간과 같다고 가정
                    term_months = row['유지기간'] * 12 if row['유지기간'] > 0 else 1
                    # 납입보험료(총액) / (유지기간 * 12) = 월 납입금
                    return row['납입보험료'] / term_months
            
            # '월 납입금' 계산 필드 생성 (일시납은 총액으로 처리)
            filtered_df['monthly_premium_value'] = filtered_df.apply(calculate_monthly_premium, axis=1)
            
            # 예산 필터링 (보수적 기준 적용)
            if monthly_budget > 0:
                # 월납/전기납 상품: 월 납입금이 예산의 1.1배 이하
                is_monthly = filtered_df['납입방법'].isin(['월납', '전기납'])
                월납_mask = is_monthly & (filtered_df['monthly_premium_value'] <= monthly_budget * 1.1)
                
                # 일시납 상품: 기본적으로 제외 (사용자가 명시적으로 요청한 경우만 허용)
                일시납_mask = (filtered_df['납입방법'] == '일시납') & \
                              (filtered_df['monthly_premium_value'] <= monthly_budget * 12)  # 1년치 예산 이하만
                
                filtered_df = filtered_df[월납_mask | 일시납_mask]
            
            # 최저보증이율 필터링
            if min_guaranteed_rate is not None:
                filtered_df = filtered_df[filtered_df['최저보증이율'] >= min_guaranteed_rate]
            
            # 필터링 결과가 비어있으면 예산 필터를 더 완화
            if filtered_df.empty:
                logger.warning("필터링 결과가 비어있어 예산 필터를 더 완화합니다.")
                filtered_df = self.df.copy()
                # 예산 필터를 더 완화
                if monthly_budget > 0:
                    filtered_df['monthly_premium_value'] = filtered_df.apply(calculate_monthly_premium, axis=1)
                    
                    # 월납/전기납 상품: 월 납입금이 월 예산의 2배 이하
                    is_monthly = filtered_df['납입방법'].isin(['월납', '전기납'])
                    월납_mask_relaxed = is_monthly & (filtered_df['monthly_premium_value'] <= monthly_budget * 2.0)
                    
                    # 일시납 상품: 2년치 예산까지 허용
                    일시납_mask_relaxed = (filtered_df['납입방법'] == '일시납') & \
                                         (filtered_df['monthly_premium_value'] <= monthly_budget * 24)
                    
                    filtered_df = filtered_df[월납_mask_relaxed | 일시납_mask_relaxed]
                
                # 그래도 비어있으면 전체 데이터 사용
                if filtered_df.empty:
                    logger.warning("완화된 필터링도 실패하여 전체 데이터를 반환합니다.")
                    filtered_df = self.df.copy()
                    # 전체 데이터에도 납입금 계산
                    filtered_df['monthly_premium_value'] = filtered_df.apply(calculate_monthly_premium, axis=1)
            
            # 점수 계산
            logger.info(f"필터링된 상품 수: {len(filtered_df)}")
            filtered_df = self._calculate_scores(filtered_df, monthly_budget, purpose)
            
            # 상위 5개 상품의 점수 로그
            top_products = filtered_df.nlargest(5, 'final_score')
            logger.info(f"상위 5개 상품 점수:")
            for idx, (_, row) in enumerate(top_products.iterrows()):
                logger.info(f"  {idx+1}. {row['보험회사명']} - {row['상품명']}: {row['final_score']:.2f}점")
            
            # 목적별 특화된 추천 로직
            recommendations = []
            
            if purpose == "단기저축":
                # 단기저축: 월납/전기납 상품 우선 선택
                priority_products = filtered_df[
                    filtered_df['납입방법'].isin(['월납', '전기납'])
                ].sort_values('final_score', ascending=False)
                
                if len(priority_products) < top_n:
                    remaining = filtered_df[~filtered_df.index.isin(priority_products.index)]
                    priority_products = pd.concat([priority_products, remaining])
                
                recommendations = priority_products.head(top_n)
                
            elif purpose == "장기저축":
                # 장기저축: 최저보증이율 높은 상품 우선 선택
                priority_products = filtered_df[
                    filtered_df['최저보증이율'] >= 1.0
                ].sort_values('final_score', ascending=False)
                
                if len(priority_products) < top_n:
                    remaining = filtered_df[~filtered_df.index.isin(priority_products.index)]
                    priority_products = pd.concat([priority_products, remaining])
                
                recommendations = priority_products.head(top_n)
                
            elif purpose == "노후자금":
                # 노후자금: 안정성 최우선 (최저보증이율 + 장기 유지)
                priority_products = filtered_df[
                    (filtered_df['최저보증이율'] >= 0.5) & 
                    (filtered_df['유지기간'] >= 5)
                ].sort_values('final_score', ascending=False)
                
                if len(priority_products) < top_n:
                    remaining = filtered_df[~filtered_df.index.isin(priority_products.index)]
                    priority_products = pd.concat([priority_products, remaining])
                
                recommendations = priority_products.head(top_n)
                
            elif purpose == "교육자금":
                # 교육자금: 수익성과 안정성 균형 (현재공시이율 + 최저보증이율)
                priority_products = filtered_df[
                    (filtered_df['현재공시이율'] >= 2.0) & 
                    (filtered_df['최저보증이율'] >= 0.5)
                ].sort_values('final_score', ascending=False)
                
                if len(priority_products) < top_n:
                    remaining = filtered_df[~filtered_df.index.isin(priority_products.index)]
                    priority_products = pd.concat([priority_products, remaining])
                
                recommendations = priority_products.head(top_n)
                
            else:
                # 기본: 점수 순으로 선택
                recommendations = filtered_df.head(top_n)
            
            # DataFrame으로 변환
            recommendations = pd.DataFrame(recommendations)
            
            # 결과 변환
            result = []
            for _, row in recommendations.iterrows():
                recommendation = {
                    'product_id': str(row['product_id']),
                    'company': row['보험회사명'],
                    'product_name': row['상품명'],
                    'product_type': '저축성보험',
                    'score': round(row['final_score'], 2),
                    'guaranteed_rate': f"{row['최저보증이율']:.2f}%" if pd.notna(row['최저보증이율']) else "정보없음",
                    'current_rate': f"{row['현재공시이율']:.2f}%" if pd.notna(row['현재공시이율']) else "정보없음",
                    'term': f"{row['유지기간']:.0f}년",
                    'monthly_premium': self._format_premium_display(row),
                    'surrender_value': f"{row['해약환급금']:,.0f}원" if pd.notna(row['해약환급금']) and row['해약환급금'] > 0 else "정보없음",
                    'payment_method': row['납입방법'],
                    'universal': '유니버셜' if row['유니버셜여부'] == '유니버셜' else '비유니버셜',
                    'sales_channel': row['판매채널'],
                    'recommendation_reason': self._generate_recommendation_reason(row, purpose)
                }
                result.append(recommendation)
            
            logger.info(f"저축성보험 추천 상품 {len(result)}개 반환")
            return result
            
        except Exception as e:
            logger.error(f"추천 생성 중 오류: {str(e)}")
            return []
    
    def _calculate_scores(self, df: pd.DataFrame, monthly_budget: int, purpose: str) -> pd.DataFrame:
        """점수 계산 - 정규화된 점수로 균형잡힌 평가"""
        try:
            # 기본 점수 초기화
            df['return_score'] = 0.0
            df['stability_score'] = 0.0
            df['flexibility_score'] = 0.0
            df['age_score'] = 0.0
            df['budget_score'] = 0.0
            df['final_score'] = 0.0
            
            # 정규화 함수 (0-100 스케일)
            def normalize_score(series):
                if series.empty or series.max() == series.min():
                    return pd.Series([50] * len(series), index=series.index)  # 중간값 반환
                return (series - series.min()) / (series.max() - series.min()) * 100
            
            # 수익성 점수 (적립률, 현재공시이율 기준) - 정규화 적용
            if '적립률' in df.columns:
                적립률_score = normalize_score(df['적립률'].fillna(0))
                df['return_score'] += 적립률_score * 0.6
            
            if '현재공시이율' in df.columns:
                # 현재공시이율 클리핑 (0-15%)
                capped_rate = df['현재공시이율'].fillna(0).clip(lower=0, upper=15)
                이율_score = normalize_score(capped_rate)
                df['return_score'] += 이율_score * 0.4
            
            # 안정성 점수 (최저보증이율, 유지기간 기준) - 정규화 적용
            if '최저보증이율' in df.columns:
                보증이율_score = normalize_score(df['최저보증이율'].fillna(0))
                df['stability_score'] += 보증이율_score * 0.7
            
            if '유지기간' in df.columns:
                # 기간 점수 (3-7년이 최적)
                기간_score = np.where(
                    (df['유지기간'] >= 3) & (df['유지기간'] <= 7), 100, 
                    np.where(df['유지기간'] < 3, 60, 80)
                )
                df['stability_score'] += 기간_score * 0.3
            
            # 유연성 점수 (납입방법 기준)
            df['flexibility_score'] = np.where(df['납입방법'].isin(['월납', '전기납']), 80, 40)
            
            # 나이별 점수 (고정)
            df['age_score'] = df['return_score'] * 0.3 + df['stability_score'] * 0.2
            
            # 예산별 점수 (예산이 클수록 수익성 중시)
            if monthly_budget < 200000:
                df['budget_score'] = df['stability_score'] * 0.3 + df['flexibility_score'] * 0.2
            elif monthly_budget < 500000:
                df['budget_score'] = df['return_score'] * 0.3 + df['stability_score'] * 0.2
            else:
                df['budget_score'] = df['return_score'] * 0.4 + df['stability_score'] * 0.1
            
            # 목적별 가중치 적용
            if purpose == "단기저축":
                # 단기저축: 유연성 최우선 (월납/전기납 선호)
                df['final_score'] = df['flexibility_score'] * 0.6 + df['return_score'] * 0.3 + df['budget_score'] * 0.1
            elif purpose == "중기저축":
                # 중기저축: 안정성과 유연성 균형
                df['final_score'] = df['stability_score'] * 0.5 + df['flexibility_score'] * 0.3 + df['return_score'] * 0.2
            elif purpose == "장기저축":
                # 장기저축: 안정성 최우선 (최저보증이율, 장기 유지 선호)
                df['final_score'] = df['stability_score'] * 0.7 + df['return_score'] * 0.2 + df['flexibility_score'] * 0.1
            elif purpose == "교육자금":
                # 교육자금: 안정성과 수익성 균형 (확실한 자금 마련)
                df['final_score'] = df['stability_score'] * 0.6 + df['return_score'] * 0.3 + df['flexibility_score'] * 0.1
            elif purpose == "주택자금":
                # 주택자금: 안정성과 유연성 균형 (중도 해지 가능성)
                df['final_score'] = df['stability_score'] * 0.5 + df['flexibility_score'] * 0.4 + df['return_score'] * 0.1
            elif purpose == "노후자금":
                # 노후자금: 안정성 최우선 (확실한 노후 준비)
                df['final_score'] = df['stability_score'] * 0.8 + df['return_score'] * 0.15 + df['flexibility_score'] * 0.05
            else:  # 기본값
                df['final_score'] = df['stability_score'] * 0.5 + df['flexibility_score'] * 0.3 + df['return_score'] * 0.2
            
            return df
            
        except Exception as e:
            logger.error(f"점수 계산 중 오류: {str(e)}")
            return df
    
    def _generate_recommendation_reason(self, row: pd.Series, purpose: str) -> str:
        """추천 이유 생성 - 사용자 조건에 맞춘 개인화된 이유"""
        reasons = []
        
        # 수익성 관련
        if pd.notna(row['현재공시이율']) and row['현재공시이율'] > 2.0:
            reasons.append(f"높은 현재공시이율({row['현재공시이율']:.2f}%)")
        
        if pd.notna(row['적립률']) and row['적립률'] > 100:
            reasons.append(f"우수한 적립률({row['적립률']:.1f}%)")
        
        # 안정성 관련
        if pd.notna(row['최저보증이율']) and row['최저보증이율'] > 0:
            reasons.append(f"보장된 최저이율({row['최저보증이율']:.2f}%)")
        
        # 기간 관련
        if pd.notna(row['유지기간']):
            if row['유지기간'] <= 3:
                reasons.append("단기 유연성")
            elif row['유지기간'] >= 7:
                reasons.append("장기 안정성")
            else:
                reasons.append("중기 균형")
        
        # 유니버셜 여부
        if row['유니버셜여부'] == '유니버셜':
            reasons.append("유니버셜 상품(유연한 납입)")
        
        # 목적별 특화
        if purpose == "단기저축":
            reasons.append("단기 저축에 적합")
            reasons.append("빠른 자금 회수 가능")
        elif purpose == "중기저축":
            reasons.append("중기 저축에 적합")
            reasons.append("안정적인 수익 기대")
        elif purpose == "장기저축":
            reasons.append("장기 저축에 적합")
            reasons.append("장기적 자산 증식")
        elif purpose == "교육자금":
            reasons.append("자녀 교육비 준비에 최적")
        elif purpose == "주택자금":
            reasons.append("주택 구매 자금 마련에 적합")
        elif purpose == "노후자금":
            reasons.append("안정적인 노후 준비")
        
        return " | ".join(reasons) if reasons else "추천 상품"
    
    def _format_premium_display(self, row: pd.Series) -> str:
        """납입방법에 따라 납입금 표시 형식 결정"""
        if 'monthly_premium_value' not in row or pd.isna(row['monthly_premium_value']) or row['monthly_premium_value'] <= 0:
            return "정보없음"
        
        if row['납입방법'] == '일시납':
            # 일시납은 총 납입보험료를 표시
            return f"{row['monthly_premium_value']:,.0f}원 (일시납)"
        else:
            # 월납은 월 납입금을 표시
            return f"{row['monthly_premium_value']:,.0f}원/월"
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """전체 상품 목록 반환"""
        if self.df is None:
            return []
        
        try:
            result = []
            for _, row in self.df.iterrows():
                product = {
                    'product_id': str(row['product_id']),
                    'company': row['보험회사명'],
                    'product_name': row['상품명'],
                    'term': f"{row['유지기간']:.0f}년",
                    'guaranteed_rate': f"{row['최저보증이율']:.2f}%" if pd.notna(row['최저보증이율']) else "정보없음",
                    'current_rate': f"{row['현재공시이율']:.2f}%" if pd.notna(row['현재공시이율']) else "정보없음",
                    'universal': '유니버셜' if row['유니버셜여부'] == '유니버셜' else '비유니버셜',
                    'sales_channel': row['판매채널']
                }
                result.append(product)
            
            return result
            
        except Exception as e:
            logger.error(f"전체 상품 목록 조회 중 오류: {str(e)}")
            return []
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """저축성보험 분석 요약 정보"""
        if self.df is None:
            return {"error": "데이터가 로드되지 않았습니다."}
        
        try:
            summary = {
                "total_products": len(self.df),
                "companies": self.df['보험회사명'].nunique(),
                "avg_guaranteed_rate": self.df['최저보증이율'].mean(),
                "avg_current_rate": self.df['현재공시이율'].mean(),
                "avg_term": self.df['유지기간'].mean(),
                "payment_methods": self.df['납입방법'].value_counts().to_dict(),
                "universal_products": len(self.df[self.df['유니버셜여부'] == '유니버셜']),
                "sales_channels": self.df['판매채널'].value_counts().to_dict()
            }
            return summary
            
        except Exception as e:
            logger.error(f"분석 요약 생성 중 오류: {str(e)}")
            return {"error": f"분석 요약 생성 중 오류: {str(e)}"}
