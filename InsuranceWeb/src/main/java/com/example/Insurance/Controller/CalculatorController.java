package com.example.Insurance.Controller;

import com.example.Insurance.DTO.CalRequestDTO;
import com.example.Insurance.DTO.CalResponseDTO;
import com.example.Insurance.Service.CalculatorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

/**
 * 보험료 계산기 관련 웹 페이지 요청과 API 요청을 처리하는 컨트롤러입니다.
 */
@Controller
@RequiredArgsConstructor
public class CalculatorController {

    private final CalculatorService calculatorService;

    /**
     * 보험료 계산기 페이지 뷰(HTML)를 반환
     * @param model 뷰에 데이터를 전달하기 위한 객체
     * @return "calculator" 뷰 이름
     */
    @GetMapping("/calculator")
    public String showCalculatorPage(Model model) {
        return "calculator";
    }

    /**
     * 보험료 계산 API 엔드포인트입니다.
     * @param requestDto 클라이언트에서 보낸 계산 요청 데이터
     * @return 계산된 보험료가 담긴 ResponseEntity
     */
    @PostMapping("/api/calculate")
    @ResponseBody
    public ResponseEntity<CalResponseDTO> calculatePremium(@RequestBody CalRequestDTO requestDto) {
        // 서비스의 계산 메소드를 호출합니다.
        long premium = calculatorService.calculate(requestDto);

        // 응답 DTO를 생성하여 결과를 담습니다.
        CalResponseDTO responseDto = new CalResponseDTO(premium);

        // HTTP 200 OK 상태와 함께 결과를 반환합니다.
        return ResponseEntity.ok(responseDto);
    }
}
