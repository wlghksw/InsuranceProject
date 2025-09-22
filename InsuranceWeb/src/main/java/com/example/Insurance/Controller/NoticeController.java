package com.example.Insurance.Controller;

import com.example.Insurance.Config.CustomUserDetails;
import com.example.Insurance.Entity.Notice; // Notice 엔티티 import
import com.example.Insurance.Entity.User;
import com.example.Insurance.Service.NoticeService; // NoticeService import
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List; // List import

@Controller
public class NoticeController {

    private final NoticeService noticeService;

    // 생성자를 통해 NoticeService 주입
    public NoticeController(NoticeService noticeService) {
        this.noticeService = noticeService;
    }

    @GetMapping("/notice")
    public String noticePage(Model model, @AuthenticationPrincipal CustomUserDetails userDetails) {
        // 1. 로그인한 사용자 정보 가져오기 (비로그인 시 null)
        User currentUser = (userDetails != null) ? userDetails.getUser() : null;

        // 2. 서비스로부터 모든 공지사항 목록 조회
        List<Notice> noticeList = noticeService.findAllNotices();

        // 3. 모델에 사용자 정보와 공지사항 목록 추가
        model.addAttribute("user", currentUser);
        model.addAttribute("noticeList", noticeList);

        // 4. notice 뷰 반환
        return "notice";
    }

    // ... 다른 페이지 컨트롤러 메서드들
}