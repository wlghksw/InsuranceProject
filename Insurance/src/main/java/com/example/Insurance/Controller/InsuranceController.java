package com.example.Insurance.Controller;

import com.example.Insurance.Config.CustomUserDetails;
import com.example.Insurance.Entity.Insurance;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.InsuranceService;
import com.example.Insurance.Service.UserService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping; // PostMapping 추가
import org.springframework.web.bind.annotation.RequestParam; // RequestParam 추가
import org.springframework.web.servlet.mvc.support.RedirectAttributes; // RedirectAttributes 추가


import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.Optional;

@Controller
public class InsuranceController {

    private final InsuranceService insuranceService;
    private final UserService userService;

    @Autowired
    public InsuranceController(InsuranceService insuranceService, UserService userService) {
        this.insuranceService = insuranceService;
        this.userService = userService;
    }

    // 기존 getMyInsurances, getMyInsuranceDetails 메서드...
    @GetMapping("/user/my_insurance")
    public String showFindMyInsurancePage(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        // 로그인 상태라면, 헤더에 닉네임 등을 표시하기 위해 user 객체를 전달할 수 있습니다.
        if (userDetails != null) {
            model.addAttribute("user", userDetails.getUser());
        }
        return "/user/my_insurance";
    }

    // ... 기존 getMyInsuranceDetails 메서드

    // ============== [추가된 메서드] ==============

    /**
     * 이름과 주민번호로 가입된 보험을 조회하는 메서드
     */
    @PostMapping("/user/my_insurance/find")
    public String findMyInsurances(@RequestParam("username") String realName,
                                   @RequestParam("userSsn1") String ssnFront,
                                   @RequestParam("userSsn2") String ssnBack,
                                   @RequestParam(value = "확인", required = false) String agreement,
                                   Model model,
                                   RedirectAttributes redirectAttributes) {

        // 1. 약관 동의 여부 확인
        if (agreement == null) {
            redirectAttributes.addFlashAttribute("errorMessage", "조회하려면 고객님의 동의가 필요합니다.");
            return "redirect:/user/my_insurance";
        }

        // 2. 이름과 주민번호로 사용자 조회
        String ssn = ssnFront + "-" + ssnBack; // 주민번호 합치기
        Optional<User> userOpt = userService.findByRealNameAndSsn(realName, ssn);

        // 3. 사용자가 존재하지 않을 경우
        if (userOpt.isEmpty()) {
            redirectAttributes.addFlashAttribute("errorMessage", "입력하신 정보와 일치하는 사용자가 없습니다.");
            return "redirect:/user/my_insurance";
        }

        // 4. 사용자가 존재할 경우, 해당 사용자의 보험 목록 조회
        User foundUser = userOpt.get();
        List<Insurance> insuranceList = insuranceService.findByUser(foundUser);

        // 5. 조회 결과를 Model에 담아 결과 페이지로 전달
        model.addAttribute("username", foundUser.getRealName()); // 조회된 사용자의 실명
        model.addAttribute("insuranceList", insuranceList);

        return "/user/my_insurance_result"; // 결과를 보여줄 뷰 템플릿
    }
}
