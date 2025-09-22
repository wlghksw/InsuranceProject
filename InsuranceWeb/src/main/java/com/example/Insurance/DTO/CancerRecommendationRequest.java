package com.example.Insurance.DTO;

import java.util.List;

public class CancerRecommendationRequest {
    private Integer minCoverage;
    private Double maxPremium;
    private Boolean preferNonRenewal;
    private String requireSalesChannel;
    private List<Double> weights;
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
