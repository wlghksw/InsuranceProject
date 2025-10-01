package com.example.Insurance.Config;

import com.example.Insurance.DTO.SessionUserDTO;
import com.example.Insurance.Entity.User;
import com.example.Insurance.Repository.UserRepository;
import com.example.Insurance.Service.UserService;
import com.example.Insurance.DTO.SessionUserDTO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.authentication.SavedRequestAwareAuthenticationSuccessHandler;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final UserService userService;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, AuthenticationSuccessHandler customLoginSuccessHandler) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers("/", "/main", "/user/**", "/calculator", "/api/calculate", "/css/**", "/js/**", "/images/**", "/service_intro", "/h2-console/**", "/user/my_insurance/**", "/user/verify-account", "/user/reset-password").permitAll()
                        .requestMatchers("/admin/**").hasRole("ADMIN").anyRequest().authenticated()
                )

                .formLogin(form -> form
                        .loginPage("/user/login")
                        .loginProcessingUrl("/user/login")
                        .successHandler(customLoginSuccessHandler) // Bean으로 등록된 핸들러 사용
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/")
                        .invalidateHttpSession(true)
                        .deleteCookies("JSESSIONID")
                        .permitAll()
                );

        return http.build();
    }

    @Bean
    public static PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public DaoAuthenticationProvider daoAuthenticationProvider(PasswordEncoder passwordEncoder) {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userService);
        provider.setPasswordEncoder(passwordEncoder);
        return provider;
    }

    // 2. 기존 람다 핸들러를 세션 저장 기능이 포함된 완전한 핸들러로 교체
    @Bean
    public AuthenticationSuccessHandler customLoginSuccessHandler(UserRepository userRepository, HttpSession httpSession) {
        // SavedRequestAwareAuthenticationSuccessHandler를 상속하여 기본 세션 관리 기능 사용
        return new SavedRequestAwareAuthenticationSuccessHandler() {
            @Override
            public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws java.io.IOException, jakarta.servlet.ServletException {
                // 1. 인증된 사용자 정보 가져오기
                UserDetails userDetails = (UserDetails) authentication.getPrincipal();
                String loginId = userDetails.getUsername();

                // 2. DB에서 User 엔티티 조회
                User user = userRepository.findByLoginId(loginId)
                        .orElseThrow(() -> new IllegalStateException("인증된 사용자를 DB에서 찾을 수 없습니다."));

                // 3. (핵심) 세션에 SessionUser DTO 저장
                httpSession.setAttribute("user", new SessionUserDTO(user));

                // 4. 역할 기반 리다이렉트 로직
                boolean isAdmin = authentication.getAuthorities().stream()
                        .map(GrantedAuthority::getAuthority)
                        .anyMatch(role -> role.equals("ROLE_ADMIN"));

                if (isAdmin) {
                    setDefaultTargetUrl("/admin/dashboard");
                } else {
                    setDefaultTargetUrl("/main");
                }

                // 5. 최종 리다이렉트 실행
                super.onAuthenticationSuccess(request, response, authentication);
            }
        };
    }
}