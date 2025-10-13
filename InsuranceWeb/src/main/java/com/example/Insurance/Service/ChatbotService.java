package com.example.Insurance.Service;

import com.example.Insurance.DTO.ChatbotRequest;
import com.example.Insurance.DTO.ChatbotResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class ChatbotService {
    
    private final RestTemplate restTemplate;
    
    @Value("${chatbot.api.url:http://localhost:5001}")
    private String chatbotApiUrl;
    
    public ChatbotService() {
        this.restTemplate = new RestTemplate();
    }
    
    /**
     * Flask 챗봇 API에 질문을 전송하고 답변을 받아옵니다
     */
    public ChatbotResponse getAnswer(String question) {
        try {
            String url = chatbotApiUrl + "/chat";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("question", question);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            ResponseEntity<ChatbotResponse> response = restTemplate.postForEntity(url, entity, ChatbotResponse.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                ChatbotResponse errorResponse = new ChatbotResponse();
                errorResponse.setAnswer("죄송합니다. 현재 답변을 가져올 수 없습니다.");
                errorResponse.setScore(0.0);
                return errorResponse;
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            ChatbotResponse errorResponse = new ChatbotResponse();
            errorResponse.setAnswer("챗봇 서비스 오류: " + e.getMessage());
            errorResponse.setScore(0.0);
            errorResponse.setError(e.getMessage());
            return errorResponse;
        }
    }
}




