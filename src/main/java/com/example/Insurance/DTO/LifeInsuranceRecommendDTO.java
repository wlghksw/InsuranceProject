package com.example.Insurance.DTO;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonSetter;
import com.fasterxml.jackson.annotation.Nulls;
import lombok.Data;

import java.util.List;

@Data
public class LifeInsuranceRecommendDTO {

    @Data
    public static class Request {
        // 성별
        @JsonAlias({"성별", "gender"})
        private String gender;

        // 나이
        @JsonAlias({"나이", "age"})
        private Integer age;

        // 직업
        @JsonAlias({"직업", "job"})
        private String job;

        // 희망 보험료
        @JsonAlias({"desiredPremium", "premium", "보험료"})
        private Integer desiredPremium;

        // 희망 지급금액(보장금액)
        @JsonAlias({"desiredCoverage", "coverage", "지급금액", "보장금액"})
        private Integer desiredCoverage;

        // 정렬 키 (서비스에서 convertValue로도 뽑지만, DTO에 필드를 두면 가장 안전)
        @JsonAlias({"sort_by", "sortBy", "sort", "order", "정렬", "정렬순"})
        private String sortBy;

        // topk 기본값
        @JsonAlias({"topk", "k", "top"})
        @JsonSetter(nulls = Nulls.SKIP)
        private Integer topk = 10;

        // ====== 정상화(콤마숫자 → Integer)용 세터 ======

        public void setDesiredPremium(Object v) { this.desiredPremium = parseIntLoose(v); }
        public void setDesiredCoverage(Object v) { this.desiredCoverage = parseIntLoose(v); }
        public void setAge(Object v) { this.age = parseIntLoose(v); }

        // 문자열/숫자 모두 수용, "50,000" → 50000
        private Integer parseIntLoose(Object v) {
            if (v == null) return null;
            if (v instanceof Number) return ((Number) v).intValue();
            String s = String.valueOf(v).trim();
            if (s.isEmpty()) return null;
            s = s.replaceAll("[,_\\s]", "");
            try { return Integer.valueOf(s); }
            catch (Exception e) { return null; }
        }
    }

    @Data
    public static class Item {
        private String product;
        private Integer productPremium;
        private Integer productCoverage;
    }

    @Data
    public static class Response {
        private List<Item> items;
        private String error;

        public Response() {}
        public Response(String error) { this.error = error; }
    }
}
