package com.example.Insurance.Service;

import com.example.Insurance.DTO.SavingsRecommendationRequest;
import com.example.Insurance.DTO.SavingsRecommendationResponse;
import com.example.Insurance.DTO.UserProfileRecommendationRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SavingsService {

    @Value("${savings.api.url:http://localhost:8000}")
    private String savingsApiUrl;

    private final RestTemplate restTemplate;

    public SavingsService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public SavingsRecommendationResponse getRecommendations(SavingsRecommendationRequest request) {
        try {
            // 요청 데이터 로깅
        System.out.println("=== Spring Boot에서 FastAPI로 전달하는 연금보험 데이터 ===");
        System.out.println("age: " + request.getAge());
        System.out.println("monthly_budget: " + request.getMonthlyBudget());
        System.out.println("purpose: " + request.getPurpose());
        System.out.println("preferred_term: " + request.getPreferredTerm());
        System.out.println("prefer_universal: " + request.getPreferUniversal());
        System.out.println("min_guaranteed_rate: " + request.getMinGuaranteedRate());
        System.out.println("top_n: " + request.getTopN());
        System.out.println("===============================================");
            
            // FastAPI 서버로 요청 전송
            String url = savingsApiUrl + "/savings/recommend";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // 수동으로 Map을 만들어서 전송 (Jackson @JsonProperty 문제 해결)
            Map<String, Object> requestMap = new HashMap<>();
            requestMap.put("age", request.getAge() != null ? request.getAge() : 35);  // 기본값: 35세
            requestMap.put("monthly_budget", request.getMonthlyBudget() != null ? request.getMonthlyBudget() : 300000);  // 기본값: 30만원
            requestMap.put("purpose", request.getPurpose() != null ? request.getPurpose() : "연금준비");  // 기본값: 연금준비
            requestMap.put("preferred_term", request.getPreferredTerm());
            requestMap.put("prefer_universal", request.getPreferUniversal());
            requestMap.put("min_guaranteed_rate", request.getMinGuaranteedRate());
            requestMap.put("top_n", request.getTopN() != null ? request.getTopN() : 5);  // 기본값: 5개
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestMap, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return convertToSavingsResponse(response.getBody());
            } else {
                throw new RuntimeException("연금보험 추천 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            SavingsRecommendationResponse errorResponse = new SavingsRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("연금보험 추천 서비스 오류: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }

    public SavingsRecommendationResponse getProfileRecommendations(UserProfileRecommendationRequest request) {
        try {
            // 사용자 프로필 기반 연금보험 추천
            String url = savingsApiUrl + "/savings/profile-recommend";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<UserProfileRecommendationRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<SavingsRecommendationResponse> response = restTemplate.postForEntity(url, entity, SavingsRecommendationResponse.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("사용자 프로필 기반 연금보험 추천 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            SavingsRecommendationResponse errorResponse = new SavingsRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("사용자 프로필 기반 연금보험 추천 서비스 오류: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }

    public Map<String, Object> getAnalyticsSummary() {
        try {
            String url = savingsApiUrl + "/savings/analytics/summary";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("연금보험 분석 요약 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "연금보험 분석 요약 조회 중 오류가 발생했습니다: " + e.getMessage());
            return errorResponse;
        }
    }

    public List<Map<String, Object>> getAllProducts() {
        try {
            String url = savingsApiUrl + "/savings/products";
            ResponseEntity<List> response = restTemplate.getForEntity(url, List.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("연금보험 상품 목록 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    private SavingsRecommendationResponse convertToSavingsResponse(Map<String, Object> responseBody) {
        // FastAPI 응답 데이터 로깅
        System.out.println("=== FastAPI에서 받은 응답 데이터 ===");
        System.out.println("전체 응답: " + responseBody);
        if (responseBody.containsKey("recommendations")) {
            List<Map<String, Object>> recommendations = (List<Map<String, Object>>) responseBody.get("recommendations");
            if (recommendations != null && !recommendations.isEmpty()) {
                System.out.println("첫 번째 추천 상품 데이터: " + recommendations.get(0));
                System.out.println("첫 번째 추천 상품의 키들: " + recommendations.get(0).keySet());
            }
        }
        System.out.println("===============================================");
        
        SavingsRecommendationResponse response = new SavingsRecommendationResponse();
        
        // 기본 필드 설정
        response.setSuccess((Boolean) responseBody.get("success"));
        response.setMessage((String) responseBody.get("message"));
        
        Object totalProductsObj = responseBody.get("total_products");
        if (totalProductsObj instanceof Number) {
            response.setTotalProducts(((Number) totalProductsObj).intValue());
        }
        
        // 추천 상품 목록 변환
        List<Map<String, Object>> recommendationsData = (List<Map<String, Object>>) responseBody.get("recommendations");
        List<SavingsRecommendationResponse.SavingsProductRecommendation> recommendations = new ArrayList<>();
        
        if (recommendationsData != null) {
            for (Map<String, Object> recData : recommendationsData) {
                SavingsRecommendationResponse.SavingsProductRecommendation recommendation = 
                    new SavingsRecommendationResponse.SavingsProductRecommendation();
                
                recommendation.setProductId((String) recData.get("product_id"));
                recommendation.setCompany((String) recData.get("company"));
                recommendation.setProductName((String) recData.get("product_name"));
                recommendation.setProductType((String) recData.get("product_type"));
                
                Object scoreObj = recData.get("score");
                if (scoreObj instanceof Number) {
                    recommendation.setScore(((Number) scoreObj).doubleValue());
                }
                
                recommendation.setGuaranteedRate((String) recData.get("guaranteed_rate"));
                recommendation.setCurrentRate((String) recData.get("current_rate"));
                recommendation.setPayPeriod((String) recData.get("payment_method"));
                recommendation.setTerm((String) recData.get("term"));
                recommendation.setMonthlyPremiumEstimate((String) recData.get("monthly_premium"));
                recommendation.setAnnualSavings((String) recData.get("annual_savings"));
                recommendation.setSurrender5y((String) recData.get("surrender_5y"));
                recommendation.setSurrender10y((String) recData.get("surrender_value"));
                recommendation.setExtraContribution((String) recData.get("extra_contribution"));
                recommendation.setPartialWithdrawal((String) recData.get("partial_withdrawal"));
                recommendation.setPremiumHoliday((String) recData.get("premium_holiday"));
                recommendation.setTaxBenefit((String) recData.get("tax_benefit"));
                recommendation.setReplacementReason((String) recData.get("recommendation_reason"));
                
                // 세부 점수 필드 추가
                Object returnScoreObj = recData.get("return_score");
                if (returnScoreObj instanceof Number) {
                    recommendation.setReturnScore(((Number) returnScoreObj).doubleValue());
                }
                
                Object refundScoreObj = recData.get("refund_score");
                if (refundScoreObj instanceof Number) {
                    recommendation.setRefundScore(((Number) refundScoreObj).doubleValue());
                }
                
                Object taxScoreObj = recData.get("tax_score");
                if (taxScoreObj instanceof Number) {
                    recommendation.setTaxScore(((Number) taxScoreObj).doubleValue());
                }
                
                Object flexibilityScoreObj = recData.get("flexibility_score");
                if (flexibilityScoreObj instanceof Number) {
                    recommendation.setFlexibilityScore(((Number) flexibilityScoreObj).doubleValue());
                }
                
                recommendations.add(recommendation);
            }
        }
        
        response.setRecommendations(recommendations);
        return response;
    }
}
