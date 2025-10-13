package com.example.Insurance.Service;

import com.example.Insurance.DTO.CartRequest;
import com.example.Insurance.Entity.Cart;
import com.example.Insurance.Repository.CartRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class CartService {

    private final CartRepository cartRepository;

    /**
     * 관심 상품에 추가
     */
    @Transactional
    public Cart addToCart(Long userId, CartRequest request) {
        // 중복 체크
        Optional<Cart> existing = cartRepository.findByUserIdAndInsuranceTypeAndProductName(
                userId, request.getInsuranceType(), request.getProductName()
        );

        if (existing.isPresent()) {
            throw new IllegalStateException("이미 관심 상품에 추가된 상품입니다.");
        }

        Cart cart = Cart.builder()
                .userId(userId)
                .insuranceType(request.getInsuranceType())
                .insuranceCompany(request.getInsuranceCompany())
                .productName(request.getProductName())
                .coverageAmount(request.getCoverageAmount())
                .malePremium(request.getMalePremium())
                .femalePremium(request.getFemalePremium())
                .monthlyPremium(request.getMonthlyPremium())
                .guaranteedRate(request.getGuaranteedRate())
                .currentRate(request.getCurrentRate())
                .renewalCycle(request.getRenewalCycle())
                .term(request.getTerm())
                .paymentMethod(request.getPaymentMethod())
                .salesChannel(request.getSalesChannel())
                .recommendationReason(request.getRecommendationReason())
                .build();

        return cartRepository.save(cart);
    }

    /**
     * 사용자의 전체 관심 상품 조회
     */
    public List<Cart> getCartByUserId(Long userId) {
        return cartRepository.findByUserIdOrderByAddedAtDesc(userId);
    }

    /**
     * 사용자의 특정 보험 타입 관심 상품 조회
     */
    public List<Cart> getCartByUserIdAndType(Long userId, String insuranceType) {
        return cartRepository.findByUserIdAndInsuranceTypeOrderByAddedAtDesc(userId, insuranceType);
    }

    /**
     * 관심 상품에서 삭제
     */
    @Transactional
    public void removeFromCart(Long cartId, Long userId) {
        Cart cart = cartRepository.findById(cartId)
                .orElseThrow(() -> new IllegalArgumentException("관심 상품을 찾을 수 없습니다."));

        // 본인의 관심 상품인지 확인
        if (!cart.getUserId().equals(userId)) {
            throw new IllegalStateException("본인의 관심 상품만 삭제할 수 있습니다.");
        }

        cartRepository.delete(cart);
    }

    /**
     * 관심 상품 개수 조회
     */
    public Long getCartCount(Long userId) {
        return cartRepository.countByUserId(userId);
    }

    /**
     * 관심 상품 전체 비우기
     */
    @Transactional
    public void clearCart(Long userId) {
        List<Cart> cartItems = cartRepository.findByUserIdOrderByAddedAtDesc(userId);
        cartRepository.deleteAll(cartItems);
    }
}

