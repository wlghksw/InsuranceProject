package com.example.Insurance.Controller;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class MainController {

    @Autowired
    private UserRepository userRepository;

    @GetMapping("/main")
    public String mainPage(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        if (userDetails != null) {
            // 로그인 상태일 때만 사용자 정보 추가
            User user = userRepository.findByLoginId(userDetails.getUsername())
                    .orElse(null);
            if (user != null) {
                model.addAttribute("user", user);
            }
        }
        return "main";
    }
}
