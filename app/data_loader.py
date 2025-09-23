import pandas as pd
import numpy as np
import re
from typing import Optional
import os

class DataLoader:
    """암보험 데이터 로더 클래스"""
    
    def __init__(self, data_dir: str = "products"):
        self.data_dir = data_dir
        self.coverages = None
        self.eligibility = None
        self.policies = None
        self.rates = None
        self.base_df = None
        self._load_data()
    
    def _load_data(self):
        """CSV 파일들을 로드하고 전처리"""
        try:
            # 데이터 파일 경로 설정
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, self.data_dir)
            
            # CSV 파일 로드
            self.coverages = pd.read_csv(os.path.join(data_path, "cancer_coverages.csv"))
            self.eligibility = pd.read_csv(os.path.join(data_path, "cancer_eligibility.csv"))
            self.policies = pd.read_csv(os.path.join(data_path, "cancer_policies.csv"))
            self.rates = pd.read_csv(os.path.join(data_path, "cancer_rates.csv"))
            
            # 데이터 전처리
            self._preprocess_data()
            
        except Exception as e:
            raise Exception(f"데이터 로드 실패: {str(e)}")
    
    def _parse_money(self, s: str) -> float:
        """금액 문자열을 숫자로 변환"""
        if pd.isna(s):
            return np.nan
        s = str(s).strip()
        
        # 괄호 안의 내용 제거 (예: "1,000만원 (단, [여성형]은 500만원)")
        if '(' in s:
            s = s.split('(')[0].strip()
        
        ten_thousand_unit = '만' in s  # e.g., "3,000만원"
        digits = re.sub(r'[^\d]', '', s)
        if digits == '':
            return np.nan
        val = int(digits)
        return val * 10000 if ten_thousand_unit else val
    
    def _normalize(self, series: pd.Series) -> pd.Series:
        """시리즈를 0-1 범위로 정규화"""
        s = pd.to_numeric(series, errors='coerce')
        mn = s.min()
        mx = s.max()
        if pd.isna(mn) or pd.isna(mx) or mx == mn:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)
    
    def _preprocess_data(self):
        """데이터 전처리 수행"""
        # policies 데이터 전처리
        self.policies = self.policies.copy()
        self.policies['coverage_amount_num'] = self.policies['coverage_amount'].apply(self._parse_money)
        self.policies['surrender_value_num'] = self.policies['surrender_value'].apply(self._parse_money)
        
        # 대표 보장금액 계산
        rep_cov = self.policies.set_index('policy_id')['coverage_amount_num']
        
        # 기본 병합 데이터프레임 생성
        self.base_df = self.policies.merge(
            rep_cov.rename('rep_coverage'), 
            left_on='policy_id', 
            right_index=True, 
            how='left'
        ).merge(
            self.eligibility, 
            on='policy_id', 
            how='left'
        ).merge(
            self.rates, 
            on='policy_id', 
            how='left'
        )
        
        # 숫자형 컬럼 변환
        for col in ['rep_coverage', 'min_coverage', 'max_coverage', 'male_premium', 'female_premium']:
            self.base_df[col] = pd.to_numeric(self.base_df[col], errors='coerce')
        
        # 갱신형 선호도 점수 계산
        self.base_df['renewal_pref'] = self.base_df['renewal_cycle'].map({
            '비갱신형': 1.0, 
            '갱신형': 0.0
        }).fillna(0.5)
        
        # 해약환급금 숫자 변환
        self.base_df['sv_num'] = pd.to_numeric(self.base_df['surrender_value_num'], errors='coerce')
    
    def get_base_dataframe(self) -> pd.DataFrame:
        """전처리된 기본 데이터프레임 반환"""
        return self.base_df.copy()
    
    def is_data_loaded(self) -> bool:
        """데이터가 로드되었는지 확인"""
        return self.base_df is not None and not self.base_df.empty
    
    @property
    def products(self):
        """상품 데이터를 딕셔너리 리스트로 반환"""
        if self.base_df is None:
            return []
        
        products = []
        for _, row in self.base_df.iterrows():
            product = {
                'policy_id': row.get('policy_id'),
                'insurance_company': row.get('insurance_company'),
                'product_name': row.get('product_name'),
                'coverage_amount': row.get('coverage_amount_num'),
                'male_premium': row.get('male_premium'),
                'female_premium': row.get('female_premium'),
                'avg_premium': (row.get('male_premium', 0) + row.get('female_premium', 0)) / 2 if pd.notna(row.get('male_premium')) and pd.notna(row.get('female_premium')) else None,
                'renewal_cycle': row.get('renewal_cycle'),
                'surrender_value': str(row.get('surrender_value_num')) if pd.notna(row.get('surrender_value_num')) else "0",
                'sales_channel': row.get('sales_channel'),
                'coverage_score': 0.0,  # 기본값
                'value_score': 0.0,     # 기본값
                'stability_score': 0.0  # 기본값
            }
            products.append(product)
        
        return products