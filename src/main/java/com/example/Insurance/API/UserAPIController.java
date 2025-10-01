package com.example.Insurance.API;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
public class UserAPIController {

    @GetMapping("/api/user/current")
    public ResponseEntity<Map<String, Object>> getCurrentUser() {
        // Spring Security 컨텍스트에서 현재 인증된 사용자 정보를 가져옵니다.
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> userDetails = new HashMap<>();

        // 사용자가 인증되었는지 확인 (로그인 상태인지)
        if (authentication != null && authentication.isAuthenticated() && !"anonymousUser".equals(authentication.getPrincipal())) {
            userDetails.put("isAuthenticated", true);
            userDetails.put("username", authentication.getName());
            // 사용자의 역할(Role) 목록을 가져옵니다. 예: ["ROLE_USER", "ROLE_ADMIN"]
            userDetails.put("roles", authentication.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toList()));
        } else {
            userDetails.put("isAuthenticated", false);
        }

        return ResponseEntity.ok(userDetails);
    }
}

