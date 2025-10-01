package com.example.Insurance.Controller;

import com.example.Insurance.DTO.UserRegisterDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import java.util.Optional;

@Controller
public class UserController {

    private static final Logger log = LoggerFactory.getLogger(UserController.class);
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 로그인 페이지
    @GetMapping("/user/login")
    public String loginForm(Model model,
                            @RequestParam(value = "error", required = false) String error,
                            @RequestParam(value = "logout", required = false) String logout,
                            @RequestParam(value = "success", required = false) Boolean success) {
        log.info("GET /user/login - 로그인 폼 요청");
        if (error != null) {
            model.addAttribute("errorMessage", "아이디 또는 비밀번호가 올바르지 않습니다.");
        }
        if (logout != null) {
            model.addAttribute("successMessage", "성공적으로 로그아웃되었습니다.");
        }
        if (success != null && success) {
            model.addAttribute("successMessage", "회원가입이 완료되었습니다. 로그인해주세요.");
        }
        return "user/login";
    }

    // 회원가입 페이지
    @GetMapping("/user/register")
    public String registerForm(Model model) {
        log.info("GET /user/register - 회원가입 폼 요청");
        model.addAttribute("userRegisterDTO", new UserRegisterDTO());
        return "user/register";
    }

    // 회원가입 처리
    @PostMapping("/user/register")
    public String registerUser(@ModelAttribute UserRegisterDTO registerDTO, Model model) {
        log.info("POST /user/register - 회원가입 시도: loginId={}", registerDTO.getLoginId());
        try {
            userService.register(registerDTO);
            log.info("회원가입 성공: loginId={}", registerDTO.getLoginId());
            return "redirect:/user/login?success=true";
        } catch (IllegalArgumentException e) {
            log.warn("회원가입 실패: loginId={}, reason={}", registerDTO.getLoginId(), e.getMessage());
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("userRegisterDTO", registerDTO);
            return "user/register";
        }
    }

     // 아이디 찾기 페이지
    @GetMapping("/user/find_id")
    public String findIdForm() {
        log.info("GET /user/find_id - 아이디 찾기 폼 요청");
        return "user/find_id";
    }

     // 아이디 찾기 요청
    @PostMapping("/user/find_id")
    public String findIdAction(@RequestParam String realName,
                               @RequestParam String phone,
                               RedirectAttributes redirectAttributes) {
        log.info("POST /user/find_id - 아이디 찾기 시도: realName={}", realName);
        Optional<User> optionalUser = userService.findByRealNameAndPhone(realName, phone);

        if (optionalUser.isPresent()) {
            User foundUser = optionalUser.get();
            String message = "회원님의 아이디는 [ " + foundUser.getLoginId() + " ] 입니다.";
            log.info("아이디 찾기 성공: realName={}", realName);
            redirectAttributes.addFlashAttribute("successMessage", message);
        } else {
            String message = "해당 정보로 가입된 회원을 찾을 수 없습니다.";
            log.warn("아이디 찾기 실패: realName={}", realName);
            redirectAttributes.addFlashAttribute("errorMessage", message);
        }
        return "redirect:/user/find_id";
    }
}



