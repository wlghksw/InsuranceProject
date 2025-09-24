package com.example.Insurance.Service;

import com.example.Insurance.DTO.UserDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class UserService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;

    public UserService(PasswordEncoder passwordEncoder, UserRepository userRepository) {
        this.passwordEncoder = passwordEncoder;
        this.userRepository = userRepository;
    }

    @Transactional
    public void register(UserDTO dto) {
        // 아이디 중복 검사
        if (userRepository.existsByLoginId(dto.getLoginId())) {
            // [개선] 더 구체적인 예외를 사용하여 컨트롤러에서 처리하기 용이하게 만듭니다.
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
                .isActive(true)
                .isAdmin(false)
                .build();

        userRepository.save(user);
    }

    public Optional<User> getUserByLoginId(String loginId) {
        return userRepository.findByLoginId(loginId);
    }

    public String findLoginId(String realName, String phone, Integer birthYear) {
        return userRepository.findByRealNameAndPhoneAndBirthYear(realName, phone, birthYear)
                .map(User::getLoginId)
                .orElse(null);
    }

    public Optional<User> findByRealNameAndPhone(String realName, String phone) {
        return userRepository.findByRealNameAndPhone(realName, phone);
    }

    public Optional<User> findByRealNameAndSsn(String realName, String ssn) {
        return userRepository.findByRealNameAndSsn(realName, ssn);
    }
}