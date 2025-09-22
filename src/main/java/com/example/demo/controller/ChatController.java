package com.example.demo.controller;

import com.example.demo.dto.ChatResponseDto;
import com.example.demo.service.ChatbotService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ChatController {

    private final ChatbotService chatbotService;

    public ChatController(ChatbotService chatbotService) {
        this.chatbotService = chatbotService;
    }

    // http://localhost:8080/ask?query=여기에 질문 입력
    @GetMapping("/ask")
    public ChatResponseDto askQuestion(@RequestParam("query") String query) {
        return chatbotService.getChatbotResponse(query);
    }
}