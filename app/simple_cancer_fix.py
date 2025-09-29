import pandas as pd
import os
from typing import List
from models import ProductRecommendation

class SimpleCancerFix:
    """간단한 암보험 추천 엔진 (완전 재작성)"""
    
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            # 절대 경로로 데이터 로드
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "products")
            file_path = os.path.join(data_path, "cancer_policies.csv")
            
            print(f"데이터 파일 경로: {file_path}")
            print(f"파일 존재 여부: {os.path.exists(file_path)}")
            
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                self.df = None
                return
            
            self.df = pd.read_csv(file_path)
            print(f"암보험 데이터 로드 완료: {len(self.df)}개 상품")
            print(f"컬럼: {list(self.df.columns)}")
            
            # 데이터 전처리
            self._preprocess_data()
            
        except Exception as e:
            print(f"데이터 로드 중 오류: {str(e)}")
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
        
        print(f"데이터 전처리 완료 - coverage_amount 범위: {self.df['coverage_amount'].min():,} ~ {self.df['coverage_amount'].max():,}")
        print(f"male_premium 범위: {self.df['male_premium'].min():,.0f} ~ {self.df['male_premium'].max():,.0f}")
    
    def get_recommendations(self, request) -> List[ProductRecommendation]:
        """암보험 상품 추천 - 조건에 따른 필터링 및 점수 계산"""
        if self.df is None or self.df.empty:
            print("데이터프레임이 비어있습니다.")
            return []
        
        print(f"전체 데이터: {len(self.df)}개")
        
        # top_n 기본값 설정
        top_n = getattr(request, 'top_n', 5)
        if top_n is None:
            top_n = 5
        
        print(f"요청된 추천 상품 수: {top_n}개")
        
        # 조건에 따른 필터링
        filtered_df = self._filter_products(request)
        print(f"필터링 후 데이터: {len(filtered_df)}개")
        
        # 점수 계산 및 정렬
        scored_df = self._calculate_scores(filtered_df, request)
        print(f"점수 계산 완료: {len(scored_df)}개")
        
        # 상위 N개 선택
        top_products = scored_df.head(top_n)
        print(f"최종 추천 상품: {len(top_products)}개")
        
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
                print(f"추천 상품 {i+1}: {row.get('product_name', '정보없음')}")
                
            except Exception as e:
                print(f"ProductRecommendation 객체 생성 중 오류: {str(e)}")
                continue
        
        print(f"총 추천 상품 {len(recommendations)}개 생성")
        return recommendations
    
    def _filter_products(self, request):
        """조건에 따른 상품 필터링"""
        filtered_df = self.df.copy()
        
        # 최소 보장금액 필터링
        if hasattr(request, 'min_coverage') and request.min_coverage:
            min_coverage = int(request.min_coverage)
            filtered_df = filtered_df[filtered_df['coverage_amount'] >= min_coverage]
            print(f"최소 보장금액 {min_coverage:,}원 필터링 후: {len(filtered_df)}개")
        
        # 최대 보험료 필터링
        if hasattr(request, 'max_premium_avg') and request.max_premium_avg:
            max_premium = float(request.max_premium_avg)
            filtered_df = filtered_df[filtered_df['avg_premium'] <= max_premium]
            print(f"최대 보험료 {max_premium:,.0f}원 필터링 후: {len(filtered_df)}개")
        
        # 갱신 유형 필터링 (더 엄격한 디버깅)
        print(f"=== 갱신 방식 필터링 디버깅 ===")
        print(f"prefer_non_renewal 값: {getattr(request, 'prefer_non_renewal', 'None')}")
        
        if hasattr(request, 'prefer_non_renewal'):
            print(f"갱신 방식 필터링 전: {len(filtered_df)}개")
            print(f"갱신 방식 분포: {filtered_df['renewal_cycle'].value_counts().to_dict()}")
            
            if request.prefer_non_renewal:
                # 비갱신형 필터링 (비갱신형만)
                print("비갱신형 상품만 필터링 중...")
                non_renewal_mask = filtered_df['renewal_cycle'] == '비갱신형'
                filtered_df = filtered_df[non_renewal_mask]
                print(f"비갱신형 필터링 후: {len(filtered_df)}개")
            else:
                # 갱신형 필터링 (갱신형만)
                print("갱신형 상품만 필터링 중...")
                print(f"갱신형 데이터 확인: {(filtered_df['renewal_cycle'] == '갱신형').sum()}개")
                renewal_mask = filtered_df['renewal_cycle'] == '갱신형'
                filtered_df = filtered_df[renewal_mask]
                print(f"갱신형 필터링 후: {len(filtered_df)}개")
                
                if len(filtered_df) == 0:
                    print("⚠️ 갱신형 상품이 0개입니다! 실제 데이터 확인:")
                    print(f"전체 데이터 갱신형: {(self.df['renewal_cycle'] == '갱신형').sum()}개")
        else:
            print("prefer_non_renewal 속성이 없습니다 - 갱신 필터링 건너뜀")
        
        print(f"=== 갱신 방식 필터링 완료 ===")
        
        # 판매채널 필터링
        if hasattr(request, 'require_sales_channel') and request.require_sales_channel:
            sales_channel = str(request.require_sales_channel).strip()
            if sales_channel:
                filtered_df = filtered_df[
                    filtered_df['sales_channel'].str.contains(sales_channel, na=False)
                ]
                print(f"판매채널 '{sales_channel}' 필터링 후: {len(filtered_df)}개")
        
        return filtered_df
    
    def _calculate_scores(self, df, request):
        """상품 점수 계산 및 정렬"""
        if df.empty:
            return df
        
        # 가중치 설정
        weights = [70.0, 20.0, 10.0]  # 기본값
        if hasattr(request, 'weights') and request.weights:
            weights = list(request.weights)
        
        coverage_weight, value_weight, stability_weight = weights
        print(f"가중치 - 보장금액:{coverage_weight}, 가성비:{value_weight}, 안정성:{stability_weight}")
        
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
        
        # 최종 점수 계산
        df['final_score'] = (
            df['coverage_score'] * coverage_weight / 100 +
            df['value_score'] * value_weight / 100 +
            df['stability_score'] * stability_weight / 100
        )
        
        # 다양성을 위한 추가 점수
        import random
        random.seed(42)
        
        # 회사별 다양성 점수
        df['diversity_bonus'] = 0
        companies = df['insurance_company'].unique()
        for i, company in enumerate(companies):
            company_mask = df['insurance_company'] == company
            df.loc[company_mask, 'diversity_bonus'] = (len(companies) - i) * 3
        
        # 랜덤 요소 추가
        df['random_bonus'] = [random.uniform(0, 10) for _ in range(len(df))]
        
        # 갱신 방식 보너스
        df['renewal_bonus'] = 0
        if hasattr(request, 'prefer_non_renewal') and request.prefer_non_renewal:
            non_renewal_mask = df['renewal_cycle'].str.contains('비갱신|무갱신', na=False)
            df.loc[non_renewal_mask, 'renewal_bonus'] = 15
        
        # 최종 점수에 다양성 요소 추가
        df['final_score'] = df['final_score'] + df['diversity_bonus'] + df['random_bonus'] + df['renewal_bonus']
        
        # 점수 순으로 정렬
        df = df.sort_values('final_score', ascending=False)
        
        print(f"점수 계산 완료 - 최고점: {df['final_score'].max():.1f}, 최저점: {df['final_score'].min():.1f}")
        
        return df