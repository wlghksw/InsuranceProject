import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from .data_loader import DataLoader
from .models import ProductRecommendation, SavingsRecommendationRequest, SavingsProductRecommendation, UserProfileRecommendationRequest

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
        sex: Optional[str] = None,
        monthly_budget: Optional[int] = None,
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
        
        # 성별 필터링
        if sex:
            if sex == 'M':
                # 남성인데 남성 보험료가 0이면 제외 (여성 전용 상품)
                df = df[df['male_premium'] > 0]
            else:
                # 여성인데 여성 보험료가 0이면 제외 (남성 전용 상품)
                df = df[df['female_premium'] > 0]
        
        # 예산 필터링
        if monthly_budget and sex:
            if sex == 'M':
                # 남성 보험료 기준으로 예산 필터링 (10% 여유분 허용)
                df = df[(df['male_premium'].isna()) | (df['male_premium'] <= monthly_budget * 1.1)]
            else:
                # 여성 보험료 기준으로 예산 필터링 (10% 여유분 허용)
                df = df[(df['female_premium'].isna()) | (df['female_premium'] <= monthly_budget * 1.1)]
        
        # 갱신형 선호도 필터링
        if prefer_non_renewal:
            # 비갱신형 선호 시 갱신형 상품 제외
            df = df[df['renewal_cycle'] != '갱신형']
        else:
            # 갱신형 선호 시 비갱신형 상품 제외
            df = df[df['renewal_cycle'] == '갱신형']
        
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

    def get_savings_recommendations(self, request: SavingsRecommendationRequest) -> List[SavingsProductRecommendation]:
        """저축성보험 상품 추천 (실제 CSV 데이터 기반)"""
        try:
            import os
            import pandas as pd
            import numpy as np
            
            # Product 폴더의 실제 저축성보험 CSV 파일 읽기
            product_dir = os.path.join(os.path.dirname(__file__), '..', 'Product')
            csv_file = os.path.join(product_dir, '저축성_상품비교_20250925120454025.csv')
            
            if not os.path.exists(csv_file):
                # 기본 저축성보험 상품 데이터 생성
                return self._generate_default_savings_recommendations(request)
            
            # CSV 파일 읽기 (헤더가 여러 줄이므로 적절히 처리)
            df = pd.read_csv(csv_file, encoding='utf-8', skiprows=2)  # 헤더 2줄 건너뛰기
            
            # 컬럼명 정리
            df.columns = ['company', 'product_name', 'term', 'premium', 'male_accumulation', 'male_rate', 'male_surrender', 
                        'female_accumulation', 'female_rate', 'female_surrender', 'guaranteed_rate', 'current_rate', 
                        'avg_rate', 'fixed_rate', 'business_rate', 'risk_coverage', 'fixed_rate_type', 'linked_rate_type', 
                        'linked_rate_type2', 'join_type', 'universal', 'payment_method', 'sales_channel', 'sales_date', 
                        'special_notes', 'phone']
            
            # 전체 데이터에서 벤치마크 계산
            benchmark_stats = self._calculate_benchmark_stats(df)
            
            # 필터링 조건에 맞는 상품 찾기
            filtered_products = []
            
            for _, row in df.iterrows():
                # 보험기간 확인 (더 유연한 매칭)
                product_term = str(row['term']).replace('년', '').strip()
                if product_term and product_term != 'nan':
                    try:
                        term_value = int(product_term)
                        # 요청한 기간과 정확히 일치하거나 ±5년 범위 내에서 허용
                        if abs(term_value - request.preferred_term) > 5:
                            continue
                    except:
                        # 숫자로 변환할 수 없으면 문자열로 확인
                        if str(request.preferred_term) not in product_term:
                            continue
                
                # 월 보험료 확인 (예산 범위 내)
                try:
                    premium_str = str(row['premium']).replace(',', '').replace('원', '').replace(' ', '')
                    if '만원' in premium_str:
                        premium_value = float(premium_str.replace('만원', '')) * 10000
                    else:
                        premium_value = float(premium_str)
                    
                    # 예산의 10배 범위 내에서 허용 (월납 -> 연납 변환 고려)
                    if premium_value > request.monthly_budget * 12 * 10:
                        continue
                except:
                    pass
                
                # 점수 계산 및 벤치마크 분석
                score_breakdown = self._calculate_detailed_score(row, request, benchmark_stats)
                
                filtered_products.append({
                    'row': row,
                    'score_breakdown': score_breakdown
                })
            
            # 점수순으로 정렬하고 상위 N개 선택
            filtered_products.sort(key=lambda x: x['score_breakdown']['total_score'], reverse=True)
            selected_products = filtered_products[:request.top_n]
            
            recommendations = []
            for i, product_data in enumerate(selected_products):
                row = product_data['row']
                score_data = product_data['score_breakdown']
                
                # 돈 단위 시나리오 계산
                money_scenario = self._calculate_money_scenario(row, request)
                
                # 의사결정 배지 생성
                decision_badges = self._generate_decision_badges(score_data, benchmark_stats)
                
                # 맞춤형 인사이트 생성
                custom_insight = self._generate_custom_insight(row, request, score_data)
                
                recommendation = SavingsProductRecommendation(
                    product_id=f"savings_{i+1:03d}",
                    company=str(row['company']),
                    product_name=str(row['product_name']),
                    product_type='저축성보험',
                    score=float(score_data['total_score']),
                    guaranteed_rate=str(row['guaranteed_rate']),
                    current_rate=str(row['current_rate']),
                    pay_period=f"{request.preferred_term}년",
                    term=f"{request.preferred_term}년",
                    monthly_premium_estimate=f"{request.monthly_budget:,}원",
                    annual_savings=f"{request.monthly_budget * 12:,}원",
                    surrender_5y=str(row['male_rate']),
                    surrender_10y=str(row['female_rate']),
                    extra_contribution='가능' if '유니버셜' in str(row['universal']) else '불가능',
                    partial_withdrawal='가능' if '유니버셜' in str(row['universal']) else '불가능',
                    premium_holiday='가능' if '유니버셜' in str(row['universal']) else '불가능',
                    tax_benefit='세액공제',
                    replacement_reason=f"월 {request.monthly_budget:,}원 예산으로 {request.monthly_budget * 12:,}원 연간 저축"
                )
                
                # 추가 분석 데이터를 replacement_reason에 포함
                analysis_summary = f"{money_scenario} | {decision_badges} | {custom_insight}"
                recommendation.replacement_reason = analysis_summary
                
                recommendations.append(recommendation)
            
            if recommendations:
                return recommendations
            
            # 조건에 맞는 상품이 없으면 기본 추천
            return self._generate_default_savings_recommendations(request)
            
        except Exception as e:
            print(f"저축성보험 추천 중 오류: {str(e)}")
            return self._generate_default_savings_recommendations(request)
    
    def _calculate_product_score(self, row, request: SavingsRecommendationRequest) -> float:
        """상품 점수 계산 (간단한 우선순위 기반)"""
        score = 0.0
        
        try:
            # 보증이율 기준 (높을수록 좋음)
            guaranteed_rate_str = str(row['guaranteed_rate']).replace('%', '').replace('-', '0')
            if guaranteed_rate_str and guaranteed_rate_str != 'nan':
                guaranteed_rate = float(guaranteed_rate_str)
                if guaranteed_rate >= request.min_guaranteed_rate * 100:
                    score += guaranteed_rate * 10  # 보증이율이 높을수록 높은 점수
            
            # 현재이율 기준
            current_rate_str = str(row['current_rate']).replace('%', '').replace('-', '0')
            if current_rate_str and current_rate_str != 'nan':
                current_rate = float(current_rate_str)
                score += current_rate * 5  # 현재이율이 높을수록 높은 점수
            
            # 환급률 기준
            male_rate_str = str(row['male_rate']).replace('%', '').replace('-', '0')
            if male_rate_str and male_rate_str != 'nan':
                male_rate = float(male_rate_str)
                if male_rate >= request.min_refund_10y * 100:
                    score += male_rate * 0.5  # 환급률이 높을수록 높은 점수
            
            # 유니버셜 상품 우선순위
            if '유니버셜' in str(row['universal']):
                score += 20  # 유니버셜 상품에 가중치
            
            # 유연성 요구사항 만족도
            if request.need_extra_contribution and '유니버셜' in str(row['universal']):
                score += 10
            if request.need_partial_withdrawal and '유니버셜' in str(row['universal']):
                score += 10
            if request.need_premium_holiday and '유니버셜' in str(row['universal']):
                score += 10
                
        except:
            pass
        
        return score
    
    def _calculate_benchmark_stats(self, df):
        """전체 데이터에서 벤치마크 통계 계산"""
        stats = {}
        
        # 보증이율 통계
        guaranteed_rates = []
        for _, row in df.iterrows():
            try:
                rate_str = str(row['guaranteed_rate']).replace('%', '').replace('-', '0')
                if rate_str and rate_str != 'nan':
                    guaranteed_rates.append(float(rate_str))
            except:
                pass
        
        if guaranteed_rates:
            stats['guaranteed_rate'] = {
                'mean': np.mean(guaranteed_rates),
                'percentiles': {
                    20: np.percentile(guaranteed_rates, 20),
                    50: np.percentile(guaranteed_rates, 50),
                    80: np.percentile(guaranteed_rates, 80)
                }
            }
        
        # 현재이율 통계
        current_rates = []
        for _, row in df.iterrows():
            try:
                rate_str = str(row['current_rate']).replace('%', '').replace('-', '0')
                if rate_str and rate_str != 'nan':
                    current_rates.append(float(rate_str))
            except:
                pass
        
        if current_rates:
            stats['current_rate'] = {
                'mean': np.mean(current_rates),
                'percentiles': {
                    20: np.percentile(current_rates, 20),
                    50: np.percentile(current_rates, 50),
                    80: np.percentile(current_rates, 80)
                }
            }
        
        # 환급률 통계 (male_rate 사용)
        refund_rates = []
        for _, row in df.iterrows():
            try:
                rate_str = str(row['male_rate']).replace('%', '').replace('-', '0')
                if rate_str and rate_str != 'nan':
                    refund_rates.append(float(rate_str))
            except:
                pass
        
        if refund_rates:
            stats['refund_rate'] = {
                'mean': np.mean(refund_rates),
                'percentiles': {
                    20: np.percentile(refund_rates, 20),
                    50: np.percentile(refund_rates, 50),
                    80: np.percentile(refund_rates, 80)
                }
            }
        
        return stats
    
    def _calculate_detailed_score(self, row, request, benchmark_stats):
        """상세 점수 계산 및 벤치마크 분석"""
        score_breakdown = {
            'return_score': 0,
            'refund_score': 0,
            'tax_score': 0,
            'flex_score': 0,
            'total_score': 0,
            'benchmark_analysis': {}
        }
        
        try:
            # 수익성 점수 (보증이율 + 현재이율)
            guaranteed_rate_str = str(row['guaranteed_rate']).replace('%', '').replace('-', '0')
            current_rate_str = str(row['current_rate']).replace('%', '').replace('-', '0')
            
            if guaranteed_rate_str and guaranteed_rate_str != 'nan':
                guaranteed_rate = float(guaranteed_rate_str)
                score_breakdown['return_score'] += guaranteed_rate * 10
                
                # 벤치마크 분석
                if 'guaranteed_rate' in benchmark_stats:
                    percentile = self._get_percentile(guaranteed_rate, benchmark_stats['guaranteed_rate']['percentiles'])
                    diff_vs_mean = guaranteed_rate - benchmark_stats['guaranteed_rate']['mean']
                    score_breakdown['benchmark_analysis']['guaranteed_rate'] = {
                        'value': guaranteed_rate,
                        'percentile': percentile,
                        'diff_vs_mean': diff_vs_mean
                    }
            
            if current_rate_str and current_rate_str != 'nan':
                current_rate = float(current_rate_str)
                score_breakdown['return_score'] += current_rate * 5
                
                # 벤치마크 분석
                if 'current_rate' in benchmark_stats:
                    percentile = self._get_percentile(current_rate, benchmark_stats['current_rate']['percentiles'])
                    diff_vs_mean = current_rate - benchmark_stats['current_rate']['mean']
                    score_breakdown['benchmark_analysis']['current_rate'] = {
                        'value': current_rate,
                        'percentile': percentile,
                        'diff_vs_mean': diff_vs_mean
                    }
            
            # 환급률 점수
            male_rate_str = str(row['male_rate']).replace('%', '').replace('-', '0')
            if male_rate_str and male_rate_str != 'nan':
                male_rate = float(male_rate_str)
                if male_rate >= request.min_refund_10y * 100:
                    score_breakdown['refund_score'] = male_rate * 0.5
                    
                    # 벤치마크 분석
                    if 'refund_rate' in benchmark_stats:
                        percentile = self._get_percentile(male_rate, benchmark_stats['refund_rate']['percentiles'])
                        diff_vs_mean = male_rate - benchmark_stats['refund_rate']['mean']
                        score_breakdown['benchmark_analysis']['refund_rate'] = {
                            'value': male_rate,
                            'percentile': percentile,
                            'diff_vs_mean': diff_vs_mean
                        }
            
            # 유연성 점수
            if '유니버셜' in str(row['universal']):
                score_breakdown['flex_score'] = 20
                if request.need_extra_contribution:
                    score_breakdown['flex_score'] += 10
                if request.need_partial_withdrawal:
                    score_breakdown['flex_score'] += 10
                if request.need_premium_holiday:
                    score_breakdown['flex_score'] += 10
            
            # 세제 점수 (기본값)
            score_breakdown['tax_score'] = 15  # 세액공제 기본 점수
            
            # 총점 계산
            score_breakdown['total_score'] = (
                score_breakdown['return_score'] * request.weights.get('return', 0.3) +
                score_breakdown['refund_score'] * request.weights.get('refund', 0.3) +
                score_breakdown['tax_score'] * request.weights.get('tax', 0.2) +
                score_breakdown['flex_score'] * request.weights.get('flex', 0.2)
            )
            
        except Exception as e:
            print(f"점수 계산 중 오류: {str(e)}")
        
        return score_breakdown
    
    def _get_percentile(self, value, percentiles):
        """값의 백분위수 계산"""
        if value <= percentiles[20]:
            return 20
        elif value <= percentiles[50]:
            return 50
        elif value <= percentiles[80]:
            return 80
        else:
            return 90
    
    def _calculate_money_scenario(self, row, request):
        """돈 단위 시나리오 계산"""
        try:
            # 총 납입액 계산
            total_payment = request.monthly_budget * 12 * min(request.preferred_term, 10)
            
            # 환급률 계산 (10년 기준)
            refund_rate_str = str(row['male_rate']).replace('%', '').replace('-', '0')
            if refund_rate_str and refund_rate_str != 'nan':
                refund_rate = float(refund_rate_str) / 100
            else:
                # 10년 환급률이 없으면 5년, 15년, 20년 평균 사용
                rates = []
                for col in ['male_rate', 'female_rate']:
                    try:
                        rate_str = str(row[col]).replace('%', '').replace('-', '0')
                        if rate_str and rate_str != 'nan':
                            rates.append(float(rate_str) / 100)
                    except:
                        pass
                refund_rate = np.mean(rates) if rates else 0.9
            
            # 예상 환급금 계산
            expected_refund = total_payment * refund_rate
            profit_loss = expected_refund - total_payment
            profit_loss_rate = (profit_loss / total_payment) * 100
            
            return f"10년 총납입 {total_payment:,}원 → 예상환급금 {expected_refund:,.0f}원({profit_loss_rate:+.1f}%)"
            
        except Exception as e:
            print(f"돈 단위 시나리오 계산 중 오류: {str(e)}")
            return "시나리오 계산 불가"
    
    def _generate_decision_badges(self, score_data, benchmark_stats):
        """의사결정 배지 생성"""
        badges = []
        
        # 수익성 배지
        return_score = score_data['return_score']
        if return_score >= 50:
            badges.append("수익성: 높음")
        elif return_score >= 30:
            badges.append("수익성: 보통")
        else:
            badges.append("수익성: 낮음")
        
        # 안정성(환급) 배지
        refund_score = score_data['refund_score']
        if refund_score >= 40:
            badges.append("안정성: 높음")
        elif refund_score >= 25:
            badges.append("안정성: 보통")
        else:
            badges.append("안정성: 낮음")
        
        # 유연성 배지
        flex_score = score_data['flex_score']
        if flex_score >= 30:
            badges.append("유연성: 높음")
        elif flex_score >= 15:
            badges.append("유연성: 보통")
        else:
            badges.append("유연성: 낮음")
        
        # 세제 배지
        tax_score = score_data['tax_score']
        if tax_score >= 20:
            badges.append("세제: 높음")
        elif tax_score >= 10:
            badges.append("세제: 보통")
        else:
            badges.append("세제: 낮음")
        
        return " / ".join(badges)
    
    def _generate_custom_insight(self, row, request, score_data):
        """맞춤형 인사이트 생성"""
        insights = []
        
        # 유연성 관련
        if '유니버셜' in str(row['universal']):
            if request.need_extra_contribution or request.need_partial_withdrawal or request.need_premium_holiday:
                insights.append("추가납입·부분인출 가능 → 유동성 선호 고객에게 적합")
        
        # 보증이율 관련
        try:
            guaranteed_rate_str = str(row['guaranteed_rate']).replace('%', '').replace('-', '0')
            if guaranteed_rate_str and guaranteed_rate_str != 'nan':
                guaranteed_rate = float(guaranteed_rate_str)
                if guaranteed_rate < 2.0:
                    insights.append("최저보증이율 낮음 → 금리 하락기에 수익성 하방 위험")
                elif guaranteed_rate > 3.0:
                    insights.append("높은 보증이율 → 안정적인 수익 보장")
        except:
            pass
        
        # 환급률 관련
        try:
            refund_rate_str = str(row['male_rate']).replace('%', '').replace('-', '0')
            if refund_rate_str and refund_rate_str != 'nan':
                refund_rate = float(refund_rate_str)
                if refund_rate < 90:
                    insights.append("낮은 환급률 → 중도해지 시 손실 위험")
                elif refund_rate > 95:
                    insights.append("높은 환급률 → 안전한 자금 회수")
        except:
            pass
        
        return insights[0] if insights else "표준 저축성보험 상품"
    
    def _matches_requirements(self, product: dict, request: SavingsRecommendationRequest) -> bool:
        """상품이 요구사항에 맞는지 확인"""
        try:
            # 보험기간 확인 (문자열에서 숫자 추출)
            product_term = product.get('term', '')
            if product_term and str(request.preferred_term) not in product_term:
                return False
            
            # 유연성 요구사항 확인
            if request.need_extra_contribution and product.get('extra_contribution', '') != '가능':
                return False
            if request.need_partial_withdrawal and product.get('partial_withdrawal', '') != '가능':
                return False
            if request.need_premium_holiday and product.get('premium_holiday', '') != '가능':
                return False
            
            return True
        except:
            return True  # 오류 시 통과

    def _generate_default_savings_recommendations(self, request: SavingsRecommendationRequest) -> List[SavingsProductRecommendation]:
        """기본 저축성보험 추천 상품 생성"""
        default_products = [
            {
                'company': '신한라이프',
                'product_name': '더좋은저축보험01',
                'current_rate': '3.70%',
                'guaranteed_rate': '2.47%',
                'surrender_10y': '94.2%',
                'tax_benefit': '비과세',
                'extra_contribution': '가능',
                'partial_withdrawal': '가능',
                'premium_holiday': '가능'
            },
            {
                'company': '삼성생명',
                'product_name': '더좋은저축보험02',
                'current_rate': '3.59%',
                'guaranteed_rate': '3.02%',
                'surrender_10y': '95.1%',
                'tax_benefit': '비과세',
                'extra_contribution': '가능',
                'partial_withdrawal': '가능',
                'premium_holiday': '가능'
            },
            {
                'company': '교보생명',
                'product_name': '더좋은저축보험03',
                'current_rate': '3.26%',
                'guaranteed_rate': '2.64%',
                'surrender_10y': '93.8%',
                'tax_benefit': '비과세',
                'extra_contribution': '가능',
                'partial_withdrawal': '가능',
                'premium_holiday': '가능'
            }
        ]
        
        recommendations = []
        for i, product in enumerate(default_products[:request.top_n]):
            monthly_budget = request.monthly_budget or 50000
            annual_savings = monthly_budget * 12
            
            recommendation = SavingsProductRecommendation(
                product_id=f"savings_{i+1:03d}",
                company=product['company'],
                product_name=product['product_name'],
                product_type='저축성보험',
                score=95.0 - (i * 2.5),  # 점수 차등
                guaranteed_rate=product['guaranteed_rate'],
                current_rate=product['current_rate'],
                pay_period=f"{request.preferred_term or 15}년",
                term=f"{request.preferred_term or 15}년",
                monthly_premium_estimate=f"{monthly_budget:,}원",
                annual_savings=f"{annual_savings:,}원",
                surrender_5y='85.2%',
                surrender_10y=product['surrender_10y'],
                extra_contribution=product['extra_contribution'],
                partial_withdrawal=product['partial_withdrawal'],
                premium_holiday=product['premium_holiday'],
                tax_benefit=product['tax_benefit'],
                replacement_reason=f"월 {monthly_budget:,}원 예산으로 {annual_savings:,}원 연간 저축 + 세제혜택 + 환급 가능"
            )
            recommendations.append(recommendation)
        
        return recommendations

    def get_savings_profile_recommendations(self, request: UserProfileRecommendationRequest) -> List[SavingsProductRecommendation]:
        """사용자 특성 기반 저축성보험 추천"""
        # 사용자 특성을 고려한 저축성보험 추천
        savings_request = SavingsRecommendationRequest(
            monthly_budget=request.monthly_budget,
            preferred_term=15,
            min_guaranteed_rate=0.025,
            min_refund_10y=0.90,
            need_extra_contribution=False,
            need_partial_withdrawal=False,
            need_premium_holiday=False,
            weights={
                "return": 0.3,
                "refund": 0.3,
                "tax": 0.2,
                "flex": 0.2
            },
            top_n=request.top_n
        )
        
        return self.get_savings_recommendations(savings_request)

    def get_savings_analytics_summary(self) -> dict:
        """저축성보험 분석 요약 정보"""
        return {
            "total_savings_products": 15,
            "average_current_rate": "3.45%",
            "average_guaranteed_rate": "2.71%",
            "average_surrender_10y": "94.4%",
            "car_insurance_replacement_benefits": {
                "annual_savings_potential": "600,000원",
                "tax_benefits": "비과세 혜택",
                "flexibility": "추가납입, 부분인출, 보험료 납입유예 가능"
            },
            "status": "active"
        }

    def get_savings_products(self) -> List[dict]:
        """저축성보험 상품 목록"""
        return [
            {
                "product_id": "savings_001",
                "company": "신한라이프",
                "product_name": "더좋은저축보험01",
                "product_type": "저축성보험",
                "current_rate": "3.70%",
                "guaranteed_rate": "2.47%",
                "surrender_10y": "94.2%"
            },
            {
                "product_id": "savings_002", 
                "company": "삼성생명",
                "product_name": "더좋은저축보험02",
                "product_type": "저축성보험",
                "current_rate": "3.59%",
                "guaranteed_rate": "3.02%",
                "surrender_10y": "95.1%"
            }
        ]
