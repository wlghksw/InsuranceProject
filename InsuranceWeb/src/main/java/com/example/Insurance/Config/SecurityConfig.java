package com.example.Insurance.Config;

import com.example.Insurance.Service.CustomUserDetailsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final CustomUserDetailsService customUserDetailsService;

    public SecurityConfig(CustomUserDetailsService customUserDetailsService) {
        this.customUserDetailsService = customUserDetailsService;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests(authorize -> authorize
                        // 메인 페이지와 일부 정적 자원(CSS, JS 등)은 로그인 없이 접근 허용
                        .requestMatchers("/", "/main", "/css/**", "/js/**", "/images/**","/service_intro","/notice","/user/find_id").permitAll()
                        // 로그인 및 회원가입 페이지에 대한 접근 허용
                        .requestMatchers("/user/login", "/user/register").permitAll()
                        // 추천 API는 익명 접근 허용
                        .requestMatchers("/cancer/recommend", "/cancer/recommend/api", "/cancer/profile-recommend", "/cancer/profile-recommend/api").permitAll()
                        .requestMatchers("/savings/recommend", "/savings/recommend/api", "/savings/profile-recommend", "/savings/profile-recommend/api").permitAll()
                        // 내 보험찾기 URL은 로그인 후 접근 가능하도록 설정
                        .requestMatchers("/user/my_insurance/**").authenticated()
                        // 그 외 모든 요청은 인증 필요
                        .anyRequest().authenticated()
                )
                .formLogin(form -> form
                        .loginPage("/user/login")
                        .loginProcessingUrl("/user/login")
                        .defaultSuccessUrl("/main", true)
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/main")
                        .permitAll()
                )
                .csrf(csrf -> csrf.disable());

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public DaoAuthenticationProvider daoAuthenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(customUserDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }
}