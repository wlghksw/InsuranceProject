package com.example.Insurance.Controller;

import com.example.Insurance.DTO.CartRequest;
import com.example.Insurance.Entity.Cart;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import com.example.Insurance.Service.CartService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class CartController {

    private final CartService cartService;
    private final UserRepository userRepository;

    /**
     * 관심 상품 페이지
     */
    @GetMapping("/cart")
    public String cartPage(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        if (userDetails == null) {
            return "redirect:/user/login";
        }

        User user = userRepository.findByLoginId(userDetails.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

        List<Cart> cartItems = cartService.getCartByUserId(user.getId());
        model.addAttribute("user", user);
        model.addAttribute("cartItems", cartItems);
        model.addAttribute("cartCount", cartItems.size());

        return "user/cart";
    }

    /**
     * 관심 상품에 추가 (AJAX)
     */
    @PostMapping("/cart/add")
    @ResponseBody
    public ResponseEntity<?> addToCart(@AuthenticationPrincipal UserDetails userDetails,
                                       @RequestBody CartRequest request) {
        try {
            if (userDetails == null) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "로그인이 필요합니다."));
            }

            User user = userRepository.findByLoginId(userDetails.getUsername())
                    .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

            Cart cart = cartService.addToCart(user.getId(), request);
            Long cartCount = cartService.getCartCount(user.getId());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "관심 상품에 추가했습니다!");
            response.put("cartCount", cartCount);

            return ResponseEntity.ok(response);
        } catch (IllegalStateException e) {
            return ResponseEntity.ok(Map.of("success", false, "message", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("success", false, "message", "오류가 발생했습니다: " + e.getMessage()));
        }
    }

    /**
     * 관심 상품에서 삭제 (AJAX)
     */
    @DeleteMapping("/cart/{cartId}")
    @ResponseBody
    public ResponseEntity<?> removeFromCart(@PathVariable Long cartId,
                                            @AuthenticationPrincipal UserDetails userDetails) {
        try {
            if (userDetails == null) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "로그인이 필요합니다."));
            }

            User user = userRepository.findByLoginId(userDetails.getUsername())
                    .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

            cartService.removeFromCart(cartId, user.getId());
            Long cartCount = cartService.getCartCount(user.getId());

            return ResponseEntity.ok(Map.of("success", true, "message", "삭제되었습니다.", "cartCount", cartCount));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("success", false, "message", e.getMessage()));
        }
    }

    /**
     * 관심 상품 개수 조회 (AJAX)
     */
    @GetMapping("/cart/count")
    @ResponseBody
    public ResponseEntity<?> getCartCount(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.ok(Map.of("count", 0));
        }

        User user = userRepository.findByLoginId(userDetails.getUsername())
                .orElse(null);

        if (user == null) {
            return ResponseEntity.ok(Map.of("count", 0));
        }

        Long count = cartService.getCartCount(user.getId());
        return ResponseEntity.ok(Map.of("count", count));
    }

    /**
     * 관심 상품 전체 비우기
     */
    @DeleteMapping("/cart/clear")
    @ResponseBody
    public ResponseEntity<?> clearCart(@AuthenticationPrincipal UserDetails userDetails) {
        try {
            if (userDetails == null) {
                return ResponseEntity.status(401).body(Map.of("success", false, "message", "로그인이 필요합니다."));
            }

            User user = userRepository.findByLoginId(userDetails.getUsername())
                    .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

            cartService.clearCart(user.getId());
            return ResponseEntity.ok(Map.of("success", true, "message", "관심 상품이 비워졌습니다."));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("success", false, "message", e.getMessage()));
        }
    }
}

