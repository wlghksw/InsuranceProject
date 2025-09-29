package com.example.Insurance.DTO;

import java.util.List;

public class CancerRecommendationResponse {
    private boolean success;
    private String message;
    private int totalProducts;
    private List<CancerProduct> recommendations;

    // 기본 생성자
    public CancerRecommendationResponse() {}

    // Getters and Setters
    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public int getTotalProducts() {
        return totalProducts;
    }

    public void setTotalProducts(int totalProducts) {
        this.totalProducts = totalProducts;
    }

    public List<CancerProduct> getRecommendations() {
        return recommendations;
    }

    public void setRecommendations(List<CancerProduct> recommendations) {
        this.recommendations = recommendations;
    }

    // 내부 클래스
    public static class CancerProduct {
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
        private List<String> coverageDetails;

        // 기본 생성자
        public CancerProduct() {}

        // Getters and Setters
        public int getPolicyId() {
            return policyId;
        }

        public void setPolicyId(int policyId) {
            this.policyId = policyId;
        }

        public String getInsuranceCompany() {
            return insuranceCompany;
        }

        public void setInsuranceCompany(String insuranceCompany) {
            this.insuranceCompany = insuranceCompany;
        }

        public String getProductName() {
            return productName;
        }

        public void setProductName(String productName) {
            this.productName = productName;
        }

        public int getCoverageAmount() {
            return coverageAmount;
        }

        public void setCoverageAmount(int coverageAmount) {
            this.coverageAmount = coverageAmount;
        }

        public Double getMalePremium() {
            return malePremium;
        }

        public void setMalePremium(Double malePremium) {
            this.malePremium = malePremium;
        }

        public Double getFemalePremium() {
            return femalePremium;
        }

        public void setFemalePremium(Double femalePremium) {
            this.femalePremium = femalePremium;
        }

        public Double getAvgPremium() {
            return avgPremium;
        }

        public void setAvgPremium(Double avgPremium) {
            this.avgPremium = avgPremium;
        }

        public String getRenewalCycle() {
            return renewalCycle;
        }

        public void setRenewalCycle(String renewalCycle) {
            this.renewalCycle = renewalCycle;
        }

        public String getSurrenderValue() {
            return surrenderValue;
        }

        public void setSurrenderValue(String surrenderValue) {
            this.surrenderValue = surrenderValue;
        }

        public String getSalesChannel() {
            return salesChannel;
        }

        public void setSalesChannel(String salesChannel) {
            this.salesChannel = salesChannel;
        }

        public double getCoverageScore() {
            return coverageScore;
        }

        public void setCoverageScore(double coverageScore) {
            this.coverageScore = coverageScore;
        }

        public double getValueScore() {
            return valueScore;
        }

        public void setValueScore(double valueScore) {
            this.valueScore = valueScore;
        }

        public double getStabilityScore() {
            return stabilityScore;
        }

        public void setStabilityScore(double stabilityScore) {
            this.stabilityScore = stabilityScore;
        }

        public double getFinalScore() {
            return finalScore;
        }

        public void setFinalScore(double finalScore) {
            this.finalScore = finalScore;
        }

        public List<String> getCoverageDetails() {
            return coverageDetails;
        }

        public void setCoverageDetails(List<String> coverageDetails) {
            this.coverageDetails = coverageDetails;
        }
    }
}
