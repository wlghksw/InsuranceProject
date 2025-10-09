package com.example.Insurance.DTO;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccidentRecommendationResponse {
    private boolean success;
    private String message;
    private int totalProducts;
    private List<AccidentProduct> recommendations;
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AccidentProduct {
        private int policyId;
        private String insuranceCompany;
        private String productName;
        private int coverageAmount;
        private Double malePremium;
        private Double femalePremium;
        private Double avgPremium;
        private String renewalCycle;
        private String surrenderValue;
        private String salesChannel;
        private double coverageScore;
        private double valueScore;
        private double stabilityScore;
        private double finalScore;
    }
}

