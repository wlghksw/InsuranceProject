package com.example.Insurance.Controller;

import com.example.Insurance.DTO.UserDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.UserService;
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

    // [수정] final 키워드를 추가하고 @Autowired 대신 생성자 주입을 사용합니다.
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/user/login")
    public String loginForm(Model model,
                            @RequestParam(value = "error", required = false) String error,
                            @RequestParam(value = "logout", required = false) String logout,
                            @RequestParam(value = "success", required = false) Boolean success) { // [추가] 회원가입 성공 파라미터

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

    @GetMapping("/user/register")
    public String registerForm(Model model) {
        model.addAttribute("userDTO", new UserDTO());
        return "user/register";
    }

    @PostMapping("/user/register")
    public String register(@ModelAttribute UserDTO userDTO, Model model, RedirectAttributes redirectAttributes) {
        try {
            userService.register(userDTO);
            // [수정] RedirectAttributes를 사용하여 성공 메시지를 전달할 수도 있지만,
            // 로그인 페이지에서 파라미터로 처리하는 것이 더 간단하므로 리다이렉트 경로를 유지합니다.
            return "redirect:/user/login?success=true";
        } catch (IllegalArgumentException e) { // [개선] 더 구체적인 예외를 잡는 것이 좋습니다.
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("userDTO", userDTO); // 입력했던 내용을 유지하기 위해 DTO를 다시 전달
            return "user/register";
        }
    }

    /**
     * [추가] 아이디 찾기 폼을 보여주는 GET 메서드
     */
    @GetMapping("/user/find_id")
    public String findIdForm() {
        return "user/find_id";
    }

    @PostMapping("/user/find_id")
    public String findIdAction(@RequestParam String realName,
                               @RequestParam String phone,
                               RedirectAttributes redirectAttributes) {

        Optional<User> optionalUser = userService.findByRealNameAndPhone(realName, phone);

        if (optionalUser.isPresent()) {
            User foundUser = optionalUser.get();
            String message = "회원님의 아이디는 [ " + foundUser.getLoginId() + " ] 입니다.";
            redirectAttributes.addFlashAttribute("successMessage", message);
        } else {
            String message = "해당 정보로 가입된 회원을 찾을 수 없습니다.";
            redirectAttributes.addFlashAttribute("errorMessage", message);
        }
        return "redirect:/user/find_id";
    }
}


