package com.example.Insurance.Config;

import jakarta.servlet.http.HttpSession;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
        // 필요하면: return PasswordEncoderFactories.createDelegatingPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http,
            ClientRegistrationRepository clientRegistrationRepository
    ) throws Exception {

        DefaultOAuth2AuthorizationRequestResolver baseResolver =
                new DefaultOAuth2AuthorizationRequestResolver(
                        clientRegistrationRepository, "/oauth2/authorization");

        baseResolver.setAuthorizationRequestCustomizer(customizer ->
                customizer.additionalParameters(params -> params.put("prompt", "login")));

        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/", "/main", "/login/**", "/css/**", "/js/**", "/images/**").permitAll()
                        .requestMatchers("/codef/**").permitAll()
                        .anyRequest().authenticated()
                )
                .oauth2Login(oauth -> oauth
                        .loginPage("/")
                        .authorizationEndpoint(ae -> ae.authorizationRequestResolver(baseResolver))
                        .successHandler((request, response, authentication) -> {
                            Object principal = authentication.getPrincipal();
                            if (principal instanceof OAuth2User user) {
                                System.out.println("[KAKAO OAUTH SUCCESS] id=" + user.getAttribute("id"));
                                System.out.println("[KAKAO OAUTH SUCCESS] attrs=" + user.getAttributes());
                            }
                            response.sendRedirect("/login/success");
                        })
                        .failureHandler((request, response, exception) -> {
                            String msg = exception.getClass().getSimpleName() + " - " + exception.getMessage();
                            System.err.println("[KAKAO OAUTH ERROR] " + msg);
                            HttpSession session = request.getSession();
                            session.setAttribute("oauthError", msg);
                            response.sendRedirect("/login/failure");
                        })
                )
                .logout(lo -> lo.logoutSuccessUrl("/"));

        return http.build();
    }
}
