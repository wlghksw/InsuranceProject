package com.example.Insurance.Entity;

import lombok.Getter;

@Getter
public enum UserRole {
    // Spring Security는 역할(Role) 이름 앞에 'ROLE_' 접두사를 붙여 인식하는 규칙을 가집니다.
    USER("ROLE_USER"),
    ADMIN("ROLE_ADMIN");

    private final String value;

    UserRole(String value) {
        this.value = value;
    }
}