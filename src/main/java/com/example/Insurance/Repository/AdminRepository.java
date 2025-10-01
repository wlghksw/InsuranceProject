package com.example.Insurance.Repository;

import com.example.Insurance.Entity.Insurance;
import com.example.Insurance.Entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AdminRepository extends JpaRepository<Insurance, Long> {

    Optional<User> findByIdAndUser(Long id, User user);
}
