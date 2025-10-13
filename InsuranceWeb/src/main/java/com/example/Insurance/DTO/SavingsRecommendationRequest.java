package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

public class SavingsRecommendationRequest {
    @JsonProperty("age")
    private Integer age;                        // 나이
    
    @JsonProperty("monthly_budget")
    private Integer monthlyBudget;              // 월 예산 (원)
    
    @JsonProperty("purpose")
    private String purpose;                     // 가입 목적 (연금준비, 단기저축, 세제혜택)
    
    @JsonProperty("preferred_term")
    private Integer preferredTerm;              // 선호하는 보험기간 (년)
    
    @JsonProperty("prefer_universal")
    private Boolean preferUniversal;            // 유니버셜 상품 선호 여부
    
    @JsonProperty("min_guaranteed_rate")
    private Double minGuaranteedRate;           // 최소 보증이율
    
    @JsonProperty("top_n")
    private Integer topN;                       // 추천 상품 개수

    // 기본 생성자
    public SavingsRecommendationRequest() {}

    // Getters and Setters
    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public Integer getMonthlyBudget() {
        return monthlyBudget;
    }

    public void setMonthlyBudget(Integer monthlyBudget) {
        this.monthlyBudget = monthlyBudget;
    }

    public String getPurpose() {
        return purpose;
    }

    public void setPurpose(String purpose) {
        this.purpose = purpose;
    }

    public Integer getPreferredTerm() {
        return preferredTerm;
    }

    public void setPreferredTerm(Integer preferredTerm) {
        this.preferredTerm = preferredTerm;
    }

    public Boolean getPreferUniversal() {
        return preferUniversal;
    }

    public void setPreferUniversal(Boolean preferUniversal) {
        this.preferUniversal = preferUniversal;
    }

    public Double getMinGuaranteedRate() {
        return minGuaranteedRate;
    }

    public void setMinGuaranteedRate(Double minGuaranteedRate) {
        this.minGuaranteedRate = minGuaranteedRate;
    }

    public Integer getTopN() {
        return topN;
    }

    public void setTopN(Integer topN) {
        this.topN = topN;
    }

    @Override
    public String toString() {
        return "SavingsRecommendationRequest{" +
                "age=" + age +
                ", monthlyBudget=" + monthlyBudget +
                ", purpose='" + purpose + '\'' +
                ", preferredTerm=" + preferredTerm +
                ", preferUniversal=" + preferUniversal +
                ", minGuaranteedRate=" + minGuaranteedRate +
                ", topN=" + topN +
                '}';
    }
}