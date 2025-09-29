package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED) // JPA를 위한 기본 생성자
@AllArgsConstructor(access = AccessLevel.PRIVATE) // Builder를 통한 생성만 허용
@Builder
@EqualsAndHashCode(of = "id") // [보완] id를 기준으로 엔티티의 동등성을 비교
@ToString(exclude = {"password", "ssn"}) // [보완] 로그 출력 시 민감 정보 제외
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String loginId;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String realName;

    private String nickname;

    private String phone;

    private Integer birthYear;

    private String gender;

    private String profileImage;

    // [보안] 주민번호와 같은 민감 정보는 암호화하여 저장하는 것을 권장합니다.
    @Column(unique = true)
    private String ssn;

    @Builder.Default // [보완] Builder 사용 시 기본값을 true로 설정
    @Column(nullable = false)
    private Boolean isActive = true;

    @Enumerated(EnumType.STRING)
    @Builder.Default // [보완] Builder 사용 시 기본 역할을 USER로 설정
    @Column(nullable = false)
    private UserRole role = UserRole.USER;

    @Column(updatable = false, nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    //== 비즈니스 로직 (수정 메서드) ==//

    /**
     * [보완] 사용자 프로필 정보 수정
     */
    public void updateProfile(String nickname, String phone, String profileImage) {
        this.nickname = nickname;
        this.phone = phone;
        this.profileImage = profileImage;
    }

    /**
     * [보완] 관리자에 의한 사용자 역할 변경
     */
    public void updateRole(UserRole role) {
        this.role = role;
    }

    /**
     * [보완] 관리자에 의한 사용자 상태 변경 (활성/비활성)
     */
    public void updateStatus(boolean isActive) {
        this.isActive = isActive;
    }


    //== 조회용 편의 메서드 ==//

    public String getSsnFront() {
        if (ssn != null && ssn.contains("-")) {
            return ssn.split("-")[0];
        }
        return "";
    }

    public String getSsnBack() {
        if (ssn != null && ssn.contains("-")) {
            return ssn.split("-")[1];
        }
        return "";
    }

    public boolean isAdmin() {
        return this.role == UserRole.ADMIN;
    }
}