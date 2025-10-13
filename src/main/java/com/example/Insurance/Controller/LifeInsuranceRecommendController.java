package com.example.Insurance.Controller;

import com.example.Insurance.DTO.LifeInsuranceRecommendDTO;
import com.example.Insurance.Service.LifeInsuranceRecommendService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
@RequestMapping("/life")
public class LifeInsuranceRecommendController {

    private final LifeInsuranceRecommendService service;

    @GetMapping("/recommend")
    public String lifeRecommendPage() {
        return "life/recommend";
    }

    @PostMapping("/recommend")
    @ResponseBody
    public LifeInsuranceRecommendDTO.Response recommend(
            @Valid @RequestBody LifeInsuranceRecommendDTO.Request req) {
        return service.recommend(req);
    }

    @GetMapping("/health")
    @ResponseBody
    public String health() { return "ok"; }
}
