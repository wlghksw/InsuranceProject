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
public class CalculationHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 어떤 사용자의 계산 기록인지 연결합니다. (N:1 관계)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String insuranceType; // 계산한 보험 종류 (예: "CANCER", "CAR")

    // 계산 시 사용된 주요 입력값들을 저장합니다.
    private Integer age;
    private Integer coverage; // 암 진단비
    private Integer experience; // 운전 경력
    private Integer days; // 여행 기간
    private Integer deposit; // 월 납입액
    private Integer years; // 납입 기간
    // ... 필요한 다른 계산 요소 필드 추가

    @Column(nullable = false)
    private Long calculatedPremium; // 계산된 결과 보험료

    @Column(updatable = false, nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }

    @Builder
    public CalculationHistory(User user, String insuranceType, Integer age, Integer coverage,
                              Integer experience, Integer days, Integer deposit, Integer years,
                              Long calculatedPremium) {
        this.user = user;
        this.insuranceType = insuranceType;
        this.age = age;
        this.coverage = coverage;
        this.experience = experience;
        this.days = days;
        this.deposit = deposit;
        this.years = years;
        this.calculatedPremium = calculatedPremium;
    }
}
