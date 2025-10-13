# -*- coding: utf-8 -*-

from pathlib import Path
import os, sys, json
import pandas as pd
import numpy as np
from difflib import get_close_matches
from sklearn.preprocessing import LabelEncoder, StandardScaler

def _write_json_line(obj: dict):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def _ok(payload: dict):
    _write_json_line({"status": "ok", **payload})

def _err(msg: str):
    _write_json_line({"status": "error", "message": msg})

def _debug_log(msg: str):
    sys.stderr.write(str(msg) + "\n")
    sys.stderr.flush()

ROOT = Path(__file__).parent
candidates = [
    os.environ.get("INS_CSV_PATH"),
    ROOT / "csv" / "insurance_core.csv",
    ROOT / "insurance_core.csv",
    ]
CSV_PATH = None
for c in candidates:
    if not c:
        continue
    p = Path(c).expanduser().resolve()
    if p.exists():
        CSV_PATH = str(p)
        break

if not CSV_PATH:
    _err("insurance_core.csv not found")
    sys.exit(1)

try:
    insurance_df = pd.read_csv(CSV_PATH)
except Exception as e:
    _err(f"csv_read_error: {e}")
    sys.exit(1)

NUM_COLS = ["남자(보험료)", "여자(보험료)", "지급금액", "나이"]
for col in NUM_COLS:
    if col in insurance_df.columns:
        insurance_df[col] = (
            insurance_df[col].astype(str).str.replace(",", "", regex=False).str.strip()
        )
        insurance_df[col] = pd.to_numeric(insurance_df[col], errors="coerce")

required_cols = {"상품명","성별","나이","지급금액","직업","직업 위험도","남자(보험료)","여자(보험료)"}
missing = [c for c in required_cols if c not in insurance_df.columns]
if missing:
    _err(f"missing_columns: {', '.join(missing)}")
    sys.exit(1)

before_rows = len(insurance_df)
insurance_df = insurance_df.dropna(subset=["지급금액", "나이"])
insurance_df = insurance_df[~(insurance_df["남자(보험료)"].isna() & insurance_df["여자(보험료)"].isna())]
_debug_log(f"[clean] rows: {before_rows} -> {len(insurance_df)} after cleaning")

def _normalize_gender_label(x):
    if pd.isna(x):
        return x
    s = str(x).strip().lower()
    if s in {"남","남자","m","male","man","boy"}:
        return "남"
    if s in {"여","여자","f","female","woman","girl"}:
        return "여"
    return x

insurance_df["성별"] = insurance_df["성별"].apply(_normalize_gender_label)

job = LabelEncoder()
jobrisk = LabelEncoder()
product = LabelEncoder()
gender = LabelEncoder()

try:
    insurance_df["직업"] = job.fit_transform(insurance_df["직업"])
    insurance_df["직업 위험도"] = jobrisk.fit_transform(insurance_df["직업 위험도"])
    insurance_df["상품명"] = product.fit_transform(insurance_df["상품명"])
    insurance_df["성별"] = gender.fit_transform(insurance_df["성별"])
except Exception as e:
    _err(f"label_encode_error: {e}")
    sys.exit(1)

try:
    insurance_df["직업(원문)"] = job.inverse_transform(insurance_df["직업"].astype(int))
    insurance_df["직업 위험도(원문)"] = jobrisk.inverse_transform(insurance_df["직업 위험도"].astype(int))
    insurance_df["상품명(원문)"] = product.inverse_transform(insurance_df["상품명"].astype(int))
except Exception:
    if "직업(원문)" not in insurance_df.columns:
        insurance_df["직업(원문)"] = insurance_df["직업"]
    if "직업 위험도(원문)" not in insurance_df.columns:
        insurance_df["직업 위험도(원문)"] = insurance_df["직업 위험도"]
    if "상품명(원문)" not in insurance_df.columns:
        insurance_df["상품명(원문)"] = insurance_df["상품명"]

def _get_gender_codes():
    try:
        male_code   = int(gender.transform(["남"])[0])
        female_code = int(gender.transform(["여"])[0])
        return male_code, female_code
    except Exception:
        classes_raw = list(gender.classes_)
        classes = [str(c).strip().lower() for c in classes_raw]
        male_aliases = {"남","남자","m","male","man","boy"}
        female_aliases = {"여","여자","f","female","woman","girl"}
        male_label = next((classes_raw[i] for i, s in enumerate(classes) if s in male_aliases), None)
        female_label = next((classes_raw[i] for i, s in enumerate(classes) if s in female_aliases), None)
        if male_label is None or female_label is None:
            _err("gender_label_error: CSV 성별 라벨에서 남/여를 식별할 수 없습니다.")
            sys.exit(1)
        return int(gender.transform([male_label])[0]), int(gender.transform([female_label])[0])

male_code, female_code = _get_gender_codes()

def build_job_to_risk_lookup(df, job_col="직업(원문)", risk_col="직업 위험도(원문)"):
    return df.groupby(job_col)[risk_col].agg(lambda s: s.mode().iloc[0]).to_dict()

job2risk_lookup = build_job_to_risk_lookup(insurance_df)

# 여자
df_f = insurance_df[insurance_df["성별"] == female_code].copy()
if df_f.empty:
    _err("no_female_rows_in_dataset")
    sys.exit(1)
num_cols_f = ["여자(보험료)", "지급금액", "나이"]
Xnum_f = df_f[num_cols_f].astype(float).values
scaler_num_f = StandardScaler().fit(Xnum_f)
Xnum_f_scaled = scaler_num_f.transform(Xnum_f)
cat_job_f  = df_f["직업"].astype(int).to_numpy()
cat_risk_f = df_f["직업 위험도"].astype(int).to_numpy()

# 남자
df_m = insurance_df[insurance_df["성별"] == male_code].copy()
if df_m.empty:
    _err("no_male_rows_in_dataset")
    sys.exit(1)
num_cols_m = ["남자(보험료)", "지급금액", "나이"]
Xnum_m = df_m[num_cols_m].astype(float).values
scaler_num_m = StandardScaler().fit(Xnum_m)
Xnum_m_scaled = scaler_num_m.transform(Xnum_m)
cat_job_m  = df_m["직업"].astype(int).to_numpy()
cat_risk_m = df_m["직업 위험도"].astype(int).to_numpy()

def _coerce_gender(g):
    if isinstance(g, str):
        s = g.strip().lower()
        if s in {"남","남자","m","male"}:
            return male_code
        if s in {"여","여자","f","female"}:
            return female_code
        raise ValueError(f"성별 해석 불가: {g}")
    return int(g)

def _to_job_code(job_text: str) -> int:
    labels = [str(x).strip() for x in job.classes_]
    s = str(job_text).strip()
    if s in labels:
        return int(job.transform([s])[0])
    cand = get_close_matches(s, labels, n=1, cutoff=0.5)
    if cand:
        return int(job.transform([cand[0]])[0])
    raise ValueError(f"알 수 없는 직업: {job_text}")

def _fallback_job_code_for_pool(pool_df: pd.DataFrame) -> int:
    return int(pool_df["직업"].mode().iloc[0])

def _infer_risk_from_job(job_text: str):
    if job2risk_lookup and job_text in job2risk_lookup:
        try:
            risk_text = job2risk_lookup[job_text]
            return int(jobrisk.transform([risk_text])[0])
        except Exception:
            pass
    try:
        j_code = _to_job_code(job_text)
    except Exception:
        return None
    sub = insurance_df[insurance_df["직업"] == j_code]
    if sub.empty:
        return None
    mode_val = sub["직업 위험도"].mode()
    return int(mode_val.iloc[0]) if not mode_val.empty else None

def _restore_products(series_like: pd.Series) -> pd.Series:
    try:
        if series_like.dtype == object:
            return series_like
        return pd.Series(product.inverse_transform(series_like.astype(int)), index=series_like.index)
    except Exception:
        return series_like

def _restore_risk_text(code_series: pd.Series) -> pd.Series:
    try:
        return pd.Series(jobrisk.inverse_transform(code_series.astype(int)), index=code_series.index)
    except Exception:
        return code_series

def _restore_job_text(code_series: pd.Series) -> pd.Series:
    try:
        return pd.Series(job.inverse_transform(code_series.astype(int)), index=code_series.index)
    except Exception:
        return code_series

def _normalize_sort_by(v: str) -> str:
    if not v:
        return "distance"
    s = str(v).strip().lower()
    s0 = s.replace(" ", "")
    mapping0 = {
        "종합":"distance", "overall":"distance", "distance":"distance",
        "보험가까운순":"premium", "보험료가까운순":"premium",
        "보험근접":"premium", "보험료근접":"premium",
        "premium":"premium", "premiumnear":"premium",
        "보장금액가까운순":"coverage", "지급금액가까운순":"coverage",
        "보장근접":"coverage", "지급금액근접":"coverage",
        "보장금액정렬순":"coverage", "지급금액정렬순":"coverage",
        "coverage":"coverage", "coveragenear":"coverage",
    }
    if s0 in mapping0:
        return mapping0[s0]
    mapping = {
        "종합":"distance", "overall":"distance", "distance":"distance",
        "보험 가까운순":"premium", "보험료 가까운순":"premium",
        "보장금액 가까운순":"coverage", "지급금액 가까운순":"coverage",
        "보장금액 정렬순":"coverage", "지급금액 정렬순":"coverage",
        "premium":"premium", "coverage":"coverage",
    }
    return mapping.get(s, "distance")

def _auto_scale_value(val: float, ref_series: pd.Series, name: str, choices=(1, 10, 100)):

    try:
        med = float(np.nanmedian(pd.to_numeric(ref_series, errors="coerce")))
    except Exception:
        return val, 1, None
    if not np.isfinite(med) or med == 0:
        return val, 1, None
    cands = [val * c for c in choices]
    diffs = [abs(med - c) for c in cands]
    idx   = int(np.argmin(diffs))
    return cands[idx], choices[idx], med

def recommend_top_k(
        gender_input,
        premium,
        coverage,
        age,
        job_text,
        k=5,
        sort_by="종합",
        risk_weight=5.0,
        job_weight=2.0,
        risk_filter=True,
        job_filter=True,
        unique_products=True,
        autoscale=False
):
    g = _coerce_gender(gender_input)
    if g == female_code:
        premium_col = "여자(보험료)"
        pool_df = df_f
        X_pool_scaled = Xnum_f_scaled
        pool_job = cat_job_f
        pool_risk = cat_risk_f
        scaler_num = scaler_num_f
    else:
        premium_col = "남자(보험료)"
        pool_df = df_m
        X_pool_scaled = Xnum_m_scaled
        pool_job = cat_job_m
        pool_risk = cat_risk_m
        scaler_num = scaler_num_m

    try:
        j_code = _to_job_code(job_text)
    except Exception:
        j_code = _fallback_job_code_for_pool(pool_df)
        job_filter = False

    r_code = _infer_risk_from_job(job_text)
    if r_code is None:
        r_code = int(pool_df["직업 위험도"].mode().iloc[0])

    premium = float(premium)
    coverage = float(coverage)
    age = float(age)

    if autoscale:
        premium, prem_scale, prem_med = _auto_scale_value(premium, pool_df[premium_col], "premium", choices=(1,10,100))
        coverage, cov_scale,  cov_med = _auto_scale_value(coverage, pool_df["지급금액"], "coverage", choices=(1,10,100))
    else:
        prem_scale, prem_med = 1, None
        cov_scale,  cov_med  = 1, None

    premium_used = premium
    coverage_used = coverage

    q_num = np.array([[premium_used, coverage_used, age]], dtype=float)
    q_num_scaled = scaler_num.transform(q_num)

    key = _normalize_sort_by(sort_by)

    prem_band = max(5_000, premium_used * 0.30)
    cov_band  = max(10_000_000, coverage_used * 0.30)
    age_band  = max(1.0, age * 0.15)

    if key == "premium":
        idx_all = np.where((np.abs(pool_df[premium_col] - premium_used) <= prem_band).values)[0]
        if len(idx_all) < k:
            idx_all = np.argsort((pool_df[premium_col] - premium_used).abs().values)[:max(k*10, 100)]
    elif key == "coverage":
        idx_all = np.where((np.abs(pool_df["지급금액"] - coverage_used) <= cov_band).values)[0]
        if len(idx_all) < k:
            idx_all = np.argsort((pool_df["지급금액"] - coverage_used).abs().values)[:max(k*10, 100)]
    else:
        cond = (
                (pool_df[premium_col].sub(premium_used).abs().values <= prem_band) &
                (pool_df["지급금액"].sub(coverage_used).abs().values <= cov_band) &
                (pool_df["나이"].sub(age).abs().values <= age_band)
        )
        idx_tmp = np.where(cond)[0]
        if len(idx_tmp) >= max(k*3, 30):
            idx_all = idx_tmp
        else:
            idx_age = np.where((np.abs(pool_df["나이"] - age) <= age_band).values)[0]
            if len(idx_age) >= max(k*3, 30):
                idx_all = idx_age
            else:
                idx_all = np.arange(len(pool_df))

    if len(idx_all) == 0:
        cols = ["상품명","보험료","지급금액","나이","직업(원문)","직업 위험도(원문)"]
        return pd.DataFrame(columns=cols)

    def _stage_indices():
        base = idx_all
        if job_filter:
            same_job = base[(pool_job[base] == j_code)]
            if len(same_job) > 0:
                same_job_same_risk = same_job[(pool_risk[same_job] == r_code)]
                if len(same_job_same_risk) > 0:
                    yield same_job_same_risk
                    if len(same_job_same_risk) >= k: return
                adj_risk = same_job[(np.abs(pool_risk[same_job] - r_code) == 1)]
                if len(adj_risk) > 0:
                    yield adj_risk
                    if len(adj_risk) + len(same_job_same_risk) >= k: return

        if risk_filter:
            same_risk = base[(pool_risk[base] == r_code)]
            if len(same_risk) > 0:
                yield same_risk
                if len(same_risk) >= k: return
            adj_risk = base[(np.abs(pool_risk[base] - r_code) == 1)]
            if len(adj_risk) > 0:
                yield adj_risk
                if len(adj_risk) + len(same_risk) >= k: return

        yield base

    selected_idxs = np.array([], dtype=int)
    for bucket in _stage_indices():
        selected_idxs = np.unique(np.concatenate([selected_idxs, bucket])) if selected_idxs.size else np.array(bucket, dtype=int)
        if len(selected_idxs) >= k:
            break

    num_diffs = X_pool_scaled[selected_idxs] - q_num_scaled
    if key == "premium":
        w = np.array([1.0, 0.0, 0.2], dtype=float)
    elif key == "coverage":
        w = np.array([0.0, 1.0, 0.3], dtype=float)
    else:
        w = np.array([0.8, 0.8, 0.4], dtype=float)

    weighted_diffs = num_diffs * w
    num_dists = np.linalg.norm(weighted_diffs, axis=1)

    risk_diff = np.abs(pool_risk[selected_idxs] - r_code).astype(float)
    job_mismatch = (pool_job[selected_idxs] != j_code).astype(float)
    total_score = num_dists + risk_weight * risk_diff + job_weight * job_mismatch

    rec_rows = pool_df.iloc[selected_idxs].copy()
    rec_rows["상품명"] = _restore_products(rec_rows["상품명"])
    if "직업(원문)" not in rec_rows.columns:
        rec_rows["직업(원문)"] = _restore_job_text(rec_rows["직업"])
    if "직업 위험도(원문)" not in rec_rows.columns:
        rec_rows["직업 위험도(원문)"] = _restore_risk_text(rec_rows["직업 위험도"])
    rec_rows["_score"] = total_score

    if key == "premium":
        rec_rows["_prem_gap"] = (rec_rows[premium_col] - premium_used).abs()
        rec_rows = rec_rows.sort_values(by=["_prem_gap", "_score"], ascending=[True, True]).drop(columns=["_prem_gap"])
    elif key == "coverage":
        rec_rows["_cov_gap"] = (rec_rows["지급금액"] - coverage_used).abs()
        rec_rows = rec_rows.sort_values(by=["_cov_gap", "_score"], ascending=[True, True]).drop(columns=["_cov_gap"])
    else:
        rec_rows = rec_rows.sort_values(by="_score", ascending=True)

    if unique_products and "상품명" in rec_rows.columns:
        rec_rows = rec_rows.drop_duplicates(subset=["상품명"], keep="first")

    rec_rows = rec_rows.head(int(k))
    rec_rows = rec_rows.assign(보험료=rec_rows[premium_col])
    show_cols = ["상품명","보험료","지급금액","나이","직업(원문)","직업 위험도(원문)"]
    return rec_rows[show_cols].reset_index(drop=True)

def main_loop():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            _err(f"bad_request: {e}")
            continue

        try:
            gender_input = req.get("gender") or req.get("성별")
            age         = req.get("age") or req.get("나이")
            job_text    = req.get("job") or req.get("직업")
            premium_raw = req.get("desiredPremium") or req.get("premium") or req.get("보험료")
            coverage_raw= req.get("desiredCoverage") or req.get("coverage") or req.get("지급금액")

            premium     = float(premium_raw)
            coverage    = float(coverage_raw)

            k           = int(req.get("k", req.get("topk", 5)))
            sort_by_raw = (req.get("sort_by") or req.get("sortBy") or req.get("sort")
                           or req.get("order") or req.get("정렬") or req.get("정렬순") or "종합")
            sort_by_norm= _normalize_sort_by(sort_by_raw)
            risk_weight = float(req.get("risk_weight", 5.0))
            job_weight  = float(req.get("job_weight", 2.0))
            risk_filter = bool(req.get("risk_filter", True))
            job_filter  = bool(req.get("job_filter", True))
            unique_products = bool(req.get("unique_products", True))
            autoscale  = bool(req.get("autoscale", False))
            debug_flag = bool(req.get("debug", False))

            if gender_input is None or age is None or job_text is None or premium is None or coverage is None:
                _err("missing_fields: need gender, age, job, premium, coverage")
                continue

            df = recommend_top_k(
                gender_input=gender_input,
                premium=premium,
                coverage=coverage,
                age=float(age),
                job_text=str(job_text),
                k=k,
                sort_by=str(sort_by_norm),
                risk_weight=risk_weight,
                job_weight=job_weight,
                risk_filter=risk_filter,
                job_filter=job_filter,
                unique_products=unique_products,
                autoscale=autoscale,
            )

            records = json.loads(df.to_json(orient="records", force_ascii=False))
            payload = {"top": records, "items": records}

            if debug_flag:
                payload["meta"] = {
                    "sort_by_input": sort_by_raw,
                    "sort_by_used": sort_by_norm,
                    "k": k,
                    "returned": len(records),
                    "gender_input": str(gender_input),
                    "job_text": str(job_text),
                    "premium_input_raw": float(premium_raw),
                    "coverage_input_raw": float(coverage_raw),
                    "autoscale": autoscale,
                    "premium_used": float(premium),
                    "coverage_used": float(coverage),
                    "risk_weight": risk_weight,
                    "job_weight": job_weight,
                    "risk_filter": risk_filter,
                    "job_filter": job_filter,
                    "unique_products": unique_products,
                }

            _ok(payload)

        except Exception as e:
            _err(f"server_error: {e}")

if __name__ == "__main__":
    main_loop()
