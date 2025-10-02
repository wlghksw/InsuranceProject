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
                        .successHandler(customLoginSuccessHandler)
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

    @Bean
    public AuthenticationSuccessHandler customLoginSuccessHandler(UserRepository userRepository, HttpSession httpSession) {
      
        return new SavedRequestAwareAuthenticationSuccessHandler() {
            @Override
            public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws java.io.IOException, jakarta.servlet.ServletException {
                
                UserDetails userDetails = (UserDetails) authentication.getPrincipal();
                String loginId = userDetails.getUsername();
                
                User user = userRepository.findByLoginId(loginId)
                        .orElseThrow(() -> new IllegalStateException("인증된 사용자를 DB에서 찾을 수 없습니다."));

                httpSession.setAttribute("user", new SessionUserDTO(user));

                boolean isAdmin = authentication.getAuthorities().stream()
                        .map(GrantedAuthority::getAuthority)
                        .anyMatch(role -> role.equals("ROLE_ADMIN"));

                if (isAdmin) {
                    setDefaultTargetUrl("/admin/dashboard");
                } else {
                    setDefaultTargetUrl("/main");
                }

                super.onAuthenticationSuccess(request, response, authentication);
            }
        };
    }

}
