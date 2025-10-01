package com.example.Insurance.Service;

import com.example.Insurance.DTO.UserRegisterDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Optional;

@Slf4j
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class UserService implements UserDetailsService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    // HttpSession 의존성 제거

    // 로그인 메소드 제거 -> 이 역할은 이제 SuccessHandler가 담당합니다.
    /*
    @Transactional
    public void login(LoginRequestDTO loginRequestDto) { ... }
    */

    @Transactional
    public User register(UserRegisterDTO dto) {
        if (userRepository.existsByLoginId(dto.getLoginId())) {
            throw new IllegalArgumentException("이미 사용 중인 아이디입니다.");
        }
        // ... 기존 register 로직 ...
        User user = User.builder()
                .loginId(dto.getLoginId())
                .password(passwordEncoder.encode(dto.getPassword()))
                .realName(dto.getRealName())
                .nickname(dto.getNickname())
                .build();
        return userRepository.save(user);
    }

    public Optional<User> findByLoginId(String loginId) {
        return userRepository.findByLoginId(loginId);
    }

    @Override
    public UserDetails loadUserByUsername(String loginId) throws UsernameNotFoundException {
        User user = userRepository.findByLoginId(loginId)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + loginId));

        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getLoginId())
                .password(user.getPassword())
                .roles(user.getRole().name())
                .disabled(!user.getIsActive())
                .build();
    }

    public Optional<User> findByRealNameAndPhone(String realName, String phone) {
        log.info("Finding user by realName={} and phone={}", realName, phone);
        return userRepository.findByRealNameAndPhone(realName, phone);
    }
}