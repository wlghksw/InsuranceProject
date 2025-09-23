package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class CancerRecommendationRequest {
    @JsonProperty("min_coverage")
    private Integer minCoverage;
    
    @JsonProperty("max_premium_avg")
    private Double maxPremium;
    
    @JsonProperty("prefer_non_renewal")
    private Boolean preferNonRenewal;
    
    @JsonProperty("require_sales_channel")
    private String requireSalesChannel;
    
    @JsonProperty("weights")
    private List<Double> weights;
    
    @JsonProperty("top_n")
    private Integer topN;

    // 기본 생성자
    public CancerRecommendationRequest() {}

    // Getters and Setters
    public Integer getMinCoverage() {
        return minCoverage;
    }

    public void setMinCoverage(Integer minCoverage) {
        this.minCoverage = minCoverage;
    }

    public Double getMaxPremium() {
        return maxPremium;
    }

    public void setMaxPremium(Double maxPremium) {
        this.maxPremium = maxPremium;
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

    public List<Double> getWeights() {
        return weights;
    }

    public void setWeights(List<Double> weights) {
        this.weights = weights;
    }

    public Integer getTopN() {
        return topN;
    }

    public void setTopN(Integer topN) {
        this.topN = topN;
    }
}
