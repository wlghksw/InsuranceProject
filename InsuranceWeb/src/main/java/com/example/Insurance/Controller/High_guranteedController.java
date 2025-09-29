package com.example.Insurance.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class High_guranteedController {

    @GetMapping("/high_guaranteed")
    public String setHigh_guaranteedPage() {
        return "high_guaranteed";
    }

    @GetMapping("/high_guaranteed/medical_high_guaranteed")
    public String medical_high_guaranteedPage() {
        return "high_guaranteed/medical_high_guaranteed";
    }

    @GetMapping("/high_guaranteed/cancer_high)guaranteed")
    public String cancer_high_guaranteedPage() {
        return "high_guaranteed/cancer_high_guaranteed";
    }

    @GetMapping("/high_guaranteed/life_high_guaranteed")
    public String life_high_guaranteedPage() {
        return "high_guaranteed/life_high_guaranteed";
    }
}
