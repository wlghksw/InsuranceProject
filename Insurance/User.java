package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor(access = AccessLevel.PRIVATE)
@Builder
@EqualsAndHashCode(of = "id")
@ToString(exclude = {"password", "ssn"})
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

    @Column(unique = true)
    private String ssn;

    @Builder.Default
    @Column(nullable = false)
    private Boolean isActive = true;

    @Enumerated(EnumType.STRING)
    @Builder.Default
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

    public void updateProfile(String nickname, String phone, String profileImage) {
        this.nickname = nickname;
        this.phone = phone;
        this.profileImage = profileImage;
    }

    public void updateRole(UserRole role) {
        this.role = role;
    }

    public void updateStatus(boolean isActive) {
        this.isActive = isActive;
    }

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

    public void updatePassword(String newPassword) {
        this.password = newPassword;
    }
}