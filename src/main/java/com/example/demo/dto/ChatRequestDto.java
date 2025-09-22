package com.example.demo.dto;

// Flask에 보낼 요청 데이터를 담을 클래스
public class ChatRequestDto {
    private String question;

    // 생성자, Getter, Setter
    public ChatRequestDto(String question) {
        this.question = question;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }
}