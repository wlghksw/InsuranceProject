package com.example.Insurance.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ClassifyController {

    @GetMapping("/classify")
    public String setclassifyPage() {
        return "classify";
    }

    @GetMapping("/classify/medical_classify")
    public String medical_classifyPage() {
        return "classify/medical_classify";
    }

    @GetMapping("/classify/cancer_classify")
    public String cancer_classifyPage() {
        return "classify/cancer_classify";
    }

    @GetMapping("/classify/life_classify")
    public String life_classifyPage() {
        return "classify/life_classify";
    }

    @GetMapping("/classify/car_classify")
    public String car_classifyPage() {
        return "classify/car_classify";
    }
}
