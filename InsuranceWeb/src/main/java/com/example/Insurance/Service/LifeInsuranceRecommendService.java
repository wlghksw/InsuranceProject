package com.example.Insurance.Service;

import com.example.Insurance.DTO.LifeInsuranceRecommendDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class LifeInsuranceRecommendService {

    private final RestTemplate restTemplate;
    
    @Value("${cancer.api.url:http://localhost:8002}")
    private String apiUrl;

    public LifeInsuranceRecommendDTO.Response recommend(LifeInsuranceRecommendDTO.Request req) {
        try {
            log.info("종신보험 추천 요청: gender={}, age={}, job={}", req.getGender(), req.getAge(), req.getJob());
            
            // FastAPI 엔드포인트 URL
            String url = apiUrl + "/recommend/life";
            
            // 요청 파라미터 구성
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("gender", req.getGender() != null ? req.getGender() : "남자");
            requestBody.put("age", req.getAge() != null ? req.getAge() : 30);
            requestBody.put("job", req.getJob() != null ? req.getJob() : "사무직");
            requestBody.put("desiredPremium", req.getDesiredPremium() != null ? req.getDesiredPremium() : 50000);
            requestBody.put("desiredCoverage", req.getDesiredCoverage() != null ? req.getDesiredCoverage() : 10000000);
            requestBody.put("topk", req.getTopk() != null ? req.getTopk() : 5);
            requestBody.put("sortBy", normalizeSortBy(req.getSortBy()));
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            
            // FastAPI 호출
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return convertToResponse(response.getBody());
            } else {
                return new LifeInsuranceRecommendDTO.Response("API 요청 실패: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            log.error("종신보험 추천 실패", e);
            return new LifeInsuranceRecommendDTO.Response("server_error: " + e.getMessage());
        }
    }

    private String normalizeSortBy(Object sortBy) {
        if (sortBy == null) return "distance";
        String s = String.valueOf(sortBy).trim().toLowerCase();
        if (s.contains("premium") || s.contains("보험료")) return "premium";
        if (s.contains("coverage") || s.contains("보장")) return "coverage";
        return "distance";
    }

    @SuppressWarnings("unchecked")
    private LifeInsuranceRecommendDTO.Response convertToResponse(Map<String, Object> apiResponse) {
        LifeInsuranceRecommendDTO.Response response = new LifeInsuranceRecommendDTO.Response();
        
        try {
            List<Map<String, Object>> recommendations = (List<Map<String, Object>>) apiResponse.get("recommendations");
            
            if (recommendations == null || recommendations.isEmpty()) {
                response.setItems(Collections.emptyList());
                return response;
            }
            
            List<LifeInsuranceRecommendDTO.Item> items = new ArrayList<>();
            
            for (Map<String, Object> rec : recommendations) {
                LifeInsuranceRecommendDTO.Item item = new LifeInsuranceRecommendDTO.Item();
                item.setProduct(String.valueOf(rec.get("product")));
                item.setProductPremium(getInteger(rec, "premium"));
                item.setProductCoverage(getInteger(rec, "coverage"));
                items.add(item);
            }
            
            response.setItems(items);
            log.info("종신보험 추천 성공: {}개 상품 반환", items.size());
            
        } catch (Exception e) {
            log.error("응답 변환 중 오류", e);
            response.setError("응답 변환 실패: " + e.getMessage());
        }
        
        return response;
    }

    private Integer getInteger(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return null;
        if (value instanceof Number) return ((Number) value).intValue();
        try {
            return Integer.parseInt(String.valueOf(value).replaceAll("[,_\\s]", ""));
        } catch (Exception e) {
            return null;
        }
    }
}
