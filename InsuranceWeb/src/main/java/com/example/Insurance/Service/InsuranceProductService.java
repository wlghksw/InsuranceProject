package com.example.Insurance.Service;

import com.example.Insurance.DTO.InsuranceProductRequest;
import com.example.Insurance.Entity.InsuranceProduct;
import com.example.Insurance.Repository.InsuranceProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class InsuranceProductService {

    private final InsuranceProductRepository productRepository;

    @Transactional
    public InsuranceProduct addProduct(InsuranceProductRequest request) {
        // 1. DB에 저장
        InsuranceProduct product = InsuranceProduct.builder()
                .productType(request.getProductType())
                .insuranceCompany(request.getInsuranceCompany())
                .productName(request.getProductName())
                .coverageAmount(request.getCoverageAmount())
                .malePremium(request.getMalePremium())
                .femalePremium(request.getFemalePremium())
                .renewalCycle(request.getRenewalCycle())
                .guaranteedRate(request.getGuaranteedRate())
                .currentRate(request.getCurrentRate())
                .term(request.getTerm())
                .monthlyPremium(request.getMonthlyPremium())
                .surrenderValue(request.getSurrenderValue())
                .paymentMethod(request.getPaymentMethod())
                .salesChannel(request.getSalesChannel())
                .specialNotes(request.getSpecialNotes())
                .build();

        InsuranceProduct savedProduct = productRepository.save(product);

        // 2. CSV 파일에 추가
        try {
            saveToCSV(request);
        } catch (IOException e) {
            // CSV 저장 실패해도 DB 저장은 유지
            System.err.println("CSV 저장 실패: " + e.getMessage());
        }

        return savedProduct;
    }

    private void saveToCSV(InsuranceProductRequest request) throws IOException {
        String csvPath = getCsvPath(request.getProductType());
        
        if (csvPath == null) {
            throw new IOException("Unknown product type: " + request.getProductType());
        }

        Path path = Paths.get(csvPath);
        
        // 파일이 존재하는지 확인
        boolean fileExists = Files.exists(path);
        
        // CSV 행 생성
        String csvLine = buildCsvLine(request);
        
        // 파일에 추가
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(path.toFile(), true))) {
            if (fileExists) {
                writer.newLine(); // 기존 파일에 추가할 경우 개행
            }
            writer.write(csvLine);
        }
    }

    private String getCsvPath(String productType) {
        String baseDir = "/Users/cjh/Desktop/Insurance 4/data/csv/";
        
        switch (productType) {
            case "암보험":
                return baseDir + "cancer.csv";
            case "상해보험":
                return baseDir + "accident.csv";
            case "저축성보험":
                return baseDir + "savings.csv";
            default:
                return null;
        }
    }

    private String buildCsvLine(InsuranceProductRequest request) {
        // 상품 유형에 따라 CSV 형식이 다름
        switch (request.getProductType()) {
            case "암보험":
                return buildCancerCsvLine(request);
            case "상해보험":
                return buildAccidentCsvLine(request);
            case "저축성보험":
                return buildSavingsCsvLine(request);
            default:
                return "";
        }
    }

    private String buildCancerCsvLine(InsuranceProductRequest request) {
        // cancer.csv 형식
        // insurance_company,product_name,product_type,coverage_amount,male_premium,female_premium,fixed_rate,current_rate,min_guaranteed_rate,surrender_value,renewal_cycle,universal,sales_channel,sales_date,contact_number,policy_id
        return String.format("%s,%s,주계약,%s,%s,%s,%s,%s,%s,%s,%s,비유니버셜,%s,%s,-,%d",
                escapeCsv(request.getInsuranceCompany()),
                escapeCsv(request.getProductName()),
                escapeCsv(request.getCoverageAmount() != null ? request.getCoverageAmount() : "-"),
                escapeCsv(request.getMalePremium() != null ? request.getMalePremium() : "-"),
                escapeCsv(request.getFemalePremium() != null ? request.getFemalePremium() : "-"),
                escapeCsv(request.getGuaranteedRate() != null ? request.getGuaranteedRate() : "-"),
                escapeCsv(request.getCurrentRate() != null ? request.getCurrentRate() : "-"),
                escapeCsv(request.getGuaranteedRate() != null ? request.getGuaranteedRate() : "-"),
                escapeCsv(request.getSurrenderValue() != null ? request.getSurrenderValue() : "-"),
                escapeCsv(request.getRenewalCycle() != null ? request.getRenewalCycle() : "비갱신형"),
                escapeCsv(request.getSalesChannel() != null ? request.getSalesChannel() : "대면채널"),
                escapeCsv(java.time.LocalDate.now().toString()),
                System.currentTimeMillis() % 10000 // 간단한 policy_id 생성
        );
    }

    private String buildAccidentCsvLine(InsuranceProductRequest request) {
        // accident.csv 형식
        // insurance_company,product_name,male_premium,female_premium,coverage_amount,renewal_cycle,special_notes
        return String.format("%s,%s,%s,%s,%s,%s,%s",
                escapeCsv(request.getInsuranceCompany()),
                escapeCsv(request.getProductName()),
                escapeCsv(request.getMalePremium() != null ? request.getMalePremium() : "-"),
                escapeCsv(request.getFemalePremium() != null ? request.getFemalePremium() : "-"),
                escapeCsv(request.getCoverageAmount() != null ? request.getCoverageAmount() : "-"),
                escapeCsv(request.getRenewalCycle() != null ? request.getRenewalCycle() : "비갱신형"),
                escapeCsv(request.getSpecialNotes() != null ? request.getSpecialNotes() : "")
        );
    }

    private String buildSavingsCsvLine(InsuranceProductRequest request) {
        return String.format("%s,%s,1,%s,-,-,-,-,-,-,%s,%s,-,-,-,-,-,-,-,일반,비유니버셜,월납,%s,%s,-,-",
                escapeCsv(request.getInsuranceCompany()),
                escapeCsv(request.getProductName()),
                escapeCsv(request.getMonthlyPremium() != null ? request.getMonthlyPremium() : "-"),
                escapeCsv(request.getGuaranteedRate() != null ? request.getGuaranteedRate() : "-"),
                escapeCsv(request.getCurrentRate() != null ? request.getCurrentRate() : "-"),
                escapeCsv(request.getSalesChannel() != null ? request.getSalesChannel() : "대면채널"),
                escapeCsv(java.time.LocalDate.now().toString())
        );
    }

    private String escapeCsv(String value) {
        if (value == null) {
            return "";
        }
        // CSV에서 쉼표와 따옴표 처리
        if (value.contains(",") || value.contains("\"") || value.contains("\n")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    public List<InsuranceProduct> getAllProducts() {
        return productRepository.findAll();
    }

    public List<InsuranceProduct> getProductsByType(String productType) {
        return productRepository.findByProductType(productType);
    }

    @Transactional
    public void deleteProduct(Long productId) {
        InsuranceProduct product = productRepository.findById(productId)
                .orElseThrow(() -> new IllegalArgumentException("상품을 찾을 수 없습니다: " + productId));
        
        // DB에서 삭제
        productRepository.delete(product);
        
        // CSV 파일에서도 삭제
        deleteProductFromCsv(product);
        
        System.out.println("상품 삭제 완료 (DB + CSV): " + product.getProductName());
    }
    
    private void deleteProductFromCsv(InsuranceProduct product) {
        String csvFilePath;
        
        // 상품 유형에 따른 CSV 파일 경로 결정
        switch (product.getProductType()) {
            case "암보험":
                csvFilePath = "/Users/cjh/Desktop/Insurance 4/data/csv/cancer.csv";
                break;
            case "상해보험":
                csvFilePath = "/Users/cjh/Desktop/Insurance 4/data/csv/accident.csv";
                break;
            case "저축성보험":
                csvFilePath = "/Users/cjh/Desktop/Insurance 4/data/csv/savings.csv";
                break;
            default:
                System.out.println("알 수 없는 상품 유형: " + product.getProductType());
                return;
        }
        
        Path path = Paths.get(csvFilePath);
        try {
            // CSV 파일의 모든 줄 읽기
            List<String> lines = Files.readAllLines(path);
            
            if (lines.isEmpty()) {
                System.out.println("CSV 파일이 비어있습니다: " + csvFilePath);
                return;
            }
            
            // 헤더 유지하고 삭제할 상품 제외
            List<String> updatedLines = new ArrayList<>();
            updatedLines.add(lines.get(0)); // 헤더 추가
            
            // 삭제할 상품의 policy_id 또는 상품명으로 필터링
            for (int i = 1; i < lines.size(); i++) {
                String line = lines.get(i);
                
                // 상품명이나 ID로 삭제 대상인지 확인
                boolean shouldDelete = false;
                
                if (product.getProductType().equals("암보험")) {
                    // 암보험: policy_id로 확인 (마지막 컬럼)
                    String[] columns = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1); // CSV 파싱
                    if (columns.length > 15) { // policy_id는 16번째 컬럼 (인덱스 15)
                        String policyIdStr = columns[15].trim();
                        try {
                            Long policyId = Long.parseLong(policyIdStr);
                            if (policyId.equals(product.getId())) {
                                shouldDelete = true;
                            }
                        } catch (NumberFormatException e) {
                            // policy_id가 숫자가 아니면 무시
                        }
                    }
                } else {
                    // 상해보험, 저축성보험: 상품명으로 확인
                    if (line.contains(product.getProductName()) && line.contains(product.getInsuranceCompany())) {
                        shouldDelete = true;
                    }
                }
                
                if (!shouldDelete) {
                    updatedLines.add(line);
                }
            }
            
            // CSV 파일 다시 쓰기
            Files.write(path, updatedLines, StandardOpenOption.TRUNCATE_EXISTING);
            
            System.out.println("CSV 파일에서 상품 삭제 완료: " + csvFilePath);
            System.out.println("삭제된 줄 수: " + (lines.size() - updatedLines.size()));
            
        } catch (IOException e) {
            System.err.println("CSV 파일에서 상품 삭제 중 오류 발생: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

