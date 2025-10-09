package com.example.Insurance.DTO;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccidentRecommendationRequest {
    private int age;
    private String sex;
    private int topN = 5;
    private String sortBy = "default";
}

