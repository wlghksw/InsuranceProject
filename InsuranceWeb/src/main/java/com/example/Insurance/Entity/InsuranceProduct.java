package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
@Table(name = "insurance_products")
public class InsuranceProduct {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String productType; // "암보험", "상해보험", "저축성보험"

    @Column(nullable = false)
    private String insuranceCompany;

    @Column(nullable = false)
    private String productName;

    private String coverageAmount; // 보장금액
    private String malePremium; // 남성 보험료
    private String femalePremium; // 여성 보험료
    private String renewalCycle; // 갱신주기
    private String guaranteedRate; // 최저보증이율
    private String currentRate; // 현재공시이율
    private String term; // 보험기간
    private String monthlyPremium; // 월 납입금
    private String surrenderValue; // 해약환급금
    private String paymentMethod; // 납입방법
    private String salesChannel; // 판매채널
    
    @Column(length = 2000)
    private String specialNotes; // 특이사항

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }
}



