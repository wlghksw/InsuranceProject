# app/recommendation_engine.py

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
import re

from .data_loader import DataLoader
from .models import ProductRecommendation, SortOrder

class RecommendationEngine:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def _normalize(self, series: pd.Series) -> pd.Series:
        s = pd.to_numeric(series, errors='coerce')
        mn, mx = s.min(), s.max()
        if pd.isna(mn) or pd.isna(mx) or mx == mn:
            return pd.Series(0.5, index=s.index)
        return (s - mn) / (mx - mn)

    def _convert_to_recommendation_list(self, df: pd.DataFrame) -> List[ProductRecommendation]:
        recommendations = []
        df_cleaned = df.replace({np.nan: None})
        for _, row in df_cleaned.iterrows():
            rec_data = row.to_dict()
            recommendations.append(ProductRecommendation(**rec_data))
        return recommendations

    def recommend_products(self,
                           min_coverage: Optional[int] = None,
                           max_premium_avg: Optional[float] = None,
                           prefer_non_renewal: bool = True,
                           require_sales_channel: Optional[str] = None,
                           sex: Optional[str] = None,
                           monthly_budget: Optional[int] = None,
                           weights: Tuple[float, float, float] = (0.5, 0.3, 0.2),
                           top_n: int = 10,
                           sort_by: SortOrder = SortOrder.DEFAULT,
                           **kwargs) -> List[ProductRecommendation]:
        """암보험 상품을 추천합니다."""
        df = self.data_loader.get_base_dataframe('cancer')
        print("기존 암보험 추천 로직 실행")

        # 필터링
        if min_coverage:
            df = df[df['coverage_amount'] >= min_coverage]
        if max_premium_avg:
            df = df[df['avg_premium'] <= max_premium_avg]
        if require_sales_channel:
            df = df[df['sales_channel'].str.contains(require_sales_channel, na=False)]

        if sex and monthly_budget:
            premium_col = 'male_premium' if sex == 'M' else 'female_premium'
            df = df[df[premium_col].notna() & (df[premium_col] <= monthly_budget)]

        df.dropna(subset=['coverage_amount'], inplace=True)

        if df.empty:
            return []

        # 점수 계산
        df['coverage_score'] = self._normalize(df['coverage_amount'])
        df['value_score'] = 1 - self._normalize(df['avg_premium'])
        df['stability_score'] = self._normalize(df.get('surrender_value_num', 0))

        if prefer_non_renewal:
            df['stability_score'] += df['renewal_cycle'].apply(lambda x: 0.2 if '비갱신' in str(x) else 0)

        coverage_weight, value_weight, stability_weight = weights
        df['final_score'] = (
                df['coverage_score'] * coverage_weight +
                df['value_score'] * value_weight +
                df['stability_score'] * stability_weight
        )

        # 정렬
        if sort_by == SortOrder.COVERAGE_DESC:
            sorted_df = df.sort_values(by='coverage_amount', ascending=False)
        elif sort_by == SortOrder.COVERAGE_ASC:
            sorted_df = df.sort_values(by='coverage_amount', ascending=True)
        else:
            sorted_df = df.sort_values(by='final_score', ascending=False)

        result_df = sorted_df.head(top_n)
        return self._convert_to_recommendation_list(result_df)

    def recommend_accident_products(self,
                                    age: int,
                                    sex: str,
                                    top_n: int = 5,
                                    sort_by: SortOrder = SortOrder.DEFAULT
                                    ) -> List[ProductRecommendation]:
        """상해보험 상품을 추천합니다."""
        df = self.data_loader.get_base_dataframe('accident')
        print("신규 상해보험 추천 로직 실행")

        # 성별 필터링
        if sex == 'M':
            filtered_df = df[df['male_premium'].notna() & (df['male_premium'] > 0)].copy()
        else:
            filtered_df = df[df['female_premium'].notna() & (df['female_premium'] > 0)].copy()

        # 나이 필터링
        def get_age_limits(note: str):
            if not isinstance(note, str): return None, None
            match = re.search(r'(\d{1,2})[세~\- ]*(\d{1,2})', note)
            if match: return int(match.group(1)), int(match.group(2))
            return None, None

        age_limits = filtered_df['special_notes'].apply(get_age_limits)
        filtered_df['min_age'] = age_limits.apply(lambda x: x[0])
        filtered_df['max_age'] = age_limits.apply(lambda x: x[1])

        filtered_df = filtered_df[
            (filtered_df['min_age'].isna()) |
            ((filtered_df['min_age'] <= age) & (filtered_df['max_age'] >= age))
            ].copy()

        filtered_df.dropna(subset=['coverage_amount'], inplace=True)

        if filtered_df.empty:
            return []

        # 점수 계산
        df_for_scoring = filtered_df.copy()
        df_for_scoring['avg_premium'] = df_for_scoring[['male_premium', 'female_premium']].mean(axis=1)

        cov_score = self._normalize(df_for_scoring['coverage_amount'])
        value_score = 1 - self._normalize(df_for_scoring['avg_premium'])
        stability_score = df_for_scoring['renewal_cycle'].apply(lambda x: 1.0 if '비갱신' in str(x) else 0.5)

        df_for_scoring['coverage_score'] = cov_score
        df_for_scoring['value_score'] = value_score
        df_for_scoring['stability_score'] = stability_score
        df_for_scoring['final_score'] = (cov_score * 0.5 + value_score * 0.4 + stability_score * 0.1)

        # 정렬
        if sort_by == SortOrder.COVERAGE_DESC:
            sorted_df = df_for_scoring.sort_values(by='coverage_amount', ascending=False)
        elif sort_by == SortOrder.COVERAGE_ASC:
            sorted_df = df_for_scoring.sort_values(by='coverage_amount', ascending=True)
        else:
            sorted_df = df_for_scoring.sort_values(by='final_score', ascending=False)

        result_df = sorted_df.head(top_n)
        return self._convert_to_recommendation_list(result_df)