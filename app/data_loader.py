# app/data_loader.py

import pandas as pd
import numpy as np
import re
from typing import Optional, Dict
import os
import io

class DataLoader:
    """통합 보험 데이터 로더 클래스"""

    def __init__(self, data_dir: str = "products"):
        self.data_dir = data_dir
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self._load_all_data()

    def _load_all_data(self):
        """모든 보험 데이터를 로드하고 전처리합니다."""
        # 실제 파일 경로를 찾기 위한 설정
        # (로컬 환경에 맞게 경로를 설정해야 할 수 있습니다.)
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, self.data_dir)
        except NameError:
            # __file__ 변수가 없는 환경(예: Jupyter notebook)을 위한 예외 처리
            data_path = self.data_dir


        # 1. 암보험 데이터 로드 (기존 로직 유지)
        try:
            cancer_policies = pd.read_csv(os.path.join(data_path, "cancer_policies.csv"))
            cancer_coverages = pd.read_csv(os.path.join(data_path, "cancer_coverages.csv"))
            cancer_eligibility = pd.read_csv(os.path.join(data_path, "cancer_eligibility.csv"))
            cancer_rates = pd.read_csv(os.path.join(data_path, "cancer_rates.csv"))
            self.dataframes['cancer'] = self._preprocess_cancer_data(
                cancer_policies, cancer_coverages, cancer_eligibility, cancer_rates
            )
            print("성공: 암보험 데이터 로드 및 전처리 완료")
        except Exception as e:
            print(f"경고: 암보험 데이터 로드 실패 - {e}")

        # 2. 상해보험 데이터 로드 (수정된 최종 로직)
        try:
            accident_csv_path = os.path.join(data_path, "accident_products.csv")
            self.dataframes['accident'] = self._preprocess_accident_data(accident_csv_path)
            print("성공: 상해보험 데이터 로드 및 전처리 완료")
        except Exception as e:
            print(f"경고: 상해보험 데이터 로드 실패 - {e}")

    def _parse_money(self, s: str) -> Optional[int]:
        """금액 문자열에서 숫자만 추출합니다."""
        if not isinstance(s, str) or pd.isna(s): return None
        s = re.sub(r'[^0-9]', '', s)
        return int(s) if s else None

    def _preprocess_cancer_data(self, policies, coverages, eligibility, rates) -> pd.DataFrame:
        """기존 암보험 데이터 전처리 로직"""
        print("암보험 데이터 전처리 중...")
        rates['avg_premium'] = rates[['male_premium', 'female_premium']].mean(axis=1)
        merged_df = pd.merge(policies, rates, on='policy_id', how='left')
        merged_df = pd.merge(merged_df, coverages, on='policy_id', how='left')
        merged_df = pd.merge(merged_df, eligibility, on='policy_id', how='left')
        merged_df['surrender_value_num'] = merged_df['surrender_value'].apply(lambda x: 1 if x == 'standard' else 0)
        # rep_coverage 컬럼명 변경 (RecommendationEngine과의 호환성)
        merged_df.rename(columns={'rep_coverage': 'coverage_amount'}, inplace=True)
        merged_df['coverage_amount'] = pd.to_numeric(merged_df['coverage_amount'], errors='coerce')
        return merged_df

    def _preprocess_accident_data(self, csv_path: str) -> pd.DataFrame:
        """상해보험 CSV 데이터 전처리 로직 (간단하고 안정적인 방식)"""
        print("상해보험 데이터 전처리 중...")

        # 1. CSV 로드 (첫 줄을 헤더로 사용)
        df = pd.read_csv(csv_path)

        # 2. 숫자 데이터 정리 (금액, 보험료 등)
        # RecommendationEngine에서 숫자 타입으로 기대하는 컬럼들을 변환
        for col in ['male_premium', 'female_premium', 'coverage_amount']:
            if col in df.columns:
                # to_numeric으로 변환, 변환 불가 시 NaN으로 설정
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. 추천 엔진이 요구하는 기본 컬럼 추가
        # policy_id가 없다면 인덱스를 사용하여 임시 ID 부여
        if 'policy_id' not in df.columns:
            df['policy_id'] = df.index

        # surrender_value, sales_channel 컬럼이 없다면 기본값으로 생성
        for col in ['surrender_value', 'sales_channel']:
            if col not in df.columns:
                df[col] = 'N/A'

        return df

    def get_base_dataframe(self, insurance_type: str) -> pd.DataFrame:
        """지정된 종류의 전처리된 데이터프레임을 반환합니다."""
        if insurance_type not in self.dataframes or self.dataframes[insurance_type].empty:
            raise ValueError(f"'{insurance_type}' 타입의 보험 데이터가 없거나 로드에 실패했습니다.")
        return self.dataframes[insurance_type].copy()