package com.example.Insurance.Config;

import com.example.Insurance.Entity.User;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.ArrayList;
import java.util.Collection;

public class CustomUserDetails implements UserDetails {

    private final User user;

    public CustomUserDetails(User user) {
        this.user = user;
    }

    // 현재 사용자의 User 엔티티를 반환
    public User getUser() {
        return user;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // 현재는 역할(Role) 기반 권한 관리를 사용하지 않으므로 비워둡니다.
        // 만약 ROLE_USER, ROLE_ADMIN 같은 권한을 사용한다면 여기에 로직을 추가해야 합니다.
        Collection<GrantedAuthority> authorities = new ArrayList<>();
        // 예: authorities.add(() -> "ROLE_USER");
        return authorities;
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        // Spring Security에서 username은 ID를 의미합니다.
        return user.getLoginId();
    }

    // 계정이 만료되지 않았는가?
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    // 계정이 잠기지 않았는가?
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    // 자격 증명(비밀번호)이 만료되지 않았는가?
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    // 계정이 활성화되었는가?
    @Override
    public boolean isEnabled() {
        return user.getIsActive();
    }
}
