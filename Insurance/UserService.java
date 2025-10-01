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

    @Transactional
    public User register(UserRegisterDTO dto) {
        if (userRepository.existsByLoginId(dto.getLoginId())) {
            throw new IllegalArgumentException("이미 사용 중인 아이디입니다.");
        }

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

    public Optional<User> findByLoginIdAndRealNameAndPhone(String loginId, String realName, String phone) {
        log.info("Finding user by loginId={}, realName={}, phone={}", loginId, realName, phone);
        // Repository에도 세 파라미터를 모두 사용하는 메소드가 정의되어 있어야 합니다.
        return userRepository.findByLoginIdAndRealNameAndPhone(loginId, realName, phone);
    }

    @Transactional
    public void resetPassword(String loginId, String newPassword) {
        // 1. 사용자 정보 조회
        User user = userRepository.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalArgumentException("해당 아이디의 사용자를 찾을 수 없습니다: " + loginId));

        // 2. 새로운 비밀번호를 암호화
        String encodedPassword = passwordEncoder.encode(newPassword);

        // 3. 사용자의 비밀번호 업데이트 (User 엔티티에 updatePassword와 같은 메소드가 있다고 가정)
        user.updatePassword(encodedPassword);

        // @Transactional 어노테이션으로 인해 메소드가 종료될 때 변경된 내용이 자동으로 DB에 반영(dirty checking)됩니다.
        // 따라서 userRepository.save(user)를 명시적으로 호출할 필요가 없습니다.
        log.info("비밀번호가 성공적으로 변경되었습니다. loginId={}", loginId);
    }
}