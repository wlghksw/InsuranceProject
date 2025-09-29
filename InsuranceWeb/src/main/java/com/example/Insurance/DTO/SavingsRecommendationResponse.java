package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class SavingsRecommendationResponse {
    private Boolean success;
    private String message;
    private Integer totalProducts;
    private List<SavingsProductRecommendation> recommendations;
    private SavingsRecommendationRequest requestParams;

    // 기본 생성자
    public SavingsRecommendationResponse() {}

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Integer getTotalProducts() {
        return totalProducts;
    }

    public void setTotalProducts(Integer totalProducts) {
        this.totalProducts = totalProducts;
    }

    public List<SavingsProductRecommendation> getRecommendations() {
        return recommendations;
    }

    public void setRecommendations(List<SavingsProductRecommendation> recommendations) {
        this.recommendations = recommendations;
    }

    public SavingsRecommendationRequest getRequestParams() {
        return requestParams;
    }

    public void setRequestParams(SavingsRecommendationRequest requestParams) {
        this.requestParams = requestParams;
    }

    // 내부 클래스: 저축성보험 상품 추천 정보
    public static class SavingsProductRecommendation {
        @JsonProperty("product_id")
        private String productId;
        private String company;
        @JsonProperty("product_name")
        private String productName;
        @JsonProperty("product_type")
        private String productType;
        private Double score;
        @JsonProperty("guaranteed_rate")
        private String guaranteedRate;
        @JsonProperty("current_rate")
        private String currentRate;
        @JsonProperty("pay_period")
        private String payPeriod;
        private String term;
        @JsonProperty("monthly_premium_estimate")
        private String monthlyPremiumEstimate;
        @JsonProperty("annual_savings")
        private String annualSavings;
        @JsonProperty("surrender_5y")
        private String surrender5y;
        @JsonProperty("surrender_10y")
        private String surrender10y;
        @JsonProperty("extra_contribution")
        private String extraContribution;
        @JsonProperty("partial_withdrawal")
        private String partialWithdrawal;
        @JsonProperty("premium_holiday")
        private String premiumHoliday;
        @JsonProperty("tax_benefit")
        private String taxBenefit;
        @JsonProperty("replacement_reason")
        private String replacementReason;

        // 기본 생성자
        public SavingsProductRecommendation() {}

        // Getters and Setters
        public String getProductId() {
            return productId;
        }

        public void setProductId(String productId) {
            this.productId = productId;
        }

        public String getCompany() {
            return company;
        }

        public void setCompany(String company) {
            this.company = company;
        }

        public String getProductName() {
            return productName;
        }

        public void setProductName(String productName) {
            this.productName = productName;
        }

        public String getProductType() {
            return productType;
        }

        public void setProductType(String productType) {
            this.productType = productType;
        }

        public Double getScore() {
            return score;
        }

        public void setScore(Double score) {
            this.score = score;
        }

        public String getGuaranteedRate() {
            return guaranteedRate;
        }

        public void setGuaranteedRate(String guaranteedRate) {
            this.guaranteedRate = guaranteedRate;
        }

        public String getCurrentRate() {
            return currentRate;
        }

        public void setCurrentRate(String currentRate) {
            this.currentRate = currentRate;
        }

        public String getPayPeriod() {
            return payPeriod;
        }

        public void setPayPeriod(String payPeriod) {
            this.payPeriod = payPeriod;
        }

        public String getTerm() {
            return term;
        }

        public void setTerm(String term) {
            this.term = term;
        }

        public String getMonthlyPremiumEstimate() {
            return monthlyPremiumEstimate;
        }

        public void setMonthlyPremiumEstimate(String monthlyPremiumEstimate) {
            this.monthlyPremiumEstimate = monthlyPremiumEstimate;
        }

        public String getAnnualSavings() {
            return annualSavings;
        }

        public void setAnnualSavings(String annualSavings) {
            this.annualSavings = annualSavings;
        }

        public String getSurrender5y() {
            return surrender5y;
        }

        public void setSurrender5y(String surrender5y) {
            this.surrender5y = surrender5y;
        }

        public String getSurrender10y() {
            return surrender10y;
        }

        public void setSurrender10y(String surrender10y) {
            this.surrender10y = surrender10y;
        }

        public String getExtraContribution() {
            return extraContribution;
        }

        public void setExtraContribution(String extraContribution) {
            this.extraContribution = extraContribution;
        }

        public String getPartialWithdrawal() {
            return partialWithdrawal;
        }

        public void setPartialWithdrawal(String partialWithdrawal) {
            this.partialWithdrawal = partialWithdrawal;
        }

        public String getPremiumHoliday() {
            return premiumHoliday;
        }

        public void setPremiumHoliday(String premiumHoliday) {
            this.premiumHoliday = premiumHoliday;
        }

        public String getTaxBenefit() {
            return taxBenefit;
        }

        public void setTaxBenefit(String taxBenefit) {
            this.taxBenefit = taxBenefit;
        }

        public String getReplacementReason() {
            return replacementReason;
        }

        public void setReplacementReason(String replacementReason) {
            this.replacementReason = replacementReason;
        }
        
        // 세부 점수 필드들
        private Double returnScore;
        private Double refundScore;
        private Double taxScore;
        private Double flexibilityScore;

        public Double getReturnScore() {
            return returnScore;
        }

        public void setReturnScore(Double returnScore) {
            this.returnScore = returnScore;
        }

        public Double getRefundScore() {
            return refundScore;
        }

        public void setRefundScore(Double refundScore) {
            this.refundScore = refundScore;
        }

        public Double getTaxScore() {
            return taxScore;
        }

        public void setTaxScore(Double taxScore) {
            this.taxScore = taxScore;
        }

        public Double getFlexibilityScore() {
            return flexibilityScore;
        }

        public void setFlexibilityScore(Double flexibilityScore) {
            this.flexibilityScore = flexibilityScore;
        }
    }
}
