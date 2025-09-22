import pandas as pd
import numpy as np
from typing import Optional, Tuple
from .data_loader import DataLoader
from .models import ProductRecommendation

class RecommendationEngine:
    """암보험 상품 추천 엔진"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.base_df = data_loader.get_base_dataframe()
    
    def _normalize(self, series: pd.Series) -> pd.Series:
        """시리즈를 0-1 범위로 정규화"""
        s = pd.to_numeric(series, errors='coerce')
        mn = s.min()
        mx = s.max()
        if pd.isna(mn) or pd.isna(mx) or mx == mn:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)
    
    def _is_eligible(self, row: pd.Series) -> bool:
        """상품이 가입 자격 요건을 만족하는지 확인"""
        mc = row['min_coverage']
        xc = row['max_coverage']
        val = row['rep_coverage']
        ok_min = True if pd.isna(mc) else (val >= mc)
        ok_max = True if (pd.isna(xc) or xc == 0) else (val <= xc)
        return bool(ok_min and ok_max)
    
    def recommend_products(
        self,
        min_coverage: Optional[int] = None,
        max_premium_avg: Optional[float] = None,
        prefer_non_renewal: bool = True,
        require_sales_channel: Optional[str] = None,
        weights: Tuple[float, float, float] = (0.5, 0.3, 0.2),
        top_n: int = 10
    ) -> list[ProductRecommendation]:
        """
        암보험 상품 추천
        
        Args:
            min_coverage: 최소 보장금액 (원 단위)
            max_premium_avg: 최대 평균 보험료 (원 단위)
            prefer_non_renewal: 비갱신형 선호 여부
            require_sales_channel: 필요한 판매 채널
            weights: 가중치 (보장금액, 가치, 안정성)
            top_n: 추천 상품 개수
            
        Returns:
            추천 상품 리스트
        """
        df = self.base_df.copy()
        
        # 1. 필수 Eligibility 필터 (보장금액 범위)
        df = df[df.apply(self._is_eligible, axis=1)]
        
        # 2. 사용자 입력 필터
        if min_coverage is not None:
            df = df[df['rep_coverage'] >= min_coverage]
        
        # 평균 보험료 계산 및 필터링
        avg_prem = ((df['male_premium'].fillna(0) + df['female_premium'].fillna(0)) / 2).replace(0, np.nan)
        df = df.assign(avg_premium=avg_prem)
        
        if max_premium_avg is not None:
            df = df[(df['avg_premium'].isna()) | (df['avg_premium'] <= max_premium_avg)]
        
        # 판매 채널 필터링
        if require_sales_channel:
            # 온라인 채널은 CM으로 표시되어 있음
            if require_sales_channel.lower() == "온라인":
                df = df[df['sales_channel'].astype(str).str.contains('CM', na=False)]
            else:
                df = df[df['sales_channel'].astype(str).str.contains(require_sales_channel, na=False)]
        
        if df.empty:
            return []
        
        # 3. 점수 계산
        # 보장금액 점수
        cov_score = self._normalize(df['rep_coverage'])
        
        # 가치 점수 (보장금액 / 평균보험료)
        value_raw = df['rep_coverage'] / df['avg_premium']
        value_raw = value_raw.replace([np.inf, -np.inf], np.nan)
        value_score = self._normalize(value_raw)
        
        # 안정성 점수 (비갱신 선호 + 해약환급금)
        renewal_score = df['renewal_pref']
        if prefer_non_renewal:
            renewal_score = renewal_score  # 이미 비갱신형=1.0으로 설정됨
        
        sv_score = self._normalize(df['sv_num']).fillna(0)
        stability_score = 0.7 * renewal_score + 0.3 * sv_score
        
        # 최종 점수 계산
        w_cov, w_val, w_stb = weights
        final_score = w_cov * cov_score + w_val * value_score + w_stb * stability_score
        
        # 결과 정렬 및 상위 N개 선택
        result_df = df.assign(
            coverage_score=cov_score,
            value_score=value_score,
            stability_score=stability_score,
            final_score=final_score
        ).sort_values('final_score', ascending=False).head(top_n)
        
        # ProductRecommendation 객체로 변환
        recommendations = []
        for _, row in result_df.iterrows():
            recommendation = ProductRecommendation(
                policy_id=int(row['policy_id']),
                insurance_company=str(row['insurance_company']),
                product_name=str(row['product_name']),
                coverage_amount=int(row['rep_coverage']) if not pd.isna(row['rep_coverage']) else 0,
                male_premium=float(row['male_premium']) if not pd.isna(row['male_premium']) else None,
                female_premium=float(row['female_premium']) if not pd.isna(row['female_premium']) else None,
                avg_premium=float(row['avg_premium']) if not pd.isna(row['avg_premium']) else None,
                renewal_cycle=str(row['renewal_cycle']),
                surrender_value=str(row['surrender_value']),
                sales_channel=str(row['sales_channel']),
                coverage_score=float(row['coverage_score']),
                value_score=float(row['value_score']),
                stability_score=float(row['stability_score']),
                final_score=float(row['final_score'])
            )
            recommendations.append(recommendation)
        
        return recommendations
