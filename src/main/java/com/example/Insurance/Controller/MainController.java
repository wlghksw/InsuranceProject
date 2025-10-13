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

import java.util.Map;

@Controller
public class MainController {

    @GetMapping("/")
    public String home() {
        return "main"; }

    @GetMapping("/login/success")
    public String success(@AuthenticationPrincipal OAuth2User user, Model model) {
        if (user != null) {
            Map<String, Object> attrs = user.getAttributes();
            Map<String, Object> kakaoAccount = (Map<String, Object>) attrs.get("kakao_account");

            String name = getStr(kakaoAccount, "name");            // 전지훈
            String gender = getStr(kakaoAccount, "gender");        // male
            String birthyear = getStr(kakaoAccount, "birthyear");  // 2001
            String phone = normalizeKrPhone(getStr(kakaoAccount, "phone_number"));

            // birthyear만 있으면 그걸 birth로 그대로 사용
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
