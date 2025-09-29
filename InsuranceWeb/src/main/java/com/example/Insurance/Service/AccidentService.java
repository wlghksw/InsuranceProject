// src/main/java/com/example/Insurance/Service/AccidentService.java

package com.example.Insurance.Service;

import com.example.Insurance.DTO.AccidentRecommendationRequest;
import com.example.Insurance.DTO.AccidentRecommendationResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.Map;

@Slf4j // ◀◀◀ 롬복(Lombok) 로깅 어노테이션 추가
@Service
public class AccidentService {

    @Value("${python.api.url:http://127.0.0.1:8000}")
    private String pythonApiUrl;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public AccidentService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    public AccidentRecommendationResponse getAccidentRecommendations(AccidentRecommendationRequest request) {
        try {
            String url = pythonApiUrl + "/recommend/accident";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<AccidentRecommendationRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                // ▼▼▼ 여기에 로그 추가 ▼▼▼
                log.info("성공: Python API로부터 받은 원본 데이터: {}", response.getBody());

                AccidentRecommendationResponse result = objectMapper.convertValue(response.getBody(), AccidentRecommendationResponse.class);

                // ▼▼▼ 여기에 로그 추가 ▼▼▼
                log.info("성공: Java DTO로 변환된 데이터의 상품 개수: {}", result.getRecommendations().size());

                return result;
            } else {
                throw new RuntimeException("상해보험 추천 API 요청 실패: " + response.getStatusCode());
            }

        } catch (Exception e) {
            // ▼▼▼ 여기에 로그 추가 ▼▼▼
            log.error("오류: 상해보험 추천 API 호출 중 예외 발생", e);

            AccidentRecommendationResponse errorResponse = new AccidentRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("상해보험 추천 API 호출 중 오류 발생: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(new ArrayList<>());
            return errorResponse;
        }
    }
}