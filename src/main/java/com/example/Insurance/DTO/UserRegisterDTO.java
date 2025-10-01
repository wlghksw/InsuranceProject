package com.example.Insurance.DTO;

import lombok.Getter;
import lombok.Setter;

// 회원가입 폼(register.html)의 필드와 정확히 일치해야 합니다.
@Getter
@Setter
public class UserRegisterDTO {
    private String loginId;
    private String password;
    private String nickname;
    private String realName;
    private String phone;
    private String birthYear; // String으로 받아서 서비스에서 처리
    private String gender;
}
