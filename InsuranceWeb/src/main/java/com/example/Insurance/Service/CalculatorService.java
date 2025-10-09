package com.example.Insurance.Service;

import com.example.Insurance.DTO.CalRequestDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CalculatorService {

    /**
     * 클라이언트의 요청 DTO를 받아 보험 종류에 따라 적절한 계산 메소드를 호출합니다.
     * @param requestDto 계산에 필요한 데이터
     * @return 계산된 보험료 또는 예상 만기 금액
     */
    public long calculate(CalRequestDTO requestDto) {
        String type = requestDto.getType();

        switch (type) {
            case "cancer":
                return calculateCancerPremium(requestDto.getAge(), requestDto.getCoverage());
            case "health": // 실손보험 추가
                return calculateHealthPremium(requestDto.getAge(), requestDto.getGender());
            case "protection": // 보장성보험 추가
                return calculateProtectionPremium(requestDto.getAge(), requestDto.getDeathBenefit());
            case "car":
                return calculateCarPremium(requestDto.getAge(), requestDto.getExperience());
            case "travel":
                return calculateTravelPremium(requestDto.getDays());
            case "child": // 어린이/태아보험 추가
                return calculateChildPremium(requestDto.getAge(), requestDto.getPlan());
            case "savings": // 저축성보험 추가
                return calculateSavingsPayout(requestDto.getDeposit(), requestDto.getYears());
            case "annuity":
                return calculateAnnuityPayout(requestDto.getDeposit(), requestDto.getYears());
            default:
                throw new IllegalArgumentException("지원하지 않는 보험 종류입니다: " + type);
        }
    }

    // --- 각 보험별 가상 계산 로직 ---

    private long calculateCancerPremium(int age, int coverage) {
        long base = 10000;
        double ageRate = age > 40 ? 2.1 : 1.5;
        long coverageCost = (long) (coverage / 1000.0) * 4000;
        return (long) (base * ageRate) + coverageCost;
    }

    private long calculateHealthPremium(int age, String gender) {
        long base = 15000;
        double ageRate = age > 40 ? 1.5 : 1.1;
        double genderRate = "male".equals(gender) ? 1.2 : 1.0;
        return (long) (base * ageRate * genderRate);
    }

    private long calculateProtectionPremium(int age, int deathBenefit) {
        long base = 20000;
        double ageRate = age > 40 ? 1.8 : 1.2;
        long benefitCost = (long) (deathBenefit / 10000.0) * 8000; // 사망보험금 1억당 8000원
        return (long) (base * ageRate) + benefitCost;
    }

    private long calculateCarPremium(int age, int experience) {
        long base = 700000;
        double ageRate = age < 26 ? 1.5 : (age < 30 ? 1.2 : 1.0);
        double expRate = experience < 3 ? 1.3 : 1.0;
        return (long) (base * ageRate * expRate);
    }

    private long calculateTravelPremium(int days) {
        long dailyBase = 1200;
        return dailyBase * days;
    }

    private long calculateChildPremium(int age, String plan) {
        long base = 20000;
        long ageCost = age == 0 ? 10000 : age * 500; // 태아일 때 할증
        double planRate = "premium".equals(plan) ? 1.5 : 1.0;
        return (long) ((base + ageCost) * planRate);
    }

    private long calculateSavingsPayout(int deposit, int years) {
        // 연 2.5% 복리 수익률 가정
        double annualRate = 0.025;
        double monthlyRate = annualRate / 12;
        int totalMonths = years * 12;
        // 복리 계산 공식 (만기 시 예상 환급금)
        double futureValue = deposit * ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate);
        return (long) futureValue;
    }

    private long calculateAnnuityPayout(int deposit, int years) {
        // 연 3.5% 복리 수익률 가정
        double annualRate = 0.035;
        double monthlyRate = annualRate / 12;
        int totalMonths = years * 12;
        // 복리 계산 공식 (만기 시 예상 연금액)
        double futureValue = deposit * ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate);
        return (long) futureValue;
    }
}
