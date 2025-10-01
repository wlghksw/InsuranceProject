package com.example.Insurance.Repository;

import com.example.Insurance.Entity.Insurance;
import com.example.Insurance.Entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface InsuranceRepository extends JpaRepository<Insurance, Long> {

    // 1. User 객체로 해당 사용자의 모든 보험 목록을 찾는 메서드
    List<Insurance> findByUser(User user);

    // 2. 보험 ID와 User 객체로 해당 사용자의 특정 보험을 찾는 메서드 (보안용)
    Optional<Insurance> findByIdAndUser(Long id, User user);
}