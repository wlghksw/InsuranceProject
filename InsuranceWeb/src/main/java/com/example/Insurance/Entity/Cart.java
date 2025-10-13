package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "cart")
public class Cart {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long userId; // User 테이블의 ID

    @Column(nullable = false)
    private String insuranceType; // "암보험", "상해보험", "저축성보험", "연금보험"

    @Column(nullable = false)
    private String insuranceCompany; // 보험회사명

    @Column(nullable = false)
    private String productName; // 상품명

    // 상세 정보 (JSON 형태로 저장하거나 각각 필드로 저장)
    private String coverageAmount; // 보장금액
    private String malePremium; // 남성 보험료
    private String femalePremium; // 여성 보험료
    private String monthlyPremium; // 월 납입금
    private String guaranteedRate; // 최저보증이율
    private String currentRate; // 현재공시이율
    private String renewalCycle; // 갱신주기
    private String term; // 보험기간
    private String paymentMethod; // 납입방법
    private String salesChannel; // 판매채널
    
    @Column(length = 2000)
    private String recommendationReason; // 추천 이유

    @Column(nullable = false, updatable = false)
    private LocalDateTime addedAt; // 담은 날짜

    @PrePersist
    protected void onCreate() {
        this.addedAt = LocalDateTime.now();
    }

    @Builder
    public Cart(Long userId, String insuranceType, String insuranceCompany, String productName,
                String coverageAmount, String malePremium, String femalePremium,
                String monthlyPremium, String guaranteedRate, String currentRate,
                String renewalCycle, String term, String paymentMethod, String salesChannel,
                String recommendationReason) {
        this.userId = userId;
        this.insuranceType = insuranceType;
        this.insuranceCompany = insuranceCompany;
        this.productName = productName;
        this.coverageAmount = coverageAmount;
        this.malePremium = malePremium;
        this.femalePremium = femalePremium;
        this.monthlyPremium = monthlyPremium;
        this.guaranteedRate = guaranteedRate;
        this.currentRate = currentRate;
        this.renewalCycle = renewalCycle;
        this.term = term;
        this.paymentMethod = paymentMethod;
        this.salesChannel = salesChannel;
        this.recommendationReason = recommendationReason;
    }
}


