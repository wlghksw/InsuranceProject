package com.example.demo.dto;

// Flask로부터 받을 응답 데이터를 담을 클래스
public class ChatResponseDto {
    private String answer;
    private double score;

    // Getter, Setter (기본 생성자도 있으면 좋습니다)
    public ChatResponseDto() {}

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }
}