package com.example.Insurance.Controller;

import com.example.Insurance.DTO.AccidentRecommendationRequest;
import com.example.Insurance.DTO.AccidentRecommendationResponse;
import com.example.Insurance.Service.AccidentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping("/accident")
public class AccidentController {
    
    @Autowired
    private AccidentService accidentService;
    
    @GetMapping("/recommend")
    public String recommendPage(Model model) {
        model.addAttribute("title", "상해보험 추천");
        return "accident/accident_recommend";
    }
    
    @PostMapping("/recommend/api")
    @ResponseBody
    public AccidentRecommendationResponse getRecommendations(@RequestBody AccidentRecommendationRequest request) {
        return accidentService.getRecommendations(request);
    }
}

