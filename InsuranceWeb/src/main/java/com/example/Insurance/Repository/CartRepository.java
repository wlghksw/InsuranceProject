package com.example.Insurance.Repository;

import com.example.Insurance.Entity.Cart;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CartRepository extends JpaRepository<Cart, Long> {
    // 사용자 ID로 장바구니 조회
    List<Cart> findByUserIdOrderByAddedAtDesc(Long userId);
    
    // 중복 체크 (같은 사용자가 같은 상품을 담았는지)
    Optional<Cart> findByUserIdAndInsuranceTypeAndProductName(Long userId, String insuranceType, String productName);
    
    // 사용자의 특정 보험 타입 장바구니 조회
    List<Cart> findByUserIdAndInsuranceTypeOrderByAddedAtDesc(Long userId, String insuranceType);
    
    // 사용자의 장바구니 개수
    Long countByUserId(Long userId);
}


