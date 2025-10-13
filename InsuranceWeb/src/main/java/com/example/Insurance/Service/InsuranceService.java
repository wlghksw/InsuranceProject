package com.example.Insurance.Service;

import com.example.Insurance.Entity.Insurance;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.InsuranceRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class InsuranceService {

    private final InsuranceRepository insuranceRepository;

    public InsuranceService(InsuranceRepository insuranceRepository) {
        this.insuranceRepository = insuranceRepository;
    }

    // User 객체로 보험 목록을 조회하는 서비스 메서드
    public List<Insurance> findByUser(User user) {
        return insuranceRepository.findByUser(user);
    }

    // ID와 User 객체로 특정 보험을 조회하는 서비스 메서드
    public Optional<Insurance> findByIdAndUser(Long id, User user) {
        return insuranceRepository.findByIdAndUser(id, user);
    }

    // (기존에 있었을 다른 메서드들...)
}
