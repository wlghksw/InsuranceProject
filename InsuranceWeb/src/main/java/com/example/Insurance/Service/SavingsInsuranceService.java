package com.example.Insurance.Service;

import com.example.Insurance.DTO.SavingsInsuranceRecommendationRequest;
import com.example.Insurance.DTO.SavingsInsuranceRecommendationResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SavingsInsuranceService {
    
    @Value("${savings-insurance.api.url:http://localhost:8002}")
    private String savingsInsuranceApiUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    public SavingsInsuranceRecommendationResponse getRecommendations(SavingsInsuranceRecommendationRequest request) {
        try {
            String url = savingsInsuranceApiUrl + "/savings/recommend";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // purpose 값을 FastAPI가 이해할 수 있는 값으로 매핑
            String mappedPurpose = mapPurposeToFastAPI(request.getPurpose());
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("age", request.getAge());
            requestBody.put("monthly_budget", request.getMonthlyBudget());
            requestBody.put("purpose", mappedPurpose);
            requestBody.put("min_guaranteed_rate", request.getMinGuaranteedRate());
            requestBody.put("top_n", request.getTopN());
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return convertToSavingsInsuranceResponse(response.getBody());
            } else {
                throw new RuntimeException("저축성보험 추천 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            SavingsInsuranceRecommendationResponse errorResponse = new SavingsInsuranceRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("저축성보험 추천 서비스 오류: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }
    
    public SavingsInsuranceRecommendationResponse getPensionRecommendations(SavingsInsuranceRecommendationRequest request) {
        try {
            String url = savingsInsuranceApiUrl + "/pension/recommend";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // purpose 값을 FastAPI가 이해할 수 있는 값으로 매핑
            String mappedPurpose = mapPurposeToFastAPI(request.getPurpose());
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("age", request.getAge());
            requestBody.put("monthly_budget", request.getMonthlyBudget());
            requestBody.put("purpose", mappedPurpose);
            requestBody.put("min_guaranteed_rate", request.getMinGuaranteedRate());
            requestBody.put("top_n", request.getTopN());
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return convertToSavingsInsuranceResponse(response.getBody());
            } else {
                throw new RuntimeException("연금보험 추천 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            SavingsInsuranceRecommendationResponse errorResponse = new SavingsInsuranceRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("연금보험 추천 서비스 오류: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }
    
    private SavingsInsuranceRecommendationResponse convertToSavingsInsuranceResponse(Map<String, Object> responseBody) {
        SavingsInsuranceRecommendationResponse response = new SavingsInsuranceRecommendationResponse();
        response.setSuccess((Boolean) responseBody.get("success"));
        response.setMessage((String) responseBody.get("message"));
        response.setTotalProducts((Integer) responseBody.get("total_products"));
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> recommendations = (List<Map<String, Object>>) responseBody.get("recommendations");
        List<SavingsInsuranceRecommendationResponse.SavingsInsuranceProduct> products = new ArrayList<>();
        
        if (recommendations != null) {
            for (Map<String, Object> rec : recommendations) {
                SavingsInsuranceRecommendationResponse.SavingsInsuranceProduct product = 
                    new SavingsInsuranceRecommendationResponse.SavingsInsuranceProduct();
                product.setProductId((String) rec.get("product_id"));
                product.setCompany((String) rec.get("company"));
                product.setProductName((String) rec.get("product_name"));
                product.setProductType((String) rec.get("product_type"));
                product.setScore(((Number) rec.get("score")).doubleValue());
                product.setGuaranteedRate((String) rec.get("guaranteed_rate"));
                product.setCurrentRate((String) rec.get("current_rate"));
                product.setTerm((String) rec.get("term"));
                product.setMonthlyPremium((String) rec.get("monthly_premium"));
                product.setSurrenderValue((String) rec.get("surrender_value"));
                product.setPaymentMethod((String) rec.get("payment_method"));
                product.setUniversal((String) rec.get("universal"));
                product.setSalesChannel((String) rec.get("sales_channel"));
                product.setRecommendationReason((String) rec.get("recommendation_reason"));
                product.setAccumulationRate((String) rec.get("accumulation_rate"));
                products.add(product);
            }
        }
        
        response.setRecommendations(products);
        return response;
    }
    
    public Map<String, Object> getAnalyticsSummary() {
        try {
            String url = savingsInsuranceApiUrl + "/savings-insurance/analytics";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("저축성보험 분석 요약 API 호출 실패");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "저축성보험 분석 요약 조회 중 오류가 발생했습니다: " + e.getMessage());
            return errorResponse;
        }
    }
    
    /**
     * 사용자가 선택한 목적을 FastAPI가 이해할 수 있는 값으로 매핑
     */
    private String mapPurposeToFastAPI(String userPurpose) {
        if (userPurpose == null) {
            return "단기저축"; // 기본값
        }
        
        switch (userPurpose) {
            case "단기저축":
                return "단기저축";
            case "중기저축":
            case "장기저축":
            case "교육자금":
            case "주택자금":
            case "노후자금":
                return "연금준비"; // 장기 목적은 연금준비로 매핑
            case "세제혜택":
                return "세제혜택";
            default:
                return "단기저축"; // 기본값
        }
    }
}
