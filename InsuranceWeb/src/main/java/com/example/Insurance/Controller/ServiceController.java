package com.example.Insurance.Controller;

import com.example.Insurance.Config.CustomUserDetails; // import 추가
import com.example.Insurance.Entity.User;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ServiceController {

    @GetMapping("/service_intro")
    public String serviceIntroPage(Model model, @AuthenticationPrincipal CustomUserDetails userDetails) { // 타입 변경
        User currentUser = (userDetails != null) ? userDetails.getUser() : null; // 비로그인 상태도 고려
        model.addAttribute("user", currentUser);
        return "service_intro";
    }

    // ... (다른 페이지 컨트롤러도 모두 동일한 방식으로 수정)
}
