package com.example.Insurance.Controller;

import com.example.Insurance.DTO.CancerRecommendationRequest;
import com.example.Insurance.DTO.CancerRecommendationResponse;
import com.example.Insurance.Service.CancerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/cancer")
public class CancerController {

    @Autowired
    private CancerService cancerService;

    @GetMapping("/recommend")
    public String recommendPage(Model model) {
        return "cancer/cancer_recommend";
    }

    @PostMapping("/recommend/api")
    @ResponseBody
    public CancerRecommendationResponse getRecommendations(@RequestBody CancerRecommendationRequest request) {
        try {
            return cancerService.getRecommendations(request);
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

    @GetMapping("/products")
    public String getAllProducts(Model model) {
        try {
            List<Map<String, Object>> products = cancerService.getAllProducts();
            model.addAttribute("products", products);
            return "cancer/cancer_products";
        } catch (Exception e) {
            e.printStackTrace();
            model.addAttribute("error", "상품 조회 중 오류가 발생했습니다: " + e.getMessage());
            return "cancer/cancer_products";
        }
    }
}
