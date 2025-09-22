package com.example.demo.dto;

public class MessageDto {
    private String content;
    private String sender; // "user" 또는 "bot"

    public MessageDto(String content, String sender) {
        this.content = content;
        this.sender = sender;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }

    // 머스타치에서 사용자가 보낸 메시지인지 확인하기 위한 편의 메소드
    public boolean isUser() {
        return "user".equals(this.sender);
    }
}