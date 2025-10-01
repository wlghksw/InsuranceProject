package com.example.Insurance.Controller;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.UserService; // [추가] UserService 임포트
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ServiceController {

    private final UserService userService;

    public ServiceController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/service_intro")
    public String serviceIntroPage(Model model, @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails != null) {
            // UserDetails에서 사용자 ID(loginId)를 가져와 DB에서 전체 User 정보를 조회합니다.
            String loginId = userDetails.getUsername();
            userService.findByLoginId(loginId)
                    .ifPresent(user -> model.addAttribute("user", user));
        }
        return "service_intro";
    }
}
