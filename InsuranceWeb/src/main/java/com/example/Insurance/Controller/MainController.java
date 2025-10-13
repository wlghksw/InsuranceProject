package com.example.Insurance.Controller;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Controller
public class MainController {

    @Autowired
    private UserRepository userRepository;
    
    private final RestTemplate restTemplate = new RestTemplate();

    // /main 으로 리다이렉트
    @GetMapping("/")
    public String root() {
        return "redirect:/main";
    }

    // 일반 로그인(Security UserDetails) + 카카오 OAuth2 로그인 통합 처리
    @GetMapping("/main")
    public String mainPage(
            @AuthenticationPrincipal UserDetails userDetails,
            @AuthenticationPrincipal OAuth2User oauth2User,
            Model model) {
        
        // 일반 로그인 처리
        if (userDetails != null) {
            User user = userRepository.findByLoginId(userDetails.getUsername()).orElse(null);
            if (user != null) {
                model.addAttribute("user", user);
                model.addAttribute("name", user.getRealName());
            }
        }
        // 카카오 OAuth2 로그인 처리
        else if (oauth2User != null) {
            Map<String, Object> attrs = oauth2User.getAttributes();
            Map<String, Object> kakaoAccount = (attrs == null) ? null
                    : (Map<String, Object>) attrs.get("kakao_account");
            
            String name = getStr(kakaoAccount, "name");
            String email = getStr(kakaoAccount, "email");
            
            // 프로필 정보가 있는 경우
            if (kakaoAccount != null && kakaoAccount.containsKey("profile")) {
                Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");
                if (name == null) {
                    name = getStr(profile, "nickname"); // 이름이 없으면 닉네임 사용
                }
            }
            
            model.addAttribute("name", name != null ? name : "카카오 사용자");
            model.addAttribute("isOAuth2", true);
        }
        
        
        return "main";
    }

    // 마이페이지 (미로그인 시 로그인 페이지로)
    @GetMapping("/user/myPage")
    public String myPage(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        if (userDetails == null) {
            return "redirect:/user/login";
        }
        User user = userRepository.findByLoginId(userDetails.getUsername()).orElse(null);
        if (user != null) {
            model.addAttribute("user", user);
        }
        return "user/myPage";
    }

    @GetMapping("/home")
    public String homeRedirect() {
        return "redirect:/main";
    }

    // 카카오 OAuth2 로그인 성공 핸들러 (메인에 정보 뿌리기)
    @GetMapping("/login/success")
    public String success(@AuthenticationPrincipal OAuth2User user, Model model) {
        if (user != null) {
            Map<String, Object> attrs = user.getAttributes();
            Map<String, Object> kakaoAccount = (attrs == null) ? null
                    : (Map<String, Object>) attrs.get("kakao_account");

            String name = getStr(kakaoAccount, "name");            // 예: 전지훈
            String gender = getStr(kakaoAccount, "gender");        // 예: male
            String birthyear = getStr(kakaoAccount, "birthyear");  // 예: 2001
            String phone = normalizeKrPhone(getStr(kakaoAccount, "phone_number"));

            String birth = (birthyear != null) ? birthyear : "";

            model.addAttribute("id", user.getAttribute("id"));
            model.addAttribute("name", name);
            model.addAttribute("gender", gender);
            model.addAttribute("birth", birth);
            model.addAttribute("phone", phone);
            model.addAttribute("attrs", attrs);
        }
        return "main";
    }

    @GetMapping("/login/failure")
    public String failure(HttpSession session, Model model) {
        Object msg = session.getAttribute("oauthError");
        if (msg != null) {
            model.addAttribute("error", msg);
            session.removeAttribute("oauthError");
        }
        return "main";
    }

    // ===== 유틸 메서드들 =====
    private static String getStr(Map<String, Object> m, String k){
        if (m == null) return null;
        Object v = m.get(k);
        return v == null ? null : v.toString();
    }

    private static boolean nonEmpty(String s){ return s != null && !s.isBlank(); }

    private static String normalizeKrPhone(String phone){
        if (!nonEmpty(phone)) return null;
        String p = phone.replaceAll("[\\s-]", "");
        if (p.startsWith("+82")) p = "0" + p.substring(3);
        return p;
    }
}
