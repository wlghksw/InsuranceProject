**종신 보험 맞춤 추천**

간단한 KNN 기반의 종신보험을 추천
CSV의 스키마에 맞춰 라벨 인코딩/스케일링을 수행하고, 
사용자의 입력(성별, 희망 보험료, 지급금액, 나이, 직업)을 기준으로 가까운 상품 Top‑K를 추천하는 기능

**추천 로직**

성별 분리 스케일링: 남/녀 풀을 분리하여 각각 StandardScaler로 정규화 후 KNN 거리 기반 근접도 계산

직업 위험도 추정: 직업명→위험도 매핑이 애매할 경우, 동일 직업의 위험도를 사용

정렬 옵션: distance(기본), premium(보험료 차 절댓값), coverage(지급금액 차 절댓값)

상품명 복원: 내부적으로 라벨 인코딩하되 결과 출력 시 원래 상품명으로 복원


## Repository 구조

```
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
```

---

## 🚀 사용 방법

### 1) 설치

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2) 데이터 준비

`insurance_core.csv`를 프로젝트 루트 또는 임의 경로에 둡니다. **필수 컬럼**은 아래 `data/README.md` 참고.

### 3) 데모 실행

```bash
python scripts/demo.py --csv ./insurance_core.csv \
  --gender 남자 \
  --premium 50000 \
  --coverage 10000000 \
  --age 25 \
  --job 사무직 \
  --k 10 \
  --sort_by distance
```

출력은 추천 상위 K개 상품 테이블입니다.

### 4) 라이브러리로 사용

```python
from life_insurance_recommender import Recommender
rec = Recommender().fit_csv("./insurance_core.csv")
result = rec.recommend_top_k(
    gender_input="남자",
    premium=50000,
    coverage=10_000_000,
    age=25,
    job_text="사무직",
    k=10,
    sort_by="distance",
)
print(result)
```

---




class Recommender:
    """KNN 유사도 기반 종신보험 추천기."""

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.enc: Optional[_Encoders] = None
        # 성별 풀 분리용
        self.df_f: Optional[pd.DataFrame] = None
        self.df_m: Optional[pd.DataFrame] = None
        self.scaler_f: Optional[StandardScaler] = None
        self.scaler_m: Optional[StandardScaler] = None
        self.X_f_scaled: Optional[np.ndarray] = None
        self.X_m_scaled: Optional[np.ndarray] = None
        self.job2risk_lookup: Optional[dict] = None

    # ---------- Load / Fit ----------
    def fit_csv(self, csv_path: str) -> "Recommender":
        df = pd.read_csv(csv_path)
        return self.fit_df(df)

    def fit_df(self, df: pd.DataFrame) -> "Recommender":
        self.df = df.copy()
        required_cols = [
            "상품명",
            "성별",
            "남자(보험료)",
            "여자(보험료)",
            "지급금액",
            "가입금액",
            "나이",
            "직업",
            "직업 위험도",
        ]
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"CSV에 필수 컬럼 누락: {missing}")

        # Encoders
        job = LabelEncoder()
        jobrisk = LabelEncoder()
        product = LabelEncoder()
        gender = LabelEncoder()

        # Fit encoders on original text
        self.df["직업"] = job.fit_transform(self.df["직업"].astype(str))
        self.df["직업 위험도"] = jobrisk.fit_transform(self.df["직업 위험도"].astype(str))
        self.df["상품명"] = product.fit_transform(self.df["상품명"].astype(str))
        self.df["성별"] = gender.fit_transform(self.df["성별"].astype(str))

        self.enc = _Encoders(job=job, jobrisk=jobrisk, product=product, gender=gender)

        # Optional original columns
        if "직업(원문)" not in self.df.columns:
            try:
                self.df["직업(원문)"] = gender.inverse_transform(self.df["성별"]) * 0  # dummy to create col
                self.df.drop(columns=["직업(원문)"], inplace=True)
            except Exception:
                pass
        # Build job→risk lookup if possible
        self.job2risk_lookup = self._build_job_to_risk_lookup(self.df)

        # Split by gender after encoding: female==0, male==1 (LabelEncoder 기준)
        self.df_f = self.df[self.df["성별"] == 0].copy()
        self.df_m = self.df[self.df["성별"] == 1].copy()

        # Scale features per gender pool
        self._fit_gender_pool()
        return self

    def _build_job_to_risk_lookup(self, df: pd.DataFrame,
                                  job_col: str = "직업(원문)",
                                  risk_col: str = "직업 위험도(원문)") -> Optional[dict]:
        if job_col in df.columns and risk_col in df.columns:
            try:
                return (
                    df.groupby(job_col)[risk_col]
                      .agg(lambda s: s.mode().iloc[0])
                      .to_dict()
                )
            except Exception:
                return None
        return None

    def _fit_gender_pool(self):
        # Female pool
        X_f = self.df_f[["여자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
        self.scaler_f = StandardScaler().fit(X_f)
        self.X_f_scaled = self.scaler_f.transform(X_f)

        # Male pool
        X_m = self.df_m[["남자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
        self.scaler_m = StandardScaler().fit(X_m)
        self.X_m_scaled = self.scaler_m.transform(X_m)

    # ---------- Inference helpers ----------
    def _coerce_gender(self, g) -> int:
        if isinstance(g, str):
            g = g.strip()
            if g in ("남", "남자", "M", "male", "Male"): return 1
            if g in ("여", "여자", "F", "female", "Female"): return 0
            raise ValueError(f"성별 해석 불가: {g}")
        return int(g)

    def _to_job_code(self, job_text: str) -> int:
        assert self.enc is not None
        labels = list(self.enc.job.classes_)
        if job_text in labels:
            return int(self.enc.job.transform([job_text])[0])
        cand = get_close_matches(job_text, labels, n=1, cutoff=0.6)
        if not cand:
            raise ValueError(f"알 수 없는 직업: {job_text}")
        return int(self.enc.job.transform([cand[0]])[0])

    def _infer_risk_from_job(self, job_text: str) -> Optional[int]:
        assert self.enc is not None and self.df is not None
        if self.job2risk_lookup and job_text in self.job2risk_lookup:
            risk_text = self.job2risk_lookup[job_text]
            return int(self.enc.jobrisk.transform([risk_text])[0])
        try:
            j_code = self._to_job_code(job_text)
        except Exception:
            return None
        sub = self.df[self.df["직업"] == j_code]
        if sub.empty:
            return None
        mode_val = sub["직업 위험도"].mode()
        return int(mode_val.iloc[0]) if not mode_val.empty else None

    def _restore_product_names(self, series_like: pd.Series) -> pd.Series:
        assert self.enc is not None
        try:
            if series_like.dtype == object:
                return series_like
            return pd.Series(self.enc.product.inverse_transform(series_like.astype(int)), index=series_like.index)
        except Exception:
            return series_like

    # ---------- Recommend ----------
    def recommend_top_k(
        self,
        gender_input: str | int,
        premium: float,
        coverage: float,
        age: int,
        job_text: str,
        k: int = 5,
        sort_by: SortBy = "distance",
    ) -> pd.DataFrame:
        if self.df is None:
            raise RuntimeError("fit_csv/fit_df 먼저 호출하세요.")
        g = self._coerce_gender(gender_input)
        j_code = self._to_job_code(job_text)
        r_code = self._infer_risk_from_job(job_text)
        if r_code is None:
            r_code = int(self.df["직업 위험도"].mode().iloc[0])

        base_vec = np.array([[float(premium), float(coverage), float(age), float(j_code), float(r_code)]], dtype=float)

        if g == 0:
            premium_col = "여자(보험료)"
            pool_df = self.df_f
            q_scaled = self.scaler_f.transform(base_vec)
            X_pool_scaled = self.X_f_scaled
        else:
            premium_col = "남자(보험료)"
            pool_df = self.df_m
            q_scaled = self.scaler_m.transform(base_vec)
            X_pool_scaled = self.X_m_scaled

        # 예산 이하 필터
        mask = pool_df[premium_col] <= float(premium)
        idxs = np.where(mask.values)[0]
        if len(idxs) == 0:
            cols = ["상품명", premium_col, "지급금액", "나이"]
            if "직업(원문)" in pool_df.columns:
                cols += ["직업(원문)", "직업 위험도(원문)"]
            return pd.DataFrame(columns=cols)

        # 거리 계산
        diffs = X_pool_scaled[idxs] - q_scaled
        dists = np.linalg.norm(diffs, axis=1)

        rec_rows = pool_df.iloc[idxs].copy()
        rec_rows["상품명"] = self._restore_product_names(rec_rows["상품명"])
        rec_rows["_distance"] = dists

        if sort_by == "premium":
            rec_rows["_sortkey"] = (rec_rows[premium_col] - premium).abs()
        elif sort_by == "coverage":
            rec_rows["_sortkey"] = (rec_rows["지급금액"] - coverage).abs()
        else:
            rec_rows["_sortkey"] = rec_rows["_distance"]

        rec_rows = rec_rows.sort_values(by="_sortkey", ascending=True).head(k)

        show_cols = ["상품명", premium_col, "지급금액", "나이"]
        if "직업(원문)" in pool_df.columns:
            show_cols += ["직업(원문)", "직업 위험도(원문)"]
        return rec_rows[show_cols].reset_index(drop=True)
```

## 🧪 `scripts/demo.py`

```python
import argparse
import pandas as pd
from life_insurance_recommender import Recommender

parser = argparse.ArgumentParser()
parser.add_argument("--csv", required=True)
parser.add_argument("--gender", default="남자")
parser.add_argument("--premium", type=float, default=50000)
parser.add_argument("--coverage", type=float, default=10_000_000)
parser.add_argument("--age", type=int, default=25)
parser.add_argument("--job", default="사무직")
parser.add_argument("--k", type=int, default=10)
parser.add_argument("--sort_by", choices=["distance", "premium", "coverage"], default="distance")
args = parser.parse_args()

rec = Recommender().fit_csv(args.csv)
res = rec.recommend_top_k(
    gender_input=args.gender,
    premium=args.premium,
    coverage=args.coverage,
    age=args.age,
    job_text=args.job,
    k=args.k,
    sort_by=args.sort_by,
)

# 깔끔히 출력
pd.set_option("display.max_columns", None)
print(res)
```

---

## 📌 커밋 메시지 예시

* `feat: add KNN-based life-insurance recommender with per-gender scaling`
* `docs: write README and data schema`
* `chore: add requirements and gitignore`

---

필요하면 **패키징(PyPI 배포용)** 설정(`pyproject.toml`)까지 바로 만들어 줄게. 또한 Spring Boot에서 이 파이썬 스크립트를 서브프로세스로 호출 중이면, `scripts/demo.py`를 참고해서 **입력/출력 포맷(JSON 라인)**으로 바꿔주는 버전도 추가해줄 수 있어!

