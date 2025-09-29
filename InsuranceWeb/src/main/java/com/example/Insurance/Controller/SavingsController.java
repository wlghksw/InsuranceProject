package com.example.Insurance.Controller;

import com.example.Insurance.DTO.SavingsRecommendationRequest;
import com.example.Insurance.DTO.SavingsRecommendationResponse;
import com.example.Insurance.DTO.UserProfileRecommendationRequest;
import com.example.Insurance.Service.SavingsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/savings")
public class SavingsController {

    @Autowired
    private SavingsService savingsService;

    @GetMapping("/recommend")
    public String recommendPage(Model model) {
        return "savings/savings_recommend";
    }

    @GetMapping("/profile-recommend")
    public String profileRecommendPage(Model model) {
        return "savings/savings_profile_recommend";
    }

    @PostMapping("/recommend/api")
    @ResponseBody
    public SavingsRecommendationResponse getRecommendations(@RequestBody SavingsRecommendationRequest request) {
        try {
            // Controller에서 받은 데이터 로깅
            System.out.println("=== 연금보험 추천 Controller에서 받은 데이터 ===");
            System.out.println("request 객체: " + request);
            System.out.println("age: " + request.getAge());
            System.out.println("monthlyBudget: " + request.getMonthlyBudget());
            System.out.println("purpose: " + request.getPurpose());
            System.out.println("preferredTerm: " + request.getPreferredTerm());
            System.out.println("preferUniversal: " + request.getPreferUniversal());
            System.out.println("minGuaranteedRate: " + request.getMinGuaranteedRate());
            System.out.println("topN: " + request.getTopN());
            System.out.println("===============================================");
            
            return savingsService.getRecommendations(request);
        } catch (Exception e) {
            e.printStackTrace();
            SavingsRecommendationResponse errorResponse = new SavingsRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("저축성보험 추천 요청 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(List.of());
            return errorResponse;
        }
    }

    @PostMapping("/profile-recommend/api")
    @ResponseBody
    public SavingsRecommendationResponse getProfileRecommendations(@RequestBody UserProfileRecommendationRequest request) {
        try {
            System.out.println("=== 사용자 특성 기반 저축성보험 추천 Controller에서 받은 데이터 ===");
            System.out.println("age: " + request.getAge());
            System.out.println("sex: " + request.getSex());
            System.out.println("monthlyBudget: " + request.getMonthlyBudget());
            System.out.println("minCoverage: " + request.getMinCoverage());
            System.out.println("maxPremiumAvg: " + request.getMaxPremiumAvg());
            System.out.println("preferNonRenewal: " + request.getPreferNonRenewal());
            System.out.println("requireSalesChannel: " + request.getRequireSalesChannel());
            System.out.println("topN: " + request.getTopN());
            System.out.println("===============================================");
            
            return savingsService.getProfileRecommendations(request);
        } catch (Exception e) {
            e.printStackTrace();
            SavingsRecommendationResponse errorResponse = new SavingsRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("사용자 특성 기반 저축성보험 추천 요청 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(List.of());
            return errorResponse;
        }
    }

    @GetMapping("/analytics/summary")
    @ResponseBody
    public Map<String, Object> getAnalyticsSummary() {
        try {
            return savingsService.getAnalyticsSummary();
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "저축성보험 분석 요약 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    @GetMapping("/products")
    public String getAllProducts(Model model) {
        try {
            List<Map<String, Object>> products = savingsService.getAllProducts();
            model.addAttribute("products", products);
            return "savings/savings_products";
        } catch (Exception e) {
            e.printStackTrace();
            model.addAttribute("error", "저축성보험 상품 조회 중 오류가 발생했습니다: " + e.getMessage());
            return "savings/savings_products";
        }
    }
}
