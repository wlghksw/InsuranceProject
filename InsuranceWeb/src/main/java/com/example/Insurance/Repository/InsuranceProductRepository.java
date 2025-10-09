package com.example.Insurance.Repository;

import com.example.Insurance.Entity.InsuranceProduct;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface InsuranceProductRepository extends JpaRepository<InsuranceProduct, Long> {
    
    // 상품 유형별 조회
    List<InsuranceProduct> findByProductType(String productType);
    
    // 보험사별 조회
    List<InsuranceProduct> findByInsuranceCompany(String insuranceCompany);
}



