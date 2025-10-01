package com.example.Insurance.DTO;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CalRequestDTO {
    private String type;

    // 공통 및 개별 필드
    private Integer age;
    private String gender; // 실손
    private Integer coverage; // 암
    private Integer deathBenefit; // 보장성
    private Integer experience; // 자동차
    private Integer days; // 여행자
    private String plan; // 어린이
    private Integer deposit; // 저축성, 연금
    private Integer years; // 저축성, 연금
}