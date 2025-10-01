package com.example.Insurance.Controller;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Entity.UserRole;
import com.example.Insurance.Service.AdminService;
import jakarta.persistence.EntityNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/admin")
public class AdminController {

    private static final Logger log = LoggerFactory.getLogger(AdminController.class);
    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    @GetMapping("/dashboard")
    public String dashboard(Model model) {
        log.info("GET /admin/dashboard - 관리자 대시보드 요청");
        try {
            List<User> userList = adminService.getAllUsers();
            model.addAttribute("users", userList);
            log.info("조회된 사용자 수: {}명", userList.size());

            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication != null) {
                model.addAttribute("loginAdminName", authentication.getName());
            }
            return "admin/dashboard";
        } catch (Exception e) {
            log.error("대시보드 로딩 중 오류 발생", e);
            return "error";
        }
    }

    @PostMapping("/users/{userId}/role")
    public ResponseEntity<?> updateUserRole(@PathVariable Long userId, @RequestParam("role") String role) {
        log.info("POST /users/{}/role - 역할 변경 시도: newRole={}", userId, role);
        try {
            UserRole newRole = UserRole.valueOf(role.toUpperCase());
            adminService.updateUserRole(userId, newRole);
            return ResponseEntity.ok().build();
        } catch (IllegalArgumentException e) {
            log.warn("유효하지 않은 역할 값입니다: {}", role, e);
            return ResponseEntity.badRequest().body("유효하지 않은 역할입니다.");
        } catch (EntityNotFoundException e) {
            log.warn("역할 변경 실패: 사용자를 찾을 수 없습니다. userId={}", userId);
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("역할 변경 중 서버 오류 발생: userId={}", userId, e);
            return ResponseEntity.internalServerError().body("서버 오류가 발생했습니다.");
        }
    }

    @PostMapping("/users/{userId}/withdraw")
    public ResponseEntity<?> withdrawUser(@PathVariable Long userId) {
        log.info("POST /users/{}/withdraw - 사용자 비활성화 시도", userId);
        try {
            adminService.forceWithdrawUser(userId);
            return ResponseEntity.ok().build();
        } catch (EntityNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("사용자 비활성화 중 서버 오류 발생: userId={}", userId, e);
            return ResponseEntity.internalServerError().body("서버 오류가 발생했습니다.");
        }
    }

    @PostMapping("/users/{userId}/restore")
    public ResponseEntity<?> restoreUser(@PathVariable Long userId) {
        log.info("POST /users/{}/restore - 사용자 활성화 시도", userId);
        try {
            adminService.restoreUser(userId);
            return ResponseEntity.ok().build();
        } catch (EntityNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("사용자 활성화 중 서버 오류 발생: userId={}", userId, e);
            return ResponseEntity.internalServerError().body("서버 오류가 발생했습니다.");
        }
    }

    @DeleteMapping("/users/{userId}")
    public ResponseEntity<?> deleteUser(@PathVariable Long userId) {
        log.info("DELETE /users/{} - 사용자 영구 삭제 시도", userId);
        try {
            adminService.deleteUser(userId);
            return ResponseEntity.ok().build();
        } catch (EntityNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("사용자 삭제 중 서버 오류 발생: userId={}", userId, e);
            return ResponseEntity.internalServerError().body("서버 오류가 발생했습니다.");
        }
    }
}

