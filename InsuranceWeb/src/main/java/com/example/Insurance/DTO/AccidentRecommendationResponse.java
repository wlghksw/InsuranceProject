package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.Map;

@Getter
@Setter
@JsonIgnoreProperties(ignoreUnknown = true)
public class AccidentRecommendationResponse {
    @JsonProperty("success")
    private boolean success;

    @JsonProperty("message")
    private String message;

    @JsonProperty("request_params")
    private Map<String, Object> requestParams;

    @JsonProperty("total_products")
    private int totalProducts;

    @JsonProperty("recommendations")
    private List<AccidentProduct> recommendations;

    @Getter
    @Setter
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class AccidentProduct {
        @JsonProperty("policy_id")
        private int policyId;

        @JsonProperty("insurance_company")
        private String insuranceCompany;

        @JsonProperty("product_name")
        private String productName;

        @JsonProperty("coverage_amount")
        private Integer coverageAmount;

        @JsonProperty("male_premium")
        private Double malePremium;

        @JsonProperty("female_premium")
        private Double femalePremium;

        @JsonProperty("avg_premium")
        private Double avgPremium;

        @JsonProperty("renewal_cycle")
        private String renewalCycle;

        @JsonProperty("surrender_value")
        private String surrenderValue;

        @JsonProperty("sales_channel")
        private String salesChannel;

        @JsonProperty("coverage_score")
        private double coverageScore;

        @JsonProperty("value_score")
        private double valueScore;

        @JsonProperty("stability_score")
        private double stabilityScore;

        @JsonProperty("final_score")
        private double finalScore;

    }
}