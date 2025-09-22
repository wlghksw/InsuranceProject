package com.example.demo.service;

import com.example.demo.dto.ChatRequestDto;
import com.example.demo.dto.ChatResponseDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ChatbotService {

    private final RestTemplate restTemplate;

    @Value("${flask.api.url}") // application.properties에서 URL 주소를 가져옴
    private String flaskApiUrl;

    public ChatbotService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public ChatResponseDto getChatbotResponse(String userQuestion) {
        ChatRequestDto requestDto = new ChatRequestDto(userQuestion);

        // restTemplate을 사용해 Flask 서버의 /chat 엔드포인트로 POST 요청을 보냄
        return restTemplate.postForObject(flaskApiUrl, requestDto, ChatResponseDto.class);
    }
}