package com.example.Insurance.Repository;

import com.example.Insurance.Entity.AgeRate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AgeRateRepository extends JpaRepository<AgeRate, Long> {

    @Query("SELECT ar FROM AgeRate ar WHERE ar.ageStart <= :age AND ar.ageEnd >= :age")
    Optional<AgeRate> findRateByAge(@Param("age") int age);
}