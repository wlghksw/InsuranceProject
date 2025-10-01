package com.example.Insurance.Controller;

import com.example.Insurance.Entity.Insurance;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.InsuranceService;
import com.example.Insurance.Service.UserService;
import com.example.Insurance.DTO.SessionUserDTO; // SessionUser DTO 사용 시
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.SessionAttribute;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;

/**
 * '내 보험 찾기' 관련 페이지 및 기능 요청을 처리하는 컨트롤러입니다.
 */
@Controller
@RequiredArgsConstructor
public class InsuranceController {

    private final InsuranceService insuranceService;
    private final UserService userService;

    /**
     * '내 보험 찾기' 페이지를 보여줍니다.
     * 로그인 상태인 경우, 헤더에 사용자 정보를 표시하기 위해 모델에 user 객체를 추가합니다.
     * @param user  세션에 저장된 사용자 정보
     * @param model 뷰에 데이터를 전달하기 위한 객체
     * @return "user/my_insurance" 뷰 이름
     */
    @GetMapping("/user/my_insurance")
    public String showFindMyInsurancePage(@SessionAttribute(name = "user", required = false) SessionUserDTO user, Model model) {
        if (user != null) {
            model.addAttribute("user", user);
        }
        return "user/my_insurance";
    }

    /**
     * 사용자가 입력한 정보로 '내 보험'을 조회합니다.
     * 반드시 로그인 상태여야 하며, 입력된 정보가 로그인한 사용자의 정보와 일치하는지 검증합니다.
     * @param userDetails 현재 로그인한 사용자의 상세 정보 (Spring Security가 주입)
     * @param realName    사용자가 입력한 실제 이름
     * @param ssnFront    사용자가 입력한 주민등록번호 앞자리
     * @param ssnBack     사용자가 입력한 주민등록번호 뒷자리
     * @param agreement   개인정보 동의 여부
     * @param model       결과 페이지로 데이터를 전달하기 위한 객체
     * @param redirectAttributes 리다이렉트 시 플래시 메시지를 전달하기 위한 객체
     * @return 성공 시 결과 페이지, 실패 시 조회 페이지로 리다이렉트
     */
    @PostMapping("/user/my_insurance/find")
    public String findMyInsurances(@AuthenticationPrincipal UserDetails userDetails,
                                   @RequestParam("username") String realName,
                                   @RequestParam("userSsn1") String ssnFront,
                                   @RequestParam("userSsn2") String ssnBack,
                                   @RequestParam(value = "확인", required = false) String agreement,
                                   Model model,
                                   RedirectAttributes redirectAttributes) {

        // 1. 비로그인 상태이거나 개인정보 동의를 하지 않은 경우 차단
        if (userDetails == null) {
            return "redirect:/user/login";
        }
        if (agreement == null) {
            redirectAttributes.addFlashAttribute("errorMessage", "조회하려면 고객님의 동의가 필요합니다.");
            return "redirect:/user/my_insurance";
        }

        // 2. 현재 로그인된 사용자의 정보를 가져옵니다.
        String loginId = userDetails.getUsername();
        User loggedInUser = userService.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalStateException("인증된 사용자 정보를 찾을 수 없습니다."));

        // 3. 입력된 정보가 로그인된 사용자의 정보와 일치하는지 검증합니다. (보안 강화)
        String inputSsn = ssnFront + "-" + ssnBack;
        if (!loggedInUser.getRealName().equals(realName) || !loggedInUser.getSsn().equals(inputSsn)) {
            redirectAttributes.addFlashAttribute("errorMessage", "로그인된 사용자 정보와 일치하지 않습니다.");
            return "redirect:/user/my_insurance";
        }

        // 4. 검증 완료 후, 해당 사용자의 보험 목록을 조회합니다.
        List<Insurance> insuranceList = insuranceService.findByUser(loggedInUser);

        model.addAttribute("username", loggedInUser.getRealName());
        model.addAttribute("insuranceList", insuranceList);

        // 헤더에 로그인 정보를 표시하기 위해 user 객체도 함께 전달합니다.
        model.addAttribute("user", new SessionUserDTO(loggedInUser));

        return "user/my_insurance_result";
    }
}