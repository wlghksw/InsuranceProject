package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.AccessLevel;
import lombok.Builder;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "insurances")
public class Insurance {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String insuranceName;

    @Column
    private String insuranceType;

    // 증권번호
    @Column(nullable = false, unique = true)
    private String policyNumber;

    // 보장기간 (예: "2000-01-01 ~ 2030-12-31") 형식
    @Column(nullable = false)
    private String coveragePeriod;

    // 월 납입액
    @Column(nullable = false)
    private int monthlyPremium;

    @Column(nullable = false)
    private LocalDateTime subscriptionDate;

    @Builder
    public Insurance(User user, String insuranceName, String insuranceType, String policyNumber, String coveragePeriod, int monthlyPremium, LocalDateTime subscriptionDate) {
        this.user = user;
        this.insuranceName = insuranceName;
        this.insuranceType = insuranceType;
        this.policyNumber = policyNumber;
        this.coveragePeriod = coveragePeriod;
        this.monthlyPremium = monthlyPremium;
        this.subscriptionDate = subscriptionDate;
    }
}
