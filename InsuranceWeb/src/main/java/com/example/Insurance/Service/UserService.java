package com.example.Insurance.Service;

import com.example.Insurance.DTO.UserRegisterDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Entity.UserRole;
import com.example.Insurance.Repository.UserRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class UserService implements UserDetailsService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;

    public UserService(PasswordEncoder passwordEncoder, UserRepository userRepository) {
        this.passwordEncoder = passwordEncoder;
        this.userRepository = userRepository;
    }

    @Transactional
    public User register(UserRegisterDTO dto) { // [개선] 생성된 User 객체를 반환하도록 변경
        if (userRepository.existsByLoginId(dto.getLoginId())) {
            throw new IllegalArgumentException("이미 사용 중인 아이디입니다.");
        }

        Integer birthYear;
        try {
            birthYear = Integer.parseInt(dto.getBirthYear());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("유효한 출생 연도를 입력해주세요.");
        }

        User user = User.builder()
                .loginId(dto.getLoginId())
                .password(passwordEncoder.encode(dto.getPassword()))
                .realName(dto.getRealName())
                .nickname(dto.getNickname())
                .phone(dto.getPhone())
                .birthYear(birthYear)
                .gender(dto.getGender())
                .role(UserRole.USER)
                .isActive(true) // [개선] 명시적으로 활성 상태로 생성
                .build();

        return userRepository.save(user); // [개선] 저장된 객체 반환
    }

    // [이름 변경] getUserByLoginId -> findByLoginId
    public Optional<User> findByLoginId(String loginId) {
        return userRepository.findByLoginId(loginId);
    }

    // 이 메서드는 더 이상 필요하지 않아 주석 처리 또는 삭제 가능
    /*
    public String findLoginId(String realName, String phone, Integer birthYear) {
        return userRepository.findByRealNameAndPhoneAndBirthYear(realName, phone, birthYear)
                .map(User::getLoginId)
                .orElse(null);
    }
    */

    public Optional<User> findByRealNameAndPhone(String realName, String phone) {
        return userRepository.findByRealNameAndPhone(realName, phone);
    }

    public Optional<User> findByRealNameAndSsn(String realName, String ssn) {
        return userRepository.findByRealNameAndSsn(realName, ssn);
    }

    public List<User> findAllUsers() {
        return userRepository.findAll();
    }

    @Override
    public UserDetails loadUserByUsername(String loginId) throws UsernameNotFoundException {
        User user = userRepository.findByLoginId(loginId)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + loginId));

        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getLoginId())
                .password(user.getPassword())
                .roles(user.getRole().name())
                .disabled(!user.getIsActive()) // [✅ 핵심 수정] 계정 활성화 상태 체크 로직 추가
                .build();
    }
}