// src/main/java/com/example/Insurance/Controller/AccidentController.java

package com.example.Insurance.Controller;

import com.example.Insurance.DTO.AccidentRecommendationRequest;
import com.example.Insurance.DTO.AccidentRecommendationResponse;
import com.example.Insurance.Service.AccidentService;
import lombok.extern.slf4j.Slf4j; // Slf4j import 추가
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.Model;

@Slf4j // ◀◀◀ 롬복(Lombok) 로깅 어노테이션 추가
@Controller
@RequestMapping("/accident")
public class AccidentController {

    @Autowired
    private AccidentService accidentService;

    @GetMapping("/recommend")
    public String recommendPage() {
        return "accident/accident_recommend";
    }

    @PostMapping("/recommend/api")
    @ResponseBody
    public AccidentRecommendationResponse getRecommendations(@RequestBody AccidentRecommendationRequest request) {
        // ▼▼▼ 여기에 로그 추가 ▼▼▼
        log.info("API 요청 받음: /accident/recommend/api, 요청내용: {}", request.toString()); // 요청 내용 확인

        AccidentRecommendationResponse response = accidentService.getAccidentRecommendations(request);

        log.info("API 응답 보냄: 상품 {}개 추천", response.getTotalProducts());

        return response;
    }
}