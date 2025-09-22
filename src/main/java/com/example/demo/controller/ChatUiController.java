package com.example.demo.controller;

import com.example.demo.dto.ChatResponseDto;
import com.example.demo.dto.MessageDto;
import com.example.demo.service.ChatbotService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.ArrayList;
import java.util.List;

@Controller
public class ChatUiController {

    private final ChatbotService chatbotService;

    public ChatUiController(ChatbotService chatbotService) {
        this.chatbotService = chatbotService;
    }

    //️ 자주 묻는 질문 목록을 컨트롤러에 미리 정의
    private final List<String> faqList = List.of(
            "보험이란 뭔가요?",
            "보험수익자가 뭐야?",
            "보장금액 이란?",
            "보험 가입의 장점"
    );



    // 메인 채팅 페이지를 처음 열 때
    @GetMapping("/")
    public String chatPage(HttpSession session, Model model) {
        // 새로운 대화를 위해 이전 세션 기록은 삭제
        session.removeAttribute("chatHistory");

        //2. 메인 페이지를 열 때도 FAQ 목록을 전달
        model.addAttribute("faqList", faqList);
        return "chat";

    }

    @GetMapping("/ask-ui")
    public String askQuestion(@RequestParam(name = "query") String query, Model model, HttpSession session) {
        // 1. 세션에서 이전 대화 기록 불러오기
        List<MessageDto> history = (List<MessageDto>) session.getAttribute("chatHistory");
        if (history == null) {
            history = new ArrayList<>(); // 기록이 없으면 새로 생성
        }

        // 2. 사용자의 새 질문을 기록에 추가
        history.add(new MessageDto(query, "user"));

        // 3. Flask 챗봇 서비스 호출
        ChatResponseDto response = chatbotService.getChatbotResponse(query);

        // 4. 챗봇의 답변을 기록에 추가
        history.add(new MessageDto(response.getAnswer(), "bot"));

        // 5. 업데이트된 대화 기록을 다시 세션에 저장
        session.setAttribute("chatHistory", history);

        // 6. 화면에 전체 대화 기록 전달
        model.addAttribute("chatHistory", history);


        // 질문에 답변할 때도 FAQ 목록을 계속 전달
        model.addAttribute("faqList", faqList);

        return "chat";
    }
}