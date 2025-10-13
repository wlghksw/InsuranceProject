## 종신 보험 맞춤 추천 (Life Insurance Recommender)

간단한 KNN 기반의 종신보험 추천 시스템입니다.
CSV의 스키마에 맞춰 라벨 인코딩과 스케일링을 수행하고,
사용자의 입력(성별, 희망 보험료, 지급금액, 나이, 직업)을 기준으로 가장 가까운 상품 Top-K를 추천합니다.

## 추천 로직

성별 분리 스케일링:
남/녀 데이터를 분리하고 각각 StandardScaler로 정규화 후, KNN 거리 기반 근접도 계산

직업 위험도 추정:
직업명 → 위험도 매핑이 불확실할 경우, 동일 직업군의 위험도 mode 값 사용

정렬 옵션:

distance (기본): 전체 피처 거리

premium: 보험료 차이 절댓값

coverage: 지급금액 차이 절댓값

상품명 복원:
내부적으로 LabelEncoder로 인코딩하지만, 출력 시 원래 상품명으로 복원

## Repository 구조
life-insurance-recommender/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  └─ README.md
├─ src/
│  └─ life_insurance_recommender/
│     ├─ __init__.py
│     └─ recommender.py
└─ scripts/
   └─ demo.py

## 의존성
from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
import pandas as pd
from difflib import get_close_matches
from sklearn.preprocessing import LabelEncoder, StandardScaler

## 역할
모듈
pandas, numpy	데이터 핸들링
difflib.get_close_matches	문자열 근사 매칭 (직업명 유사 검색)
LabelEncoder, StandardScaler	범주형 인코딩 / 수치 정규화

LabelEncoder는 “문자열 → 정수” 변환용이며, 숫자 크기에 의미는 없음.
따라서 거리 계산에는 직접 사용하지 않고 설명 필드용으로만 유지함.

## 클래스 구조
SortBy = Literal["distance", "premium", "coverage"]

@dataclass
class _Encoders:
    job: LabelEncoder
    jobrisk: LabelEncoder
    product: LabelEncoder
    gender: LabelEncoder

class Recommender:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.enc: Optional[_Encoders] = None
        self.df_f = self.df_m = None
        self.scaler_f = self.scaler_m = None
        self.X_f_scaled = self.X_m_scaled = None
        self.job2risk_lookup: Optional[dict] = None


4종 인코더(직업, 직업 위험도, 상품명, 성별)를 통합 관리

성별별로 풀을 분리하고 각각 StandardScaler로 정규화

fit_csv() → CSV 로드 및 인코딩

recommend_top_k() → 입력값 기반 추천 수행

## 전처리 및 학습
fit_csv / fit_df
def fit_csv(self, csv_path: str) -> "Recommender":
    df = pd.read_csv(csv_path)
    return self.fit_df(df)

def fit_df(self, df: pd.DataFrame) -> "Recommender":
    required = ["상품명","성별","남자(보험료)","여자(보험료)","지급금액","가입금액","나이","직업","직업 위험도"]

    # 라벨 인코딩
    job = LabelEncoder(); jobrisk = LabelEncoder()
    product = LabelEncoder(); gender = LabelEncoder()

    df["직업"] = job.fit_transform(df["직업"].astype(str))
    df["직업 위험도"] = jobrisk.fit_transform(df["직업 위험도"].astype(str))
    df["상품명"] = product.fit_transform(df["상품명"].astype(str))
    df["성별"] = gender.fit_transform(df["성별"].astype(str))

    self.enc = _Encoders(job=job, jobrisk=jobrisk, product=product, gender=gender)

    # 직업→위험도 룩업, 성별 풀 분리
    self.job2risk_lookup = self._build_job_to_risk_lookup(df)
    self.df_f = df[df["성별"] == 0].copy()
    self.df_m = df[df["성별"] == 1].copy()
    self._fit_gender_pool()

## 성별별 스케일링
def _fit_gender_pool(self):
    # Female
    X_f = self.df_f[["여자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
    self.scaler_f = StandardScaler().fit(X_f)
    self.X_f_scaled = self.scaler_f.transform(X_f)

    # Male
    X_m = self.df_m[["남자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
    self.scaler_m = StandardScaler().fit(X_m)
    self.X_m_scaled = self.scaler_m.transform(X_m)

💡 추천 함수 예시
res = recommender.recommend_top_k(
    gender_input="남자",
    premium=50000,
    coverage=10000000,
    age=25,
    job_text="사무직",
    k=10,                # 추천 개수
    sort_by="distance"   # 정렬 기준: "distance" | "premium" | "coverage"
)
print(res)

## 실행 순서
# 1. 환경 설정
pip install -r requirements.txt

# 2. CSV 파일 준비
# 예: ./insurance_core.csv

# 3. 실행
python scripts/demo.py

## 구현 포인트 요약
# 설명
LabelEncoder	문자열을 숫자로 변환 (직업, 위험도, 상품, 성별)
StandardScaler	성별별 피처 스케일 통일
get_close_matches	직업명 오타/근사 대응
직업→위험도	동일 직업군의 최빈(mode) 위험도 추정
정렬 옵션	거리·보험료·지급금액 기준 선택 가능
상품명 복원	추천 결과에 실제 상품명 표시
## 예시 결과
상품명	남자(보험료)	지급금액	나이	직업(원문)	직업 위험도(원문)
○○생명 종신보장형	45,000	10,000,000	25	사무직	낮음
△△생명 플러스형	48,000	9,500,000	26	사무직	낮음

## 카카오 로그인 API 사용

# Kakao Login (Spring Boot OAuth2) — Setup & Guide

이 저장소는 **카카오 로그인 API**를 Spring Boot OAuth2 클라이언트로 연동하는 방법을 정리합니다.
아래 가이드만 따라하면 바로 로컬에서 로그인 테스트까지 가능합니다.

> 📦 포함된 소스 구조 스냅샷
```
kakao_src/
├─ __MACOSX
│  ├─ kakao
│  │  ├─ .gradle
│  │  │  ├─ 8.14.3
│  │  │  │  ├─ checksums
│  │  │  │  │  ├─ ._checksums.lock
│  │  │  │  │  ├─ ._md5-checksums.bin
│  │  │  │  │  └─ ._sha1-checksums.bin
│  │  │  │  ├─ executionHistory
│  │  │  │  │  ├─ ._executionHistory.bin
│  │  │  │  │  └─ ._executionHistory.lock
│  │  │  │  ├─ fileChanges
│  │  │  │  │  └─ ._last-build.bin
│  │  │  │  ├─ fileHashes
│  │  │  │  │  ├─ ._fileHashes.bin
│  │  │  │  │  ├─ ._fileHashes.lock
│  │  │  │  │  └─ ._resourceHashesCache.bin
│  │  │  │  ├─ ._checksums
│  │  │  │  ├─ ._executionHistory
│  │  │  │  ├─ ._expanded
│  │  │  │  ├─ ._fileChanges
│  │  │  │  ├─ ._fileHashes
│  │  │  │  ├─ ._gc.properties
│  │  │  │  └─ ._vcsMetadata
│  │  │  ├─ buildOutputCleanup
│  │  │  │  ├─ ._buildOutputCleanup.lock
│  │  │  │  ├─ ._cache.properties
│  │  │  │  └─ ._outputFiles.bin
│  │  │  ├─ vcs-1
│  │  │  │  └─ ._gc.properties
│  │  │  ├─ ._8.14.3
│  │  │  ├─ ._buildOutputCleanup
│  │  │  ├─ ._file-system.probe
│  │  │  └─ ._vcs-1
│  │  ├─ .idea
│  │  │  ├─ modules
│  │  │  │  └─ ._kakao.main.iml
│  │  │  ├─ ._.gitignore
│  │  │  ├─ ._compiler.xml
│  │  │  ├─ ._gradle.xml
│  │  │  ├─ ._misc.xml
│  │  │  ├─ ._modules
│  │  │  ├─ ._modules.xml
│  │  │  └─ ._workspace.xml
│  │  ├─ build
│  │  │  ├─ classes
│  │  │  │  ├─ java
│  │  │  │  │  ├─ main
│  │  │  │  │  │  ├─ com
│  │  │  │  │  │  │  ├─ example
│  │  │  │  │  │  │  │  ├─ kakao
│  │  │  │  │  │  │  │  │  ├─ config
│  │  │  │  │  │  │  │  │  │  ├─ ._CodefConfig.class
│  │  │  │  │  │  │  │  │  │  └─ ._SecurityConfig.class
│  │  │  │  │  │  │  │  │  ├─ controller
│  │  │  │  │  │  │  │  │  │  ├─ ._CodefController.class
│  │  │  │  │  │  │  │  │  │  └─ ._HomeController.class
│  │  │  │  │  │  │  │  │  ├─ ._config
│  │  │  │  │  │  │  │  │  ├─ ._controller
│  │  │  │  │  │  │  │  │  └─ ._KakaoApplication.class
│  │  │  │  │  │  │  │  └─ ._kakao
│  │  │  │  │  │  │  └─ ._example
│  │  │  │  │  │  └─ ._com
│  │  │  │  │  └─ ._main
│  │  │  │  └─ ._java
│  │  │  ├─ generated
│  │  │  │  ├─ sources
│  │  │  │  │  ├─ annotationProcessor
│  │  │  │  │  │  ├─ java
│  │  │  │  │  │  │  └─ ._main
│  │  │  │  │  │  └─ ._java
│  │  │  │  │  ├─ headers
│  │  │  │  │  │  ├─ java
│  │  │  │  │  │  │  └─ ._main
│  │  │  │  │  │  └─ ._java
│  │  │  │  │  ├─ ._annotationProcessor
│  │  │  │  │  └─ ._headers
│  │  │  │  └─ ._sources
│  │  │  ├─ reports
│  │  │  │  ├─ problems
│  │  │  │  │  └─ ._problems-report.html
│  │  │  │  └─ ._problems
│  │  │  ├─ resources
│  │  │  │  ├─ main
│  │  │  │  │  ├─ templates
│  │  │  │  │  │  ├─ ._codef-contract-info.mustache
│  │  │  │  │  │  ├─ ._codef-create-cert.mustache
│  │  │  │  │  │  ├─ ._index.mustache
│  │  │  │  │  │  └─ ._success.mustache
│  │  │  │  │  ├─ ._application.properties
│  │  │  │  │  ├─ ._static
│  │  │  │  │  └─ ._templates
│  │  │  │  └─ ._main
│  │  │  ├─ tmp
│  │  │  │  ├─ compileJava
│  │  │  │  │  ├─ compileTransaction
│  │  │  │  │  │  ├─ stash-dir
│  │  │  │  │  │  │  └─ ._CodefController.class.uniqueId0
│  │  │  │  │  │  ├─ ._backup-dir
│  │  │  │  │  │  └─ ._stash-dir
│  │  │  │  │  ├─ ._compileTransaction
│  │  │  │  │  └─ ._previous-compilation-data.bin
│  │  │  │  └─ ._compileJava
│  │  │  ├─ ._classes
│  │  │  ├─ ._generated
│  │  │  ├─ ._reports
│  │  │  ├─ ._resources
│  │  │  └─ ._tmp
│  │  ├─ gradle
│  │  │  ├─ wrapper
│  │  │  │  ├─ ._gradle-wrapper.jar
│  │  │  │  └─ ._gradle-wrapper.properties
│  │  │  └─ ._wrapper
│  │  ├─ src
│  │  │  ├─ main
│  │  │  │  ├─ java
│  │  │  │  │  ├─ com
│  │  │  │  │  │  ├─ example
│  │  │  │  │  │  │  ├─ kakao
│  │  │  │  │  │  │  │  ├─ config
│  │  │  │  │  │  │  │  │  ├─ ._CodefConfig.java
│  │  │  │  │  │  │  │  │  └─ ._SecurityConfig.java
│  │  │  │  │  │  │  │  ├─ controller
│  │  │  │  │  │  │  │  │  ├─ ._CodefController.java
│  │  │  │  │  │  │  │  │  └─ ._HomeController.java
│  │  │  │  │  │  │  │  ├─ ._api
│  │  │  │  │  │  │  │  ├─ ._config
│  │  │  │  │  │  │  │  ├─ ._controller
│  │  │  │  │  │  │  │  ├─ ._KakaoApplication.java
│  │  │  │  │  │  │  │  └─ ._service
│  │  │  │  │  │  │  └─ ._kakao
│  │  │  │  │  │  └─ ._example
│  │  │  │  │  └─ ._com
│  │  │  │  ├─ resources
│  │  │  │  │  ├─ templates
│  │  │  │  │  │  ├─ ._codef-contract-info.mustache
│  │  │  │  │  │  ├─ ._codef-create-cert.mustache
│  │  │  │  │  │  ├─ ._index.mustache
│  │  │  │  │  │  └─ ._success.mustache
│  │  │  │  │  ├─ ._application.properties
│  │  │  │  │  ├─ ._static
│  │  │  │  │  └─ ._templates
│  │  │  │  ├─ ._java
│  │  │  │  └─ ._resources
│  │  │  ├─ test
│  │  │  │  ├─ java
│  │  │  │  │  ├─ com
│  │  │  │  │  │  ├─ example
│  │  │  │  │  │  │  ├─ kakao
│  │  │  │  │  │  │  │  └─ ._KakaoApplicationTests.java
│  │  │  │  │  │  │  └─ ._kakao
│  │  │  │  │  │  └─ ._example
│  │  │  │  │  └─ ._com
│  │  │  │  └─ ._java
│  │  │  ├─ ._main
│  │  │  └─ ._test
│  │  ├─ ._.gitattributes
│  │  ├─ ._.gitignore
│  │  ├─ ._.gradle
│  │  ├─ ._.idea
│  │  ├─ ._build
│  │  ├─ ._build.gradle
│  │  ├─ ._gradle
│  │  ├─ ._gradlew
│  │  ├─ ._gradlew.bat
│  │  ├─ ._HELP.md
│  │  ├─ ._settings.gradle
│  │  └─ ._src
│  └─ ._kakao
└─ kakao
   ├─ .gradle
   │  ├─ 8.14.3
   │  │  ├─ checksums
   │  │  │  ├─ checksums.lock
   │  │  │  ├─ md5-checksums.bin
   │  │  │  └─ sha1-checksums.bin
   │  │  ├─ executionHistory
   │  │  │  ├─ executionHistory.bin
   │  │  │  └─ executionHistory.lock
   │  │  ├─ expanded
   │  │  ├─ fileChanges
   │  │  │  └─ last-build.bin
   │  │  ├─ fileHashes
   │  │  │  ├─ fileHashes.bin
   │  │  │  ├─ fileHashes.lock
   │  │  │  └─ resourceHashesCache.bin
   │  │  ├─ vcsMetadata
   │  │  └─ gc.properties
   │  ├─ buildOutputCleanup
   │  │  ├─ buildOutputCleanup.lock
   │  │  ├─ cache.properties
   │  │  └─ outputFiles.bin
   │  ├─ vcs-1
   │  │  └─ gc.properties
   │  └─ file-system.probe
   ├─ .idea
   │  ├─ modules
   │  │  └─ kakao.main.iml
   │  ├─ .gitignore
   │  ├─ compiler.xml
   │  ├─ gradle.xml
   │  ├─ misc.xml
   │  ├─ modules.xml
   │  └─ workspace.xml
   ├─ build
   │  ├─ classes
   │  │  └─ java
   │  │     └─ main
   │  │        └─ com
   │  │           └─ example
   │  │              └─ kakao
   │  │                 ├─ config
   │  │                 │  ├─ CodefConfig.class
   │  │                 │  └─ SecurityConfig.class
   │  │                 ├─ controller
   │  │                 │  ├─ CodefController.class
   │  │                 │  └─ HomeController.class
   │  │                 └─ KakaoApplication.class
   │  ├─ generated
   │  │  └─ sources
   │  │     ├─ annotationProcessor
   │  │     │  └─ java
   │  │     │     └─ main
   │  │     └─ headers
   │  │        └─ java
   │  │           └─ main
   │  ├─ reports
   │  │  └─ problems
   │  │     └─ problems-report.html
   │  ├─ resources
   │  │  └─ main
   │  │     ├─ static
   │  │     ├─ templates
   │  │     │  ├─ codef-contract-info.mustache
   │  │     │  ├─ codef-create-cert.mustache
   │  │     │  ├─ index.mustache
   │  │     │  └─ success.mustache
   │  │     └─ application.properties
   │  └─ tmp
   │     └─ compileJava
   │        ├─ compileTransaction
   │        │  ├─ backup-dir
   │        │  └─ stash-dir
   │        │     └─ CodefController.class.uniqueId0
   │        └─ previous-compilation-data.bin
   ├─ gradle
   │  └─ wrapper
   │     ├─ gradle-wrapper.jar
   │     └─ gradle-wrapper.properties
   ├─ src
   │  ├─ main
   │  │  ├─ java
   │  │  │  └─ com
   │  │  │     └─ example
   │  │  │        └─ kakao
   │  │  │           ├─ api
   │  │  │           ├─ config
   │  │  │           │  ├─ CodefConfig.java
   │  │  │           │  └─ SecurityConfig.java
   │  │  │           ├─ controller
   │  │  │           │  ├─ CodefController.java
   │  │  │           │  └─ HomeController.java
   │  │  │           ├─ service
   │  │  │           └─ KakaoApplication.java
   │  │  └─ resources
   │  │     ├─ static
   │  │     ├─ templates
   │  │     │  ├─ codef-contract-info.mustache
   │  │     │  ├─ codef-create-cert.mustache
   │  │     │  ├─ index.mustache
   │  │     │  └─ success.mustache
   │  │     └─ application.properties
   │  └─ test
   │     └─ java
   │        └─ com
   │           └─ example
   │              └─ kakao
   │                 └─ KakaoApplicationTests.java
   ├─ .gitattributes
   ├─ .gitignore
   ├─ build.gradle
   ├─ gradlew
   ├─ gradlew.bat
   ├─ HELP.md
   └─ settings.gradle
```

> 🔎 자동 스캔된 주요 연동 파일(추정)
```
kakao/HELP.md
kakao/build.gradle
kakao/settings.gradle
kakao/build/resources/main/application.properties
kakao/src/test/java/com/example/kakao/KakaoApplicationTests.java
kakao/src/main/resources/application.properties
kakao/src/main/java/com/example/kakao/KakaoApplication.java
kakao/src/main/java/com/example/kakao/config/SecurityConfig.java
kakao/src/main/java/com/example/kakao/config/CodefConfig.java
kakao/src/main/java/com/example/kakao/controller/CodefController.java
kakao/src/main/java/com/example/kakao/controller/HomeController.java
```

---

## 1. Kakao Developers 설정

1) https://developers.kakao.com → **내 애플리케이션** → **애플리케이션 추가**  
2) **플랫폼** → **Web** 추가, 사이트 도메인 등록 (예: `http://localhost:8080`)  
3) **카카오 로그인** 활성화 → **Redirect URI** 등록  
   - 예시:  
     - `http://localhost:8080/login/oauth2/code/kakao`  
4) **동의 항목**에서 필요한 프로필 항목(이름, 성별, 생년 등)을 **선택 동의/필수 동의**로 설정  
5) **REST API 키** 확인

> ⚠️ REST API 키/클라이언트 시크릿은 절대 깃에 올리지 마세요. 이 저장소는 `application.yml.template`를 제공하니 복사해 사용하세요.

---

## 2. Spring Boot 의존성

Gradle 예시:
```gradle
dependencies {{
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'
    implementation 'org.springframework.boot:spring-boot-starter-security'
    // (선택) 템플릿 엔진 사용 시
    implementation 'org.springframework.boot:spring-boot-starter-thymeleaf'
}}
```

---

## 3. application.yml 설정

`src/main/resources/application.yml` 대신, 이 저장소의 **`application.yml.template`**를 복사하여 **`application.yml`**로 사용하세요.

```yaml
server:
  port: 8080

spring:
  security:
    oauth2:
      client:
        registration:
          kakao:
            client-id: "{{REST_API_KEY}}"           # 카카오 REST API 키
            client-secret: "{{CLIENT_SECRET?}}"     # 선택: 보통 미사용 (비워도 됨)
            redirect-uri: "{{baseUrl}}/login/oauth2/code/kakao"
            authorization-grant-type: authorization_code
            client-authentication-method: POST
            client-name: Kakao
            scope: [ profile_nickname, account_email, gender, birthday, birthyear ]
        provider:
          kakao:
            authorization-uri: https://kauth.kakao.com/oauth/authorize
            token-uri: https://kauth.kakao.com/oauth/token
            user-info-uri: https://kapi.kakao.com/v2/user/me
            user-name-attribute: id
  thymeleaf:
    cache: false
```

- **`{{baseUrl}}`**: 로컬은 보통 `http://localhost:8080`
- **scope**는 Kakao Developers **동의 항목**과 일치해야 합니다.

> 🔐 `application.yml`은 비공개로 관리하세요. 이 저장소에는 업로드 금지되도록 `.gitignore`가 포함되어 있습니다.

---

## 4. Security 설정 (예시)

```java
// SecurityConfig.java
import org.springframework.context.annotation.Bean;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SecurityConfig {{
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http
            .authorizeHttpRequests((auth) -> auth
                .requestMatchers("/", "/css/**", "/js/**", "/images/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2Login(Customizer.withDefaults())
            .logout((logout) -> logout.logoutSuccessUrl("/"));

        return http.build();
    }}
}}
```

---

## 5. 로그인 성공 처리 & 사용자 속성 매핑 (예시)

```java
// MainController.java
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Map;

@Controller
public class MainController {{

    @GetMapping("/")
    public String home() {{
        return "main";  // src/main/resources/templates/main.html
    }}

    @GetMapping("/login/success")
    public String success(@AuthenticationPrincipal OAuth2User user, Model model) {{
        if (user != null) {{
            Map<String, Object> attrs = user.getAttributes();
            Map<String, Object> kakaoAccount = (Map<String, Object>) attrs.get("kakao_account");

            String name = getStr(kakaoAccount, "name");
            String gender = getStr(kakaoAccount, "gender");
            String birthyear = getStr(kakaoAccount, "birthyear");

            model.addAttribute("name", name);
            model.addAttribute("gender", gender);
            model.addAttribute("birthyear", birthyear);
        }}
        return "success"; // src/main/resources/templates/success.html
    }}

    private String getStr(Map<String, Object> map, String key) {{
        if (map == null) return null;
        Object v = map.get(key);
        return v == null ? null : String.valueOf(v);
    }}
}}
```

템플릿 예시(`success.html`):
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><meta charset="UTF-8"><title>Login Success</title></head>
<body>
<h2>카카오 로그인 성공</h2>
<p th:text="'이름: ' + {{name}}"></p>
<p th:text="'성별: ' + {{gender}}"></p>
<p th:text="'출생연도: ' + {{birthyear}}"></p>
<a href="/">메인으로</a>
</body>
</html>
```

> 🔁 기본 성공 URL은 `/login/oauth2/code/kakao` → Spring Security가 내부 처리 후 기본 페이지로 리다이렉트합니다.  
> 커스텀 성공 URL을 원하면 `oauth2Login().defaultSuccessUrl("/login/success", true)`로 지정하세요.

---

## 6. 로컬 실행

```bash
./gradlew bootRun
# or
./mvnw spring-boot:run
```

- `http://localhost:8080` 접속 → **로그인** → 카카오 계정 인증 → **/login/success** 에서 프로필 확인

---

## 7. 자주 발생하는 오류

- **invalid_client / invalid_redirect**  
  - Kakao Developers의 **Redirect URI**가 애플리케이션 설정과 일치하는지 확인  
- **동의 항목 값이 비어 있음**  
  - 동의 항목이 **미설정**이거나 **필수/선택**이 실제 scope와 불일치  
- **키 유출 위험**  
  - `application.yml`을 깃에 올리지 마세요. 템플릿을 복사해 로컬에서만 유지

---

## 8. GitHub 업로드 가이드

**새 리포지토리**로 올리는 방법:
```bash
git init
git add .
git commit -m "feat: kakao login sample (spring security oauth2)"
git branch -M main
git remote add origin https://github.com/<YOUR_ID>/<REPO>.git
git push -u origin main
```

**기존 리포지토리**에 폴더 추가:
```bash
# 현재 프로젝트 루트에서 (예: Desktop/Insurance)
mkdir -p docs/kakao-login
# 이 README와 템플릿, 샘플 코드를 복사
# 커밋 & 푸시
git add docs/kakao-login
git commit -m "docs: add kakao login guide"
git push
```

---

## 9. 디렉터리 제안 (예시)

```
kakao-login/
├─ README.md
├─ application.yml.template
├─ src/
│  ├─ main/java/.../SecurityConfig.java
│  ├─ main/java/.../MainController.java
│  └─ main/resources/templates/{{main.html, success.html}}
└─ build.gradle (or pom.xml)
```

---

## 10. 라이선스

MIT 또는 Apache-2.0 등 목적에 맞는 라이선스를 선택해 `LICENSE` 파일을 추가하세요.





