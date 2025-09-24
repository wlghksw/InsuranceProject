package com.example.Insurance.Repository;

import com.example.Insurance.Entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByLoginId(String loginId);

    Optional<User> findByNickname(String nickname);

    boolean existsByLoginId(String loginId);

    boolean existsByNickname(String nickname);

    boolean existsByPhone(String phone);

    Optional<User> findByRealNameAndPhoneAndBirthYear(String realName, String phone, Integer birthYear);

    Optional<User> findByRealNameAndPhone(String realName, String phone);

    Optional<User> findByRealNameAndSsn(String realName, String ssn);
}
