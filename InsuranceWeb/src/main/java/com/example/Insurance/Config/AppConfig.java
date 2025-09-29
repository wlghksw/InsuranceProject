// src/main/java/com/example/Insurance/config/AppConfig.java

package com.example.Insurance.Config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {

    /**
     * 외부 API를 호출하기 위한 RestTemplate 객체를 Spring Bean으로 등록합니다.
     * 이제부터 다른 서비스에서 RestTemplate이 필요할 때마다 Spring이 이 객체를 자동으로 전달해줍니다.
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    /**
     * JSON 데이터를 Java 객체로 변환하기 위한 ObjectMapper 객체를 Spring Bean으로 등록합니다.
     */
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}