package com.example.Insurance.Entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
@Table(name = "users")
@DynamicInsert
@DynamicUpdate
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

    @Column(columnDefinition = "boolean default true")
    private Boolean isActive;

    @Column(columnDefinition = "boolean default false")
    private Boolean isAdmin;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    // 엔티티가 영속화(persist) 되기 전 실행
    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.isActive = (this.isActive != null) ? this.isActive : true;
        this.isAdmin = (this.isAdmin != null) ? this.isAdmin : false;
    }

    // 엔티티가 업데이트(update) 되기 전 실행
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // [추가] 템플릿에서 {{user.ssnFront}}를 사용할 수 있도록 해주는 메서드
    public String getSsnFront() {
        if (ssn != null && ssn.contains("-")) {
            return ssn.split("-")[0];
        }
        return ""; // ssn이 없거나 형식이 맞지 않으면 빈 문자열 반환
    }

    // [추가] 템플릿에서 {{user.ssnBack}}를 사용할 수 있도록 해주는 메서드
    public String getSsnBack() {
        if (ssn != null && ssn.contains("-")) {
            return ssn.split("-")[1];
        }
        return "";
    }
}