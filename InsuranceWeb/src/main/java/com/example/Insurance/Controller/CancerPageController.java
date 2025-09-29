package com.example.Insurance.Controller;

import com.example.Insurance.DTO.CancerFilterRequest;
import com.example.Insurance.DTO.CancerRecommendationResponse;
import com.example.Insurance.DTO.UserProfileRecommendationRequest;
import com.example.Insurance.Service.CancerRecommendationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/cancer")
public class CancerPageController {

    @Autowired
    private CancerRecommendationService cancerRecommendationService;

    @GetMapping("/recommend")
    public String showRecommendPage(Model model) {
        return "cancer/cancer_recommend";
    }


    @GetMapping("/profile-recommend")
    public String showProfileRecommendPage(Model model) {
        return "cancer/cancer_profile_recommend";
    }

    @PostMapping("/recommend/api")
    @ResponseBody
    public CancerRecommendationResponse findRecommendations(@RequestBody Map<String, Object> requestMap) {
        try {
            // Controller에서 받은 데이터 로깅
            System.out.println("=== Controller에서 받은 원본 데이터 ===");
            System.out.println("전체 데이터: " + requestMap);
            
            // Map을 CancerFilterRequest로 변환
            CancerFilterRequest request = new CancerFilterRequest();
            request.setMinCoverage((Integer) requestMap.get("minCoverage"));
            request.setMaxPremium(((Number) requestMap.get("maxPremium")).doubleValue());
            
            // renewalType을 boolean으로 변환
            String renewalType = (String) requestMap.get("renewalType");
            if ("renewal".equals(renewalType)) {
                request.setPreferNonRenewal(false); // 갱신 있음 = 갱신형 선호
            } else if ("non-renewal".equals(renewalType)) {
                request.setPreferNonRenewal(true);  // 갱신 없음 = 비갱신형 선호
            } else {
                request.setPreferNonRenewal(true); // 기본값
            }
            
            request.setRequireSalesChannel((String) requestMap.get("salesChannel"));
            
            // 가중치 변환 (개별 필드를 List로)
            Double coverageWeight = ((Number) requestMap.get("coverageWeight")).doubleValue();
            Double valueWeight = ((Number) requestMap.get("valueWeight")).doubleValue();
            Double stabilityWeight = ((Number) requestMap.get("stabilityWeight")).doubleValue();
            request.setWeights(List.of(coverageWeight, valueWeight, stabilityWeight));
            
            request.setTopN((Integer) requestMap.get("topN"));
            
            System.out.println("=== 변환된 데이터 ===");
            System.out.println("minCoverage: " + request.getMinCoverage());
            System.out.println("maxPremium: " + request.getMaxPremium());
            System.out.println("preferNonRenewal: " + request.getPreferNonRenewal());
            System.out.println("requireSalesChannel: " + request.getRequireSalesChannel());
            System.out.println("weights: " + request.getWeights());
            System.out.println("topN: " + request.getTopN());
            System.out.println("=================================");
            
            return cancerRecommendationService.findRecommendations(request);
        } catch (Exception e) {
            e.printStackTrace();
            CancerRecommendationResponse errorResponse = new CancerRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("추천 요청 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(List.of());
            return errorResponse;
        }
    }


    @PostMapping("/profile-recommend/api")
    @ResponseBody
    public CancerRecommendationResponse findProfileRecommendations(@RequestBody UserProfileRecommendationRequest request) {
        try {
            return cancerRecommendationService.findProfileRecommendations(request);
        } catch (Exception e) {
            e.printStackTrace();
            CancerRecommendationResponse errorResponse = new CancerRecommendationResponse();
            errorResponse.setSuccess(false);
            errorResponse.setMessage("사용자 특성 기반 추천 요청 중 오류가 발생했습니다: " + e.getMessage());
            errorResponse.setTotalProducts(0);
            errorResponse.setRecommendations(List.of());
            return errorResponse;
        }
    }

    @GetMapping("/analytics/summary")
    @ResponseBody
    public Map<String, Object> getAnalyticsSummary() {
        try {
            return cancerRecommendationService.getAnalyticsSummary();
        } catch (Exception e) {
            e.printStackTrace();
            return Map.of("error", "분석 요약 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }

    @GetMapping("/products")
    public String showAllProducts(Model model) {
        try {
            List<Map<String, Object>> products = cancerRecommendationService.findAllProducts();
            model.addAttribute("products", products);
            return "cancer/cancer_products";
        } catch (Exception e) {
            e.printStackTrace();
            model.addAttribute("error", "상품 조회 중 오류가 발생했습니다: " + e.getMessage());
            return "cancer/cancer_products";
        }
    }
}
