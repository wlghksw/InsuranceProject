package com.example.Insurance.Controller;

import com.example.Insurance.DTO.InsuranceProductRequest;
import com.example.Insurance.Entity.InsuranceProduct;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Entity.UserRole;
import com.example.Insurance.Service.AdminService;
import com.example.Insurance.Service.InsuranceProductService;
import jakarta.persistence.EntityNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;

@Controller
@RequestMapping("/admin")
public class AdminController {

    private static final Logger log = LoggerFactory.getLogger(AdminController.class);
    private final AdminService adminService;
    private final InsuranceProductService productService;

    public AdminController(AdminService adminService, InsuranceProductService productService) {
        this.adminService = adminService;
        this.productService = productService;
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

    /**
     * [핵심 추가] 사용자를 강제 탈퇴(비활성화)시키는 API
     * @param userId 대상 사용자의 ID
     * @return 성공/실패 응답
     */
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

    /**
     * [핵심 추가] 비활성화된 사용자를 복구(활성화)시키는 API
     * @param userId 대상 사용자의 ID
     * @return 성공/실패 응답
     */
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

    /**
     * [핵심 추가] 사용자를 영구적으로 삭제하는 API
     * @param userId 대상 사용자의 ID
     * @return 성공/실패 응답
     */
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

    // ========== 보험 상품 관리 ==========

    /**
     * 보험 상품 등록 페이지
     */
    @GetMapping("/products/new")
    public String newProductPage(Model model) {
        log.info("GET /admin/products/new - 보험 상품 등록 페이지 요청");
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null) {
            model.addAttribute("loginAdminName", authentication.getName());
        }
        return "admin/product_add";
    }

    /**
     * 보험 상품 목록 페이지
     */
    @GetMapping("/products")
    public String productsPage(Model model) {
        log.info("GET /admin/products - 보험 상품 목록 페이지 요청");
        List<InsuranceProduct> products = productService.getAllProducts();
        model.addAttribute("products", products);
        
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null) {
            model.addAttribute("loginAdminName", authentication.getName());
        }
        return "admin/product_list";
    }

    /**
     * 보험 상품 등록 API
     */
    @PostMapping("/products")
    public String addProduct(@ModelAttribute InsuranceProductRequest request, 
                            RedirectAttributes redirectAttributes) {
        log.info("POST /admin/products - 보험 상품 등록: {}", request.getProductName());
        try {
            InsuranceProduct savedProduct = productService.addProduct(request);
            log.info("보험 상품 등록 완료: ID={}, 상품명={}", savedProduct.getId(), savedProduct.getProductName());
            redirectAttributes.addFlashAttribute("message", "상품이 성공적으로 등록되었습니다!");
            redirectAttributes.addFlashAttribute("messageType", "success");
            return "redirect:/admin/products";
        } catch (Exception e) {
            log.error("보험 상품 등록 중 오류 발생", e);
            redirectAttributes.addFlashAttribute("message", "상품 등록 중 오류가 발생했습니다: " + e.getMessage());
            redirectAttributes.addFlashAttribute("messageType", "danger");
            return "redirect:/admin/products/new";
        }
    }

    /**
     * 보험 상품 삭제 API
     */
    @DeleteMapping("/products/{productId}")
    @ResponseBody
    public ResponseEntity<?> deleteProduct(@PathVariable Long productId) {
        log.info("DELETE /admin/products/{} - 보험 상품 삭제 시도", productId);
        try {
            productService.deleteProduct(productId);
            log.info("보험 상품 삭제 완료: ID={}", productId);
            return ResponseEntity.ok().build();
        } catch (IllegalArgumentException e) {
            log.warn("상품 삭제 실패: {}", e.getMessage());
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("상품 삭제 중 오류 발생", e);
            return ResponseEntity.internalServerError().body("서버 오류가 발생했습니다.");
        }
    }
}

