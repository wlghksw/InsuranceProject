package com.example.Insurance.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.fasterxml.jackson.annotation.JsonProperty;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatbotResponse {
    private String answer;
    private Double score;
    
    @JsonProperty("error")
    private String error;
}




