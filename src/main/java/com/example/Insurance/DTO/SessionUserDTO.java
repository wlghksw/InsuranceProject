package com.example.Insurance.DTO; // 실제 프로젝트 경로에 맞게 수정

import com.example.Insurance.Entity.User;
import lombok.Getter;
import java.io.Serializable;

@Getter
public class SessionUserDTO implements Serializable {

    private String nickname;
    private String loginId;
    private String realName; // 1. realName 필드 추가

    public SessionUserDTO(User user) {
        this.nickname = user.getNickname();
        this.loginId = user.getLoginId();
        this.realName = user.getRealName(); // 2. 생성자에서 realName 값 설정
    }
}