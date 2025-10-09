package com.example.Insurance.Service;

import com.example.Insurance.DTO.AccidentRecommendationRequest;
import com.example.Insurance.DTO.AccidentRecommendationResponse;
import com.example.Insurance.DTO.AccidentRecommendationResponse.AccidentProduct;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class AccidentService {
    
    @Value("${accident.api.url:http://localhost:8002}")
    private String accidentApiUrl;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public AccidentService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }
    
    public AccidentRecommendationResponse getRecommendations(AccidentRecommendationRequest request) {
        try {
            String url = accidentApiUrl + "/recommend/accident";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestMap = Map.of(
                "age", request.getAge(),
                "sex", request.getSex(),
                "top_n", request.getTopN(),
                "sort_by", request.getSortBy()
            );
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestMap, headers);
            
            Map<String, Object> response = restTemplate.exchange(
                url, HttpMethod.POST, entity, Map.class
            ).getBody();
            
            return convertToAccidentResponse(response);
            
        } catch (Exception e) {
            throw new RuntimeException("상해보험 추천 서비스 오류: " + e.getMessage(), e);
        }
    }
    
    private AccidentRecommendationResponse convertToAccidentResponse(Map<String, Object> response) {
        AccidentRecommendationResponse accidentResponse = new AccidentRecommendationResponse();
        accidentResponse.setSuccess((Boolean) response.get("success"));
        accidentResponse.setMessage((String) response.get("message"));
        accidentResponse.setTotalProducts((Integer) response.get("total_products"));
        
        // recommendations 처리
        if (response.get("recommendations") != null) {
            java.util.List<Map<String, Object>> recommendationsList = (java.util.List<Map<String, Object>>) response.get("recommendations");
            java.util.List<AccidentProduct> accidentProducts = new java.util.ArrayList<>();
            
            for (Map<String, Object> rec : recommendationsList) {
                AccidentProduct product = new AccidentProduct();
                product.setPolicyId(((Number) rec.get("policy_id")).intValue());
                product.setInsuranceCompany((String) rec.get("insurance_company"));
                product.setProductName((String) rec.get("product_name"));
                product.setCoverageAmount(((Number) rec.get("coverage_amount")).intValue());
                product.setMalePremium(((Number) rec.get("male_premium")).doubleValue());
                product.setFemalePremium(((Number) rec.get("female_premium")).doubleValue());
                product.setAvgPremium(((Number) rec.get("avg_premium")).doubleValue());
                product.setRenewalCycle((String) rec.get("renewal_cycle"));
                product.setSurrenderValue((String) rec.get("surrender_value"));
                product.setSalesChannel((String) rec.get("sales_channel"));
                product.setCoverageScore(((Number) rec.get("coverage_score")).doubleValue());
                product.setValueScore(((Number) rec.get("value_score")).doubleValue());
                product.setStabilityScore(((Number) rec.get("stability_score")).doubleValue());
                product.setFinalScore(((Number) rec.get("final_score")).doubleValue());
                
                accidentProducts.add(product);
            }
            
            accidentResponse.setRecommendations(accidentProducts);
        }
        
        return accidentResponse;
    }
}

