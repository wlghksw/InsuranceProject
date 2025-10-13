package com.example.Insurance.Service;

import com.example.Insurance.DTO.LifeInsuranceRecommendDTO;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class LifeInsuranceRecommendService {

    private static final ObjectMapper MAPPER = new ObjectMapper()
            .configure(JsonParser.Feature.ALLOW_COMMENTS, true)
            .configure(JsonParser.Feature.ALLOW_UNQUOTED_FIELD_NAMES, true);

    private static final String PYTHON = "python3";

    // 환경에 맞게 조정
    private static final File WORKDIR = new File("/Users/jun/Desktop/Insurance/Python");
    private static final String SCRIPT_NAME = "insurance_worker.py";
    private static final File SCRIPT_FILE = new File(WORKDIR, SCRIPT_NAME);
    private static final File CSV_FILE = new File(WORKDIR, "insurance_core.csv");

    public LifeInsuranceRecommendDTO.Response recommend(LifeInsuranceRecommendDTO.Request req) {
        try {
            // 1) 필수값 검증 (빈 문자열/0도 실패로 간주)
            String gender = trimToNull(req.getGender());
            String job    = trimToNull(req.getJob());
            Integer age   = req.getAge();
            Integer prem  = req.getDesiredPremium();
            Integer cov   = req.getDesiredCoverage();

            if (gender == null || job == null || age == null || prem == null || cov == null) {
                return new LifeInsuranceRecommendDTO.Response(
                        "missing_fields: need gender, age, job, premium, coverage"
                );
            }
            if (age <= 0 || prem <= 0 || cov <= 0) {
                return new LifeInsuranceRecommendDTO.Response(
                        "invalid_fields: age/premium/coverage must be positive"
                );
            }

            Map<String, Object> payload = buildWorkerPayload(req);

            ProcessBuilder pb = new ProcessBuilder(PYTHON, SCRIPT_FILE.getAbsolutePath());
            pb.directory(WORKDIR);
            Map<String, String> env = pb.environment();
            env.put("INS_CSV_PATH", CSV_FILE.getAbsolutePath());
            pb.redirectErrorStream(false);

            Process p = pb.start();

            try (BufferedWriter w = new BufferedWriter(
                    new OutputStreamWriter(p.getOutputStream(), StandardCharsets.UTF_8))) {
                w.write(MAPPER.writeValueAsString(payload));
                w.write("\n");
                w.flush();
            }

            String stdout;
            String stderr;
            try (BufferedReader out = new BufferedReader(
                    new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8));
                 BufferedReader err = new BufferedReader(
                         new InputStreamReader(p.getErrorStream(), StandardCharsets.UTF_8))) {
                stdout = readAll(out);
                stderr = readAll(err);
            }

            int exit = p.waitFor();

            log.info("[python:payload] {}", payload);
            if (!isBlank(stderr)) log.warn("[python:stderr] {}", abbreviate(stderr, 2000));
            log.info("[python:stdout] {}", abbreviate(stdout, 2000));

            if (isBlank(stdout)) {
                return new LifeInsuranceRecommendDTO.Response(
                        "python returned empty output (exit=" + exit + ")"
                );
            }

            String json = sanitizeToJson(stdout);
            if (json == null) {
                return new LifeInsuranceRecommendDTO.Response(
                        "no json found in python output (exit=" + exit + "): " + abbreviate(stdout, 200)
                );
            }

            Map<String, Object> worker = MAPPER.readValue(json, new TypeReference<Map<String, Object>>() {});
            String status = String.valueOf(worker.getOrDefault("status", "error"));
            if (!"ok".equalsIgnoreCase(status)) {
                return new LifeInsuranceRecommendDTO.Response(
                        "python error: " + String.valueOf(worker.getOrDefault("message", "unknown"))
                );
            }

            List<Map<String, Object>> rawItems = extractItems(worker);
            List<LifeInsuranceRecommendDTO.Item> items = mapToDtoItems(rawItems);

            LifeInsuranceRecommendDTO.Response resp = new LifeInsuranceRecommendDTO.Response();
            resp.setItems(items);
            return resp;

        } catch (Exception e) {
            log.error("recommend failed", e);
            return new LifeInsuranceRecommendDTO.Response("server_error: " + e.getMessage());
        }
    }

    // ----------------- Helpers -----------------

    private static String readAll(BufferedReader r) throws IOException {
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = r.readLine()) != null) sb.append(line).append('\n');
        return sb.toString();
    }

    private static String sanitizeToJson(String s) {
        if (s == null) return null;
        String t = s.trim();

        int objStart = t.indexOf('{');
        int objEnd   = t.lastIndexOf('}');
        if (objStart >= 0 && objEnd > objStart) return t.substring(objStart, objEnd + 1);

        int arrStart = t.indexOf('[');
        int arrEnd   = t.lastIndexOf(']');
        if (arrStart >= 0 && arrEnd > arrStart) return t.substring(arrStart, arrEnd + 1);

        try (BufferedReader br = new BufferedReader(new StringReader(t))) {
            String line;
            while ((line = br.readLine()) != null) {
                String L = line.trim();
                if (L.startsWith("{") || L.startsWith("[")) return L;
            }
        } catch (IOException ignored) {}
        return null;
    }

    private static String abbreviate(String s, int max) {
        if (s == null) return null;
        return (s.length() <= max) ? s : (s.substring(0, max) + "...");
    }

    private Map<String, Object> buildWorkerPayload(LifeInsuranceRecommendDTO.Request req) {
        Map<String, Object> payload = new HashMap<>();

        // ✅ 빈 문자열/0을 넣지 않고, 이미 위에서 검증된 값만 사용
        payload.put("gender", trimToNull(req.getGender()));
        payload.put("age", req.getAge());
        payload.put("job", trimToNull(req.getJob()));
        payload.put("desiredPremium", req.getDesiredPremium());
        payload.put("desiredCoverage", req.getDesiredCoverage());

        int k = (req.getTopk() == null || req.getTopk() < 1) ? 5 : req.getTopk();
        payload.put("k", k);

        String sortNorm = normalizeSort(extractSortKey(req));
        payload.put("sortBy", sortNorm);
        payload.put("sort_by", sortNorm);

        payload.put("debug", true);
        return payload;
    }

    /** Request DTO를 Map으로 바꿔서 다양한 키로 들어오는 정렬값을 안전하게 추출 */
    private Object extractSortKey(Object req) {
        Map<String, Object> m = MAPPER.convertValue(req, new TypeReference<Map<String, Object>>() {});
        String[] keys = {"sort_by", "sortBy", "sort", "order", "정렬", "정렬순"};
        for (String k : keys) {
            Object v = m.get(k);
            if (v != null) {
                String s = String.valueOf(v).trim();
                if (!s.isEmpty()) return s;
            }
        }
        return null;
    }

    /** 정렬 alias 정규화: distance / premium / coverage 로 환원 */
    private static String normalizeSort(Object v) {
        if (v == null) return "distance";
        String s = String.valueOf(v).trim().toLowerCase().replace(" ", "");
        switch (s) {
            case "distance": case "종합": case "overall": return "distance";
            case "premium":
            case "보험가까운순": case "보험료가까운순":
            case "보험근접":   case "보험료근접": return "premium";
            case "coverage":
            case "보장금액가까운순": case "지급금액가까운순":
            case "보장근접":       case "지급금액근접":
            case "보장금액정렬순":  case "지급금액정렬순": return "coverage";
            default: return "distance";
        }
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractItems(Map<String, Object> worker) {
        Object itemsObj = worker.get("items");
        if (!(itemsObj instanceof List)) itemsObj = worker.get("top");
        if (itemsObj instanceof List) return (List<Map<String, Object>>) itemsObj;
        return Collections.emptyList();
    }

    private List<LifeInsuranceRecommendDTO.Item> mapToDtoItems(List<Map<String, Object>> raw) {
        List<LifeInsuranceRecommendDTO.Item> out = new ArrayList<>();
        for (Map<String, Object> it : raw) {
            LifeInsuranceRecommendDTO.Item d = new LifeInsuranceRecommendDTO.Item();

            d.setProduct(
                    firstNonBlank(
                            it.get("product"),
                            it.get("상품명"),
                            it.get("name")
                    )
            );

            d.setProductPremium(firstNonNullInt(
                    it.get("productPremium"),
                    it.get("보험료"),
                    it.get("premium")
            ));

            d.setProductCoverage(firstNonNullInt(
                    it.get("productCoverage"),
                    it.get("지급금액"),
                    it.get("coverage")
            ));

            out.add(d);
        }
        return out;
    }

    // --- small utils ---

    private static String trimToNull(String s) {
        if (s == null) return null;
        String t = s.trim();
        return t.isEmpty() ? null : t;
    }

    private static boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }

    private static String firstNonBlank(Object... cands) {
        for (Object c : cands) {
            if (c == null) continue;
            String s = String.valueOf(c).trim();
            if (!s.isEmpty()) return s;
        }
        return "-";
    }

    private static Integer firstNonNullInt(Object... cands) {
        for (Object c : cands) {
            if (c == null) continue;
            if (c instanceof Number) return ((Number) c).intValue();
            try {
                String s = String.valueOf(c).replaceAll("[,_\\s]", "");
                if (s.isEmpty()) continue;
                return Integer.parseInt(s);
            } catch (Exception ignored) {}
        }
        return null;
    }
}
