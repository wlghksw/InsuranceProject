package com.example.Insurance.Controller;

import org.springframework.web.bind.annotation.GetMapping;

public class AvailableController {

    @GetMapping("/available")
    public String availablePage() {
        return "available";
    }

    @GetMapping("/available/cancer_available")
    public String cancer_AvailablePage() {
        return "cancer_available";
    }

    @GetMapping("/available/car_available")
    public String car_AvailablePage() {
        return "car_available";
    }

    @GetMapping("/available/medical_available")
    public String medical_availablePage() {
        return "medical_available";
    }

    @GetMapping("/available/life_available")
    public String life_availablePage() {
        return "life_available";
    }
}
