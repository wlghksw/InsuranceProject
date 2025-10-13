package com.example.Insurance.DTO;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SavingsInsuranceRecommendationRequest {
    private int age;
    private int monthlyBudget;
    private String purpose;
    private Double minGuaranteedRate;
    private int topN = 5;
}
