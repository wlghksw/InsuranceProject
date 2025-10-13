package com.example.Insurance.DTO;

import lombok.Data;

@Data
public class InsuranceProductRequest {
    private String productType; // 암보험, 상해보험, 저축성보험
    private String insuranceCompany;
    private String productName;
    private String coverageAmount;
    private String malePremium;
    private String femalePremium;
    private String renewalCycle;
    private String guaranteedRate;
    private String currentRate;
    private String term;
    private String monthlyPremium;
    private String surrenderValue;
    private String paymentMethod;
    private String salesChannel;
    private String specialNotes;
}



