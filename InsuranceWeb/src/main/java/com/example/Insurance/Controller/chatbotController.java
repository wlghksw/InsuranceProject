package com.example.Insurance.Controller;

import com.example.Insurance.DTO.ChatbotRequest;
import com.example.Insurance.DTO.ChatbotResponse;
import com.example.Insurance.Service.ChatbotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
public class ChatbotController {
    
    @Autowired
    private ChatbotService chatbotService;
    
    /**
     * 챗봇 페이지 렌더링
     */
    @GetMapping("/chatbot")
    public String chatbotPage() {
        return "chatbot";
    }
    
    /**
     * 챗봇 API - 질문에 대한 답변 반환
     */
    @PostMapping("/chatbot/ask")
    @ResponseBody
    public ResponseEntity<ChatbotResponse> askQuestion(@RequestBody ChatbotRequest request) {
        try {
            ChatbotResponse response = chatbotService.getAnswer(request.getQuestion());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ChatbotResponse errorResponse = new ChatbotResponse();
            errorResponse.setAnswer("오류가 발생했습니다: " + e.getMessage());
            errorResponse.setScore(0.0);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
}
