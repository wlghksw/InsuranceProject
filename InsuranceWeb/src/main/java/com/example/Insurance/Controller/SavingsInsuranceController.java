package com.example.Insurance.Controller;

import com.example.Insurance.DTO.SavingsInsuranceRecommendationRequest;
import com.example.Insurance.DTO.SavingsInsuranceRecommendationResponse;
import com.example.Insurance.Service.SavingsInsuranceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/savings-insurance")
public class SavingsInsuranceController {
    
    @Autowired
    private SavingsInsuranceService savingsInsuranceService;
    
    @GetMapping("/recommend")
    public String recommendPage(Model model) {
        return "savings-insurance/savings_insurance_recommend";
    }
    
    @PostMapping("/recommend/api")
    @ResponseBody
    public SavingsInsuranceRecommendationResponse getRecommendations(@RequestBody SavingsInsuranceRecommendationRequest request) {
        try {
            System.out.println("=== 저축성보험 추천 Controller에서 받은 데이터 ===");
            System.out.println("age: " + request.getAge());
            System.out.println("monthlyBudget: " + request.getMonthlyBudget());
            System.out.println("purpose: " + request.getPurpose());
            System.out.println("minGuaranteedRate: " + request.getMinGuaranteedRate());
            System.out.println("topN: " + request.getTopN());
            System.out.println("===============================================");
            
            return savingsInsuranceService.getRecommendations(request);
        } catch (Exception e) {
            e.printStackTrace();
            SavingsInsuranceRecommendationResponse errorResponse = new SavingsInsuranceRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("저축성보험 추천 요청 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(List.of());
            return errorResponse;
        }
    }
    
    @GetMapping("/analytics")
    @ResponseBody
    public Map<String, Object> getAnalyticsSummary() {
        try {
            return savingsInsuranceService.getAnalyticsSummary();
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "저축성보험 분석 요약 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
}
