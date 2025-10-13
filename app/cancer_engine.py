import pandas as pd
import numpy as np
import os
from typing import List
from models import ProductRecommendation

class PersonalizedCancerEngine:
    """맞춤형 암보험 추천 엔진 - 사용자 특성에 따른 강화된 개인화"""
    
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            # 절대 경로로 데이터 로드
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "data", "csv")
            file_path = os.path.join(data_path, "cancer.csv")
            
            print(f"맞춤형 엔진 데이터 파일 경로: {file_path}")
            print(f"파일 존재 여부: {os.path.exists(file_path)}")
            
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                self.df = None
                return
            
            self.df = pd.read_csv(file_path)
            print(f"맞춤형 암보험 데이터 로드 완료: {len(self.df)}개 상품")
            print(f"컬럼: {list(self.df.columns)}")
            
            # 데이터 전처리
            self._preprocess_data()
            
        except Exception as e:
            print(f"맞춤형 엔진 데이터 로드 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            self.df = None
    
    def _preprocess_data(self):
        """데이터 전처리"""
        if self.df is None or self.df.empty:
            return
        
        # coverage_amount를 정수로 변환
        def parse_coverage_amount(coverage_str):
            try:
                coverage_str = str(coverage_str).replace(',', '')
                if '만원' in coverage_str:
                    return int(float(coverage_str.replace('만원', '')) * 10000)
                elif '천원' in coverage_str:
                    return int(float(coverage_str.replace('천원', '')) * 1000)
                else:
                    return int(float(coverage_str))
            except:
                return 0
        
        self.df['coverage_amount'] = self.df['coverage_amount'].apply(parse_coverage_amount)
        
        # premium을 float로 변환
        self.df['male_premium'] = pd.to_numeric(self.df['male_premium'], errors='coerce').fillna(0)
        self.df['female_premium'] = pd.to_numeric(self.df['female_premium'], errors='coerce').fillna(0)
        self.df['avg_premium'] = (self.df['male_premium'] + self.df['female_premium']) / 2
        
        print(f"맞춤형 엔진 데이터 전처리 완료 - coverage_amount 범위: {self.df['coverage_amount'].min():,} ~ {self.df['coverage_amount'].max():,}")
        print(f"male_premium 범위: {self.df['male_premium'].min():,.0f} ~ {self.df['male_premium'].max():,.0f}")
    
    def get_recommendations(self, request) -> List[ProductRecommendation]:
        """맞춤형 암보험 상품 추천 - 강화된 개인화 로직"""
        if self.df is None or self.df.empty:
            print("맞춤형 엔진 데이터프레임이 비어있습니다.")
            return []
        
        print(f"맞춤형 엔진 전체 데이터: {len(self.df)}개")
        
        # top_n 기본값 설정
        top_n = getattr(request, 'top_n', 5)
        if top_n is None:
            top_n = 5
        
        print(f"맞춤형 엔진 요청된 추천 상품 수: {top_n}개")
        
        # 조건에 따른 필터링
        filtered_df = self._filter_products_personalized(request)
        print(f"맞춤형 엔진 필터링 후 데이터: {len(filtered_df)}개")
        
        # 강화된 개인화 점수 계산
        scored_df = self._calculate_personalized_scores(filtered_df, request)
        print(f"맞춤형 엔진 점수 계산 완료: {len(scored_df)}개")
        
        # 상위 N개 선택
        top_products = scored_df.head(top_n)
        print(f"맞춤형 엔진 최종 추천 상품: {len(top_products)}개")
        
        recommendations = []
        for i, (_, row) in enumerate(top_products.iterrows()):
            try:
                coverage_amount = row.get('coverage_amount', 0)
                avg_premium = row.get('avg_premium', 0.0)
                
                recommendation = ProductRecommendation(
                    policy_id=int(row.get('policy_id', i + 1)),
                    insurance_company=str(row.get('insurance_company', '정보없음')),
                    product_name=str(row.get('product_name', '정보없음')),
                    coverage_amount=coverage_amount,
                    male_premium=float(row.get('male_premium', 0.0)),
                    female_premium=float(row.get('female_premium', 0.0)),
                    avg_premium=avg_premium,
                    renewal_cycle=str(row.get('renewal_cycle', '정보없음')),
                    surrender_value=str(row.get('surrender_value', '정보없음')),
                    sales_channel=str(row.get('sales_channel', '정보없음')),
                    coverage_score=float(row.get('coverage_score', 0.0)),
                    value_score=float(row.get('value_score', 0.0)),
                    stability_score=float(row.get('stability_score', 0.0)),
                    final_score=float(row.get('final_score', 0.0)),
                    coverage_details=[f"암진단금 {coverage_amount:,}원", f"월 보험료 {int(avg_premium):,}원", "암입원금", "암수술금"]
                )
                recommendations.append(recommendation)
                print(f"맞춤형 추천 상품 {i+1}: {row.get('product_name', '정보없음')}")
                
            except Exception as e:
                print(f"맞춤형 ProductRecommendation 객체 생성 중 오류: {str(e)}")
                continue
        
        print(f"맞춤형 엔진 총 추천 상품 {len(recommendations)}개 생성")
        return recommendations
    
    def _filter_products_personalized(self, request):
        """맞춤형 필터링 - 사용자 특성에 따른 강화된 필터링"""
        filtered_df = self.df.copy()
        
        # 나이 기반 필터링 강화
        age = getattr(request, 'age', 30)
        if age < 25:
            # 젊은 층: 저렴한 상품 선호
            filtered_df = filtered_df[filtered_df['avg_premium'] <= 50000]
            print(f"젊은 층 필터링 (25세 미만): {len(filtered_df)}개")
        elif age >= 60:
            # 고령층: 높은 보장금액 선호
            filtered_df = filtered_df[filtered_df['coverage_amount'] >= 20000000]
            print(f"고령층 필터링 (60세 이상): {len(filtered_df)}개")
        
        # 성별 기반 필터링
        sex = getattr(request, 'sex', 'M')
        if sex == 'F':
            # 여성: 여성 특화 상품 우선
            female_products = filtered_df[
                filtered_df['product_name'].str.contains('여성|여자', na=False, case=False)
            ]
            if len(female_products) > 0:
                filtered_df = female_products
                print(f"여성 특화 상품 필터링: {len(filtered_df)}개")
        
        # 예산 기반 필터링
        monthly_budget = getattr(request, 'monthly_budget', None)
        if monthly_budget:
            if monthly_budget < 20000:
                # 저예산: 매우 저렴한 상품만
                filtered_df = filtered_df[filtered_df['avg_premium'] <= 20000]
                print(f"저예산 필터링 (2만원 미만): {len(filtered_df)}개")
            elif monthly_budget > 100000:
                # 고예산: 프리미엄 상품
                filtered_df = filtered_df[filtered_df['coverage_amount'] >= 30000000]
                print(f"고예산 필터링 (10만원 초과): {len(filtered_df)}개")
        
        # 가족 암력 기반 필터링
        family_cancer_history = getattr(request, 'family_cancer_history', False)
        if family_cancer_history:
            # 가족 암력 있음: 높은 보장금액 선호
            filtered_df = filtered_df[filtered_df['coverage_amount'] >= 25000000]
            print(f"가족 암력 기반 필터링: {len(filtered_df)}개")
        
        # 흡연 여부 기반 필터링
        smoker_flag = getattr(request, 'smoker_flag', 0)
        if smoker_flag == 1:
            # 흡연자: 높은 보장금액 선호
            filtered_df = filtered_df[filtered_df['coverage_amount'] >= 20000000]
            print(f"흡연자 필터링: {len(filtered_df)}개")
        
        # 갱신 방식 필터링
        prefer_non_renewal = getattr(request, 'prefer_non_renewal', True)
        if prefer_non_renewal:
            filtered_df = filtered_df[filtered_df['renewal_cycle'] == '비갱신형']
            print(f"비갱신형 필터링: {len(filtered_df)}개")
        else:
            filtered_df = filtered_df[filtered_df['renewal_cycle'] == '갱신형']
            print(f"갱신형 필터링: {len(filtered_df)}개")
        
        return filtered_df
    
    def _calculate_personalized_scores(self, df, request):
        """강화된 개인화 점수 계산"""
        if df.empty:
            return df
        
        # 사용자 특성에 따른 강화된 가중치
        weights = self._get_enhanced_weights(request)
        coverage_weight, value_weight, stability_weight, personalization_weight = weights
        print(f"맞춤형 가중치 - 보장금액:{coverage_weight}, 가성비:{value_weight}, 안정성:{stability_weight}, 개인화:{personalization_weight}")
        
        # 점수 계산
        df = df.copy()
        
        # 1. 보장금액 점수 (높을수록 좋음)
        max_coverage = df['coverage_amount'].max()
        df['coverage_score'] = (df['coverage_amount'] / max_coverage * 100) if max_coverage > 0 else 0
        
        # 2. 가성비 점수 (보장금액 대비 보험료 비율)
        df['value_ratio'] = df['coverage_amount'] / (df['avg_premium'] + 1)  # 0으로 나누기 방지
        max_value_ratio = df['value_ratio'].max()
        df['value_score'] = (df['value_ratio'] / max_value_ratio * 100) if max_value_ratio > 0 else 0
        
        # 3. 안정성 점수 (보험료가 낮을수록 좋음)
        min_premium = df['avg_premium'].min()
        max_premium = df['avg_premium'].max()
        if max_premium > min_premium:
            df['stability_score'] = 100 - ((df['avg_premium'] - min_premium) / (max_premium - min_premium) * 100)
        else:
            df['stability_score'] = 100
        
        # 4. 개인화 점수 (새로운 요소)
        df['personalization_score'] = self._calculate_personalization_score(df, request)
        
        # 최종 점수 계산 (개인화 요소 추가)
        df['final_score'] = (
            df['coverage_score'] * coverage_weight / 100 +
            df['value_score'] * value_weight / 100 +
            df['stability_score'] * stability_weight / 100 +
            df['personalization_score'] * personalization_weight / 100
        )
        
        # 다양성을 위한 추가 점수
        import random
        random.seed(42)
        
        # 회사별 다양성 점수
        df['diversity_bonus'] = 0
        companies = df['insurance_company'].unique()
        for i, company in enumerate(companies):
            company_mask = df['insurance_company'] == company
            df.loc[company_mask, 'diversity_bonus'] = (len(companies) - i) * 2
        
        # 랜덤 요소 추가 (맞춤형에서는 더 적게)
        df['random_bonus'] = [random.uniform(0, 5) for _ in range(len(df))]
        
        # 최종 점수에 다양성 요소 추가
        df['final_score'] = df['final_score'] + df['diversity_bonus'] + df['random_bonus']
        
        # 점수 순으로 정렬
        df = df.sort_values('final_score', ascending=False)
        
        print(f"맞춤형 엔진 점수 계산 완료 - 최고점: {df['final_score'].max():.1f}, 최저점: {df['final_score'].min():.1f}")
        
        return df
    
    def _get_enhanced_weights(self, request):
        """강화된 개인화 가중치 계산"""
        # 기본 가중치
        coverage_weight = 25.0
        value_weight = 35.0
        stability_weight = 25.0
        personalization_weight = 15.0  # 새로운 개인화 가중치
        
        # 나이에 따른 조정
        age = getattr(request, 'age', 30)
        if age < 25:
            # 매우 젊은 층: 가성비와 개인화 중시
            coverage_weight = 20.0
            value_weight = 40.0
            stability_weight = 20.0
            personalization_weight = 20.0
        elif age >= 60:
            # 고령층: 보장금액과 안정성 중시
            coverage_weight = 40.0
            value_weight = 20.0
            stability_weight = 30.0
            personalization_weight = 10.0
        
        # 성별에 따른 조정
        sex = getattr(request, 'sex', 'M')
        if sex == 'F':
            # 여성: 안정성과 개인화 중시
            stability_weight += 10.0
            personalization_weight += 5.0
            value_weight -= 15.0
        
        # 예산에 따른 조정
        monthly_budget = getattr(request, 'monthly_budget', None)
        if monthly_budget:
            if monthly_budget < 20000:
                # 저예산: 가성비와 안정성 중시
                value_weight += 20.0
                stability_weight += 10.0
                coverage_weight -= 20.0
                personalization_weight -= 10.0
            elif monthly_budget > 100000:
                # 고예산: 보장금액과 개인화 중시
                coverage_weight += 20.0
                personalization_weight += 10.0
                value_weight -= 20.0
                stability_weight -= 10.0
        
        # 가족 암력에 따른 조정
        family_cancer_history = getattr(request, 'family_cancer_history', False)
        if family_cancer_history:
            # 가족 암력 있음: 보장금액과 개인화 중시
            coverage_weight += 15.0
            personalization_weight += 10.0
            value_weight -= 15.0
            stability_weight -= 10.0
        
        # 흡연 여부에 따른 조정
        smoker_flag = getattr(request, 'smoker_flag', 0)
        if smoker_flag == 1:
            # 흡연자: 보장금액과 안정성 중시
            coverage_weight += 15.0
            stability_weight += 10.0
            value_weight -= 15.0
            personalization_weight -= 10.0
        
        # 가중치 정규화 (합이 100이 되도록)
        total = coverage_weight + value_weight + stability_weight + personalization_weight
        coverage_weight = (coverage_weight / total) * 100
        value_weight = (value_weight / total) * 100
        stability_weight = (stability_weight / total) * 100
        personalization_weight = (personalization_weight / total) * 100
        
        return [coverage_weight, value_weight, stability_weight, personalization_weight]
    
    def _calculate_personalization_score(self, df, request):
        """개인화 점수 계산"""
        personalization_scores = []
        
        for _, row in df.iterrows():
            score = 0
            
            # 나이 기반 개인화
            age = getattr(request, 'age', 30)
            if age < 30:
                # 젊은 층: 저렴한 상품에 높은 점수
                if row['avg_premium'] < 30000:
                    score += 20
                elif row['avg_premium'] < 50000:
                    score += 10
            elif age >= 50:
                # 중장년층: 높은 보장금액에 높은 점수
                if row['coverage_amount'] > 30000000:
                    score += 20
                elif row['coverage_amount'] > 20000000:
                    score += 10
            
            # 성별 기반 개인화
            sex = getattr(request, 'sex', 'M')
            if sex == 'F':
                # 여성: 여성 특화 상품에 높은 점수
                if '여성' in str(row['product_name']) or '여자' in str(row['product_name']):
                    score += 25
                # 여성: 안정적인 보험회사에 높은 점수
                if row['insurance_company'] in ['한화생명', '교보생명', '삼성생명']:
                    score += 15
            
            # 예산 기반 개인화
            monthly_budget = getattr(request, 'monthly_budget', None)
            if monthly_budget:
                if monthly_budget < 30000:
                    # 저예산: 저렴한 상품에 높은 점수
                    if row['avg_premium'] <= monthly_budget:
                        score += 30
                    elif row['avg_premium'] <= monthly_budget * 1.5:
                        score += 15
                elif monthly_budget > 80000:
                    # 고예산: 프리미엄 상품에 높은 점수
                    if row['coverage_amount'] > 40000000:
                        score += 30
                    elif row['coverage_amount'] > 30000000:
                        score += 15
            
            # 가족 암력 기반 개인화
            family_cancer_history = getattr(request, 'family_cancer_history', False)
            if family_cancer_history:
                # 가족 암력 있음: 높은 보장금액에 높은 점수
                if row['coverage_amount'] > 35000000:
                    score += 25
                elif row['coverage_amount'] > 25000000:
                    score += 15
            
            # 흡연 여부 기반 개인화
            smoker_flag = getattr(request, 'smoker_flag', 0)
            if smoker_flag == 1:
                # 흡연자: 높은 보장금액에 높은 점수
                if row['coverage_amount'] > 30000000:
                    score += 20
                elif row['coverage_amount'] > 20000000:
                    score += 10
            
            personalization_scores.append(min(score, 100))  # 최대 100점으로 제한
        
        return personalization_scores
