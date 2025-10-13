package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;

public class UserProfileRecommendationRequest {
    
    @JsonProperty("age")
    private Integer age;
    
    @JsonProperty("sex")
    private String sex;
    
    
    
    @JsonProperty("monthly_budget")
    private Integer monthlyBudget;
    
    @JsonProperty("min_coverage")
    private Integer minCoverage;
    
    @JsonProperty("max_premium_avg")
    private Double maxPremiumAvg;
    
    @JsonProperty("prefer_non_renewal")
    private Boolean preferNonRenewal = true;
    
    @JsonProperty("require_sales_channel")
    private String requireSalesChannel;
    
    @JsonProperty("family_cancer_history")
    private Boolean familyCancerHistory = false;
    
    @JsonProperty("preferred_coverage_period")
    private String preferredCoveragePeriod;
    
    @JsonProperty("top_n")
    private Integer topN = 10;
    
    // 기본 생성자
    public UserProfileRecommendationRequest() {}
    
    // 생성자
    public UserProfileRecommendationRequest(Integer age, String sex, 
                                          Integer monthlyBudget,
                                          Integer minCoverage, Double maxPremiumAvg, 
                                          Boolean preferNonRenewal, String requireSalesChannel, 
                                          Boolean familyCancerHistory, String preferredCoveragePeriod, Integer topN) {
        this.age = age;
        this.sex = sex;
        this.monthlyBudget = monthlyBudget;
        this.minCoverage = minCoverage;
        this.maxPremiumAvg = maxPremiumAvg;
        this.preferNonRenewal = preferNonRenewal;
        this.requireSalesChannel = requireSalesChannel;
        this.familyCancerHistory = familyCancerHistory;
        this.preferredCoveragePeriod = preferredCoveragePeriod;
        this.topN = topN;
    }
    
    // Getters and Setters
    public Integer getAge() {
        return age;
    }
    
    public void setAge(Integer age) {
        this.age = age;
    }
    
    public String getSex() {
        return sex;
    }
    
    public void setSex(String sex) {
        this.sex = sex;
    }
    
    
    public Integer getMonthlyBudget() {
        return monthlyBudget;
    }
    
    public void setMonthlyBudget(Integer monthlyBudget) {
        this.monthlyBudget = monthlyBudget;
    }
    
    public Integer getMinCoverage() {
        return minCoverage;
    }
    
    public void setMinCoverage(Integer minCoverage) {
        this.minCoverage = minCoverage;
    }
    
    public Double getMaxPremiumAvg() {
        return maxPremiumAvg;
    }
    
    public void setMaxPremiumAvg(Double maxPremiumAvg) {
        this.maxPremiumAvg = maxPremiumAvg;
    }
    
    public Boolean getPreferNonRenewal() {
        return preferNonRenewal;
    }
    
    public void setPreferNonRenewal(Boolean preferNonRenewal) {
        this.preferNonRenewal = preferNonRenewal;
    }
    
    public String getRequireSalesChannel() {
        return requireSalesChannel;
    }
    
    public void setRequireSalesChannel(String requireSalesChannel) {
        this.requireSalesChannel = requireSalesChannel;
    }
    
    public Integer getTopN() {
        return topN;
    }
    
    public void setTopN(Integer topN) {
        this.topN = topN;
    }
    
    public Boolean getFamilyCancerHistory() {
        return familyCancerHistory;
    }
    
    public void setFamilyCancerHistory(Boolean familyCancerHistory) {
        this.familyCancerHistory = familyCancerHistory;
    }
    
    public String getPreferredCoveragePeriod() {
        return preferredCoveragePeriod;
    }
    
    public void setPreferredCoveragePeriod(String preferredCoveragePeriod) {
        this.preferredCoveragePeriod = preferredCoveragePeriod;
    }
    
    @Override
    public String toString() {
        return "UserProfileRecommendationRequest{" +
                "age=" + age +
                ", sex='" + sex + '\'' +
                ", monthlyBudget=" + monthlyBudget +
                ", minCoverage=" + minCoverage +
                ", maxPremiumAvg=" + maxPremiumAvg +
                ", preferNonRenewal=" + preferNonRenewal +
                ", requireSalesChannel='" + requireSalesChannel + '\'' +
                ", familyCancerHistory=" + familyCancerHistory +
                ", preferredCoveragePeriod='" + preferredCoveragePeriod + '\'' +
                ", topN=" + topN +
                '}';
    }
}

