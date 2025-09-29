package com.example.Insurance.Service;

import com.example.Insurance.DTO.CancerFilterRequest;
import com.example.Insurance.DTO.CancerRecommendationResponse;
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
public class CancerRecommendationService {

    @Value("${cancer.api.url:http://localhost:8001}")
    private String cancerApiUrl;

    private final RestTemplate restTemplate;

    public CancerRecommendationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public CancerRecommendationResponse findRecommendations(CancerFilterRequest request) {
        try {
            // 요청 데이터 로깅
            System.out.println("=== Spring Boot에서 FastAPI로 전달하는 데이터 ===");
            System.out.println("minCoverage: " + request.getMinCoverage());
            System.out.println("maxPremium: " + request.getMaxPremium());
            System.out.println("preferNonRenewal: " + request.getPreferNonRenewal());
            System.out.println("requireSalesChannel: " + request.getRequireSalesChannel());
            System.out.println("weights: " + request.getWeights());
            System.out.println("topN: " + request.getTopN());
            System.out.println("===============================================");
            
            // FastAPI 서버로 요청 전송
            String url = cancerApiUrl + "/recommend";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<CancerFilterRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> responseBody = response.getBody();
                return convertToResponse(responseBody);
            } else {
                throw new RuntimeException("API 요청 실패: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            CancerRecommendationResponse errorResponse = new CancerRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("추천 API 호출 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }

    public List<Map<String, Object>> findAllProducts() {
        try {
            // FastAPI 서버에서 모든 상품 조회
            String url = cancerApiUrl + "/products/sample";
            
            ResponseEntity<Map[]> response = restTemplate.getForEntity(url, Map[].class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                Map[] products = response.getBody();
                List<Map<String, Object>> productList = new ArrayList<>();
                for (Map product : products) {
                    productList.add(product);
                }
                return productList;
            } else {
                throw new RuntimeException("상품 조회 API 요청 실패: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    private CancerRecommendationResponse convertToResponse(Map<String, Object> responseBody) {
        CancerRecommendationResponse response = new CancerRecommendationResponse();
        
        response.setSuccess((Boolean) responseBody.get("success"));
        response.setMessage((String) responseBody.get("message"));
        response.setTotalProducts((Integer) responseBody.get("total_products"));
        
        List<Map<String, Object>> recommendationsData = (List<Map<String, Object>>) responseBody.get("recommendations");
        List<CancerRecommendationResponse.CancerProduct> recommendations = new ArrayList<>();
        
        if (recommendationsData != null) {
            for (Map<String, Object> productData : recommendationsData) {
                CancerRecommendationResponse.CancerProduct product = new CancerRecommendationResponse.CancerProduct();
                
                product.setPolicyId((Integer) productData.get("policy_id"));
                product.setInsuranceCompany((String) productData.get("insurance_company"));
                product.setProductName((String) productData.get("product_name"));
                product.setCoverageAmount((Integer) productData.get("coverage_amount"));
                
                Object malePremium = productData.get("male_premium");
                if (malePremium != null) {
                    product.setMalePremium(((Number) malePremium).doubleValue());
                }
                
                Object femalePremium = productData.get("female_premium");
                if (femalePremium != null) {
                    product.setFemalePremium(((Number) femalePremium).doubleValue());
                }
                
                Object avgPremium = productData.get("avg_premium");
                if (avgPremium != null) {
                    product.setAvgPremium(((Number) avgPremium).doubleValue());
                }
                
                product.setRenewalCycle((String) productData.get("renewal_cycle"));
                product.setSurrenderValue((String) productData.get("surrender_value"));
                product.setSalesChannel((String) productData.get("sales_channel"));
                product.setCoverageScore(((Number) productData.get("coverage_score")).doubleValue());
                product.setValueScore(((Number) productData.get("value_score")).doubleValue());
                product.setStabilityScore(((Number) productData.get("stability_score")).doubleValue());
                product.setFinalScore(((Number) productData.get("final_score")).doubleValue());
                
                // coverage_details 추가
                Object coverageDetails = productData.get("coverage_details");
                if (coverageDetails instanceof List) {
                    @SuppressWarnings("unchecked")
                    List<String> detailsList = (List<String>) coverageDetails;
                    product.setCoverageDetails(detailsList);
                } else {
                    product.setCoverageDetails(new ArrayList<>());
                }
                
                recommendations.add(product);
            }
        }
        
        response.setRecommendations(recommendations);
        return response;
    }


    public Map<String, Object> getAnalyticsSummary() {
        try {
            // FastAPI 서버에서 분석 요약 조회
            String url = cancerApiUrl + "/analytics/summary";
            
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                throw new RuntimeException("분석 요약 API 요청 실패: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "분석 요약 API 호출 중 오류가 발생했습니다: " + e.getMessage());
            return errorResponse;
        }
    }

    public CancerRecommendationResponse findProfileRecommendations(UserProfileRecommendationRequest request) {
        try {
            // 기존 엔드포인트 사용 (이제 간단한 추천 시스템으로 변경됨)
            String url = cancerApiUrl + "/recommend/user-profile";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<UserProfileRecommendationRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> responseBody = response.getBody();
                return convertToResponse(responseBody);
            } else {
                throw new RuntimeException("사용자 특성 기반 추천 API 요청 실패: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            CancerRecommendationResponse errorResponse = new CancerRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("사용자 특성 기반 추천 API 호출 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }
}
