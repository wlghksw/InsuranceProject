package com.example.Insurance.Config;

import com.example.Insurance.Service.UserService;
import jakarta.servlet.http.HttpSession;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;

@Configuration
public class SecurityConfig {

    private final UserService userService;

    public SecurityConfig(UserService userService) {
        this.userService = userService;
    }

    // 비밀번호 인코더
    @Bean
    public static PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // DAO 인증 프로바이더 (UserService = UserDetailsService)
    @Bean
    public DaoAuthenticationProvider daoAuthenticationProvider(PasswordEncoder passwordEncoder) {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userService);
        provider.setPasswordEncoder(passwordEncoder);
        return provider;
    }

    // 폼 로그인 성공 시 역할 기반 리다이렉트
    @Bean
    public AuthenticationSuccessHandler customLoginSuccessHandler() {
        return (request, response, authentication) -> {
            boolean isAdmin = authentication.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .anyMatch(role -> role.equals("ROLE_ADMIN"));
            response.sendRedirect(isAdmin ? "/admin/dashboard" : "/main");
        };
    }

    // 단일 SecurityFilterChain (폼로그인 + OAuth2 통합)
    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http,
            ClientRegistrationRepository clientRegistrationRepository,
            AuthenticationSuccessHandler customLoginSuccessHandler,
            DaoAuthenticationProvider daoAuthenticationProvider
    ) throws Exception {

        // 카카오 권한창 매번 띄우기 (prompt=login)
        DefaultOAuth2AuthorizationRequestResolver baseResolver =
                new DefaultOAuth2AuthorizationRequestResolver(
                        clientRegistrationRepository, "/oauth2/authorization");
        baseResolver.setAuthorizationRequestCustomizer(customizer ->
                customizer.additionalParameters(params -> params.put("prompt", "login")));

        http
                // H2 콘솔/iframe 허용 & CSRF 비활성화(필요 시 토큰 적용 고려)
                .csrf(csrf -> csrf.disable())
                .headers(h -> h.frameOptions(frame -> frame.sameOrigin()))

                // URL 접근 권한
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/", "/main", "/home",
                                "/login/**", "/oauth2/**",
                                "/css/**", "/js/**", "/images/**",
                                "/service_intro", "/notice",
                                "/user/find_id", "/user/register",
                                "/savings/recommend", "/accident/recommend",
                                "/cancer/recommend", "/cancer/profile-recommend",
                                "/life/recommend",
                                "/calculator", "/api/calculate",
                                "/accident/recommend/api", "/cancer/recommend/api",
                                "/cancer/profile-recommend/api",
                                "/savings-insurance/recommend/api",
                                "/chatbot", "/chatbot/ask",
                                "/codef/**",
                                "/h2-console/**").permitAll()
                        .requestMatchers("/admin/**").hasRole("ADMIN")
                        .requestMatchers("/cart/**",
                                "/user/myPage", "/user/my_insurance/**").authenticated()
                        .anyRequest().authenticated()
                )

                // 폼 로그인
                .formLogin(form -> form
                        .loginPage("/user/login")
                        .loginProcessingUrl("/user/login")
                        .successHandler(customLoginSuccessHandler)
                        .permitAll()
                )

                // OAuth2 로그인 (카카오)
                .oauth2Login(oauth -> oauth

                        .loginPage("/user/login")
                        .authorizationEndpoint(ae -> ae.authorizationRequestResolver(baseResolver))
                        .successHandler((request, response, authentication) -> {
                            Object principal = authentication.getPrincipal();
                            if (principal instanceof OAuth2User user) {
                                System.out.println("[KAKAO OAUTH SUCCESS] id=" + user.getAttribute("id"));
                                System.out.println("[KAKAO OAUTH SUCCESS] attrs=" + user.getAttributes());
                            }

                            response.sendRedirect("/main");
                        })
                        .failureHandler((request, response, exception) -> {
                            String msg = exception.getClass().getSimpleName() + " - " + exception.getMessage();
                            System.err.println("[KAKAO OAUTH ERROR] " + msg);
                            HttpSession session = request.getSession();
                            session.setAttribute("oauthError", msg);
                            response.sendRedirect("/user/login?error=oauth");
                        })
                )


                .logout(lo -> lo
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/main")
                        .permitAll()
                )


                .authenticationProvider(daoAuthenticationProvider);

        return http.build();
    }
}
