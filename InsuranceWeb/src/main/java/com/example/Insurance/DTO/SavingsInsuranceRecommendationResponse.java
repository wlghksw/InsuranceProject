package com.example.Insurance.DTO;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SavingsInsuranceRecommendationResponse {
    private boolean success;
    private String message;
    private int totalProducts;
    private List<SavingsInsuranceProduct> recommendations;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SavingsInsuranceProduct {
        @JsonProperty("product_id")
        private String productId;
        private String company;
        @JsonProperty("product_name")
        private String productName;
        @JsonProperty("product_type")
        private String productType;
        private double score;
        @JsonProperty("guaranteed_rate")
        private String guaranteedRate;
        @JsonProperty("current_rate")
        private String currentRate;
        private String term;
        @JsonProperty("monthly_premium")
        private String monthlyPremium;
        @JsonProperty("surrender_value")
        private String surrenderValue;
        @JsonProperty("payment_method")
        private String paymentMethod;
        private String universal;
        @JsonProperty("sales_channel")
        private String salesChannel;
        @JsonProperty("recommendation_reason")
        private String recommendationReason;
        @JsonProperty("accumulation_rate")
        private String accumulationRate;
    }
}
