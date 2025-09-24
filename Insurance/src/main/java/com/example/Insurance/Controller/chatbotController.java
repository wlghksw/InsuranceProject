package com.example.Insurance.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class chatbotController {

        @GetMapping("/chatbot")
        public String showServiceIntroPage() {
            return "chatbot";
        }
    }
