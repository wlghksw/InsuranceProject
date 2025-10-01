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

    // 로그인
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

    // 비밀번호 찾기
    @GetMapping("/user/find_pw")
    public String findPwForm(Model model) {
        log.info("GET /user/find_pw - 비밀번호 찾기 폼 요청");
        model.addAttribute("isUserVerified", false);
        return "user/find_pw";
    }

    @PostMapping("/user/verify-account")
    public String verifyAccount(@RequestParam String loginId,
                                @RequestParam String realName,
                                @RequestParam String phone,
                                Model model) {
        log.info("POST /user/verify-account - 계정 확인 시도: loginId={}, realName={}", loginId, realName);
        Optional<User> optionalUser = userService.findByLoginIdAndRealNameAndPhone(loginId, realName, phone);

        if (optionalUser.isPresent()) {
            log.info("계정 확인 성공: loginId={}", loginId);
            model.addAttribute("isUserVerified", true);
            // Mustache의 {{user.loginId}}에 값을 전달하기 위해 user 객체 또는 맵을 사용
            model.addAttribute("user", optionalUser.get());
        } else {
            log.warn("계정 확인 실패: loginId={}", loginId);
            model.addAttribute("isUserVerified", false);
            model.addAttribute("errorMessage", "입력하신 정보와 일치하는 사용자가 없습니다.");
        }
        return "user/find_pw";
    }

    @PostMapping("/user/reset-password")
    public String resetPassword(@RequestParam String loginId,
                                @RequestParam String newPassword,
                                @RequestParam String confirmPassword,
                                RedirectAttributes redirectAttributes) {
        log.info("POST /user/reset-password - 비밀번호 재설정 시도: loginId={}", loginId);


        if (!newPassword.equals(confirmPassword)) {
            log.warn("비밀번호 재설정 실패: 비밀번호 불일치, loginId={}", loginId);
            redirectAttributes.addFlashAttribute("errorMessage", "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.");
            return "redirect:/user/find_pw";
        }

        try {
            userService.resetPassword(loginId, newPassword); // UserService에 이 메소드 구현 필요
            log.info("비밀번호 재설정 성공: loginId={}", loginId);
            redirectAttributes.addFlashAttribute("successMessage", "비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요.");
            return "redirect:/user/login";
        } catch (Exception e) {
            log.error("비밀번호 재설정 중 오류 발생: loginId={}", loginId, e);
            redirectAttributes.addFlashAttribute("errorMessage", "비밀번호 변경 중 오류가 발생했습니다. 다시 시도해주세요.");
            return "redirect:/user/find_pw";
        }
    }
}



