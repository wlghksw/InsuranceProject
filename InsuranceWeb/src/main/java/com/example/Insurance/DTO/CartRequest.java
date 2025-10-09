package com.example.Insurance.DTO;

import lombok.Data;

@Data
public class CartRequest {
    private String insuranceType; // "암보험", "상해보험", "저축성보험", "연금보험"
    private String insuranceCompany;
    private String productName;
    
    // 추가 정보 (선택적)
    private String coverageAmount;
    private String malePremium;
    private String femalePremium;
    private String monthlyPremium;
    private String guaranteedRate;
    private String currentRate;
    private String renewalCycle;
    private String term;
    private String paymentMethod;
    private String salesChannel;
    private String recommendationReason;
}


