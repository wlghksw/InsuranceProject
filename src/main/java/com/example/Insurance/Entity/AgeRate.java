package com.example.Insurance.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.Getter;

@Entity
@Getter
public class AgeRate {
    @Id
    private Long id;
    private int ageStart; // 나이 구간 시작
    private int ageEnd;   // 나이 구간 끝
    private double rate;  // 적용 요율(보험 비율)
}
