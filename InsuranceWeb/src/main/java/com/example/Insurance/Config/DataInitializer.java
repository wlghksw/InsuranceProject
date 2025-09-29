package com.example.Insurance.Config;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Entity.UserRole;
import com.example.Insurance.Repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // 관리자 계정이 이미 존재하는지 확인
        if (userRepository.existsByLoginId("admin")) {
            System.out.println("✅ 관리자 계정이 이미 존재합니다.");
            return;
        }

        // 기본 관리자 계정 생성
        User admin = User.builder()
                .loginId("admin")
                .password(passwordEncoder.encode("123"))
                .realName("관리자")
                .nickname("관리자")
                .role(UserRole.ADMIN)
                .isActive(true)
                .build();

        userRepository.save(admin);
        System.out.println("🎉 기본 관리자 계정이 생성되었습니다!");
        System.out.println("   아이디: admin");
        System.out.println("   비밀번호: 123");
        System.out.println("   권한: ADMIN");
    }
}
