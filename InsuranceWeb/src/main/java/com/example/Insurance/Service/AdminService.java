package com.example.Insurance.Service;

import com.example.Insurance.Entity.User;
import com.example.Insurance.Entity.UserRole;
import com.example.Insurance.Repository.UserRepository;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class AdminService {

    private final UserRepository userRepository;

    public AdminService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Transactional
    public void deleteUser(Long userId) {
        if (!userRepository.existsById(userId)) {
            throw new EntityNotFoundException("해당 ID의 사용자를 찾을 수 없습니다: " + userId);
        }
        userRepository.deleteById(userId);
    }

    /**
     * 사용자의 역할을 변경합니다.
     */
    @Transactional
    public void updateUserRole(Long userId, UserRole role) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("해당 ID의 사용자를 찾을 수 없습니다: " + userId));

        user.updateRole(role); // [수정] user.setRole() -> user.updateRole()
    }

    /**
     * 사용자를 비활성 상태로 변경합니다.
     */
    @Transactional
    public void forceWithdrawUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("해당 ID의 사용자를 찾을 수 없습니다: " + userId));

        user.updateStatus(false); // [수정] user.setIsActive(false) -> user.updateStatus(false)
    }


    /**
     * 사용자를 활성 상태로 복구합니다.
     */
    @Transactional
    public void restoreUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new EntityNotFoundException("해당 ID의 사용자를 찾을 수 없습니다: " + userId));

        user.updateStatus(true); // [수정] user.setIsActive(true) -> user.updateStatus(true)
    }
}



