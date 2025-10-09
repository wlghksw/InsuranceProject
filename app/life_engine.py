# -*- coding: utf-8 -*-
"""
종신보험 KNN 추천 엔진
FastAPI 엔드포인트로 사용 가능
"""

from pathlib import Path
import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from difflib import get_close_matches
from typing import List, Dict, Any


class LifeInsuranceEngine:
    """종신보험 KNN 추천 엔진 클래스"""
    
    def __init__(self, csv_path: str = None):
        """
        초기화 및 KNN 모델 학습
        
        Args:
            csv_path: 종신보험 데이터 CSV 파일 경로
        """
        # CSV 경로 탐색
        if csv_path is None:
            ROOT = Path(__file__).parent
            candidates = [
                os.environ.get("INS_CSV_PATH"),
                ROOT.parent / "data" / "csv" / "analysis.csv",
                ROOT / "csv" / "insurance_core.csv",
                ROOT / "insurance_core.csv"
            ]
            
            for c in candidates:
                if not c:
                    continue
                p = Path(c).expanduser().resolve()
                if p.exists():
                    csv_path = str(p)
                    break
        
        if not csv_path or not Path(csv_path).exists():
            raise FileNotFoundError("종신보험 데이터 파일을 찾을 수 없습니다.")
        
        # CSV 불러오기
        self.insurance_df = pd.read_csv(csv_path)
        
        # 전처리: 문자열을 숫자로 변환
        self.job = LabelEncoder()
        self.jobrisk = LabelEncoder()
        self.product = LabelEncoder()
        self.gender = LabelEncoder()
        
        self.insurance_df["직업"] = self.job.fit_transform(self.insurance_df["직업"])
        self.insurance_df["직업 위험도"] = self.jobrisk.fit_transform(self.insurance_df["직업 위험도"])
        self.insurance_df["상품명"] = self.product.fit_transform(self.insurance_df["상품명"])
        self.insurance_df["성별"] = self.gender.fit_transform(self.insurance_df["성별"])
        
        # KNN 모델 학습
        self._train_knn_models()
        
        # 직업-위험도 매핑
        self.job2risk_lookup = self._build_job_to_risk_lookup()
    
    def _train_knn_models(self):
        """성별별 KNN 모델 학습"""
        # 여자 데이터셋
        self.df_f = self.insurance_df[self.insurance_df["성별"]==0].copy()
        X_f = self.df_f[["여자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
        self.scaler_f = StandardScaler().fit(X_f)
        self.X_f_scaled = self.scaler_f.transform(X_f)
        self.knn_f = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(self.X_f_scaled)
        
        # 남자 데이터셋
        self.df_m = self.insurance_df[self.insurance_df["성별"]==1].copy()
        X_m = self.df_m[["남자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
        self.scaler_m = StandardScaler().fit(X_m)
        self.X_m_scaled = self.scaler_m.transform(X_m)
        self.knn_m = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(self.X_m_scaled)
    
    def _build_job_to_risk_lookup(self, job_col="직업(원문)", risk_col="직업 위험도(원문)"):
        """직업별 위험도 매핑 딕셔너리 생성"""
        if job_col in self.insurance_df.columns and risk_col in self.insurance_df.columns:
            return self.insurance_df.groupby(job_col)[risk_col].agg(lambda s: s.mode().iloc[0]).to_dict()
        return None

    def _coerce_gender(self, g):
        """성별 문자열을 숫자로 변환"""
        if isinstance(g, str):
            g = g.strip()
            if g in ("남", "남자", "M", "male", "Male"):
                return 1
            if g in ("여", "여자", "F", "female", "Female"):
                return 0
            raise ValueError(f"성별 해석 불가: {g}")
        return int(g)
    
    def _to_job_code(self, job_text):
        """직업 문자열을 코드로 변환"""
        labels = list(self.job.classes_)
        if job_text in labels:
            return int(self.job.transform([job_text])[0])
        cand = get_close_matches(job_text, labels, n=1, cutoff=0.6)
        if not cand:
            raise ValueError(f"알 수 없는 직업: {job_text}")
        return int(self.job.transform([cand[0]])[0])
    
    def _infer_risk_from_job(self, job_text):
        """직업으로부터 위험도 추론"""
        if self.job2risk_lookup and job_text in self.job2risk_lookup:
            risk_text = self.job2risk_lookup[job_text]
            return int(self.jobrisk.transform([risk_text])[0])
        try:
            j_code = self._to_job_code(job_text)
        except:
            return None
        sub = self.insurance_df[self.insurance_df["직업"] == j_code]
        if sub.empty:
            return None
        mode_val = sub["직업 위험도"].mode()
        return int(mode_val.iloc[0]) if not mode_val.empty else None
    
    def _restore_product_names(self, series_like):
        """인코딩된 상품명을 원래 이름으로 복원"""
        try:
            if series_like.dtype == object:
                return series_like
            return pd.Series(self.product.inverse_transform(series_like.astype(int)), index=series_like.index)
        except Exception:
            return series_like
    
    def recommend(self, gender_input: str, premium: int, coverage: int, age: int, 
                  job_text: str, k: int = 5, sort_by: str = "distance") -> List[Dict[str, Any]]:
        """
        종신보험 추천 (FastAPI용)
        
        Args:
            gender_input: 성별 ("남자" 또는 "여자")
            premium: 희망 보험료
            coverage: 희망 보장금액
            age: 나이
            job_text: 직업
            k: 추천 개수
            sort_by: 정렬 기준 ("distance", "premium", "coverage")
        
        Returns:
            추천 상품 리스트
        """
        g = self._coerce_gender(gender_input)
        j_code = self._to_job_code(job_text)
        r_code = self._infer_risk_from_job(job_text)
        if r_code is None:
            r_code = int(self.insurance_df["직업 위험도"].mode().iloc[0])
        
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
        
        mask = pool_df[premium_col] <= float(premium)
        idxs = np.where(mask.values)[0]
        
        if len(idxs) == 0:
            return []
        
        diffs = X_pool_scaled[idxs] - q_scaled
        dists = np.linalg.norm(diffs, axis=1)
        
        rec_rows = pool_df.iloc[idxs].copy()
        rec_rows["상품명"] = self._restore_product_names(rec_rows["상품명"])
        rec_rows["_distance"] = dists
        
        if sort_by == "premium":
            rec_rows["_sortkey"] = (rec_rows[premium_col] - premium).abs()
        elif sort_by == "coverage":
            rec_rows["_sortkey"] = (rec_rows["지급금액"] - coverage).abs()
        else:  # distance
            rec_rows["_sortkey"] = rec_rows["_distance"]
        
        rec_rows = rec_rows.sort_values(by="_sortkey", ascending=True).head(k)
        
        # 결과를 딕셔너리 리스트로 변환
        results = []
        for _, row in rec_rows.iterrows():
            item = {
                "product": str(row["상품명"]),
                "premium": int(row[premium_col]),
                "coverage": int(row["지급금액"]),
                "age": int(row["나이"]),
                "distance": float(row["_distance"])
            }
            if "직업(원문)" in row:
                item["job"] = str(row["직업(원문)"])
            if "직업 위험도(원문)" in row:
                item["risk"] = str(row["직업 위험도(원문)"])
            results.append(item)
        
        return results


# === 테스트 및 직접 실행용 ===
if __name__ == "__main__":
    # 테스트 모드
    print("=== 종신보험 KNN 추천 엔진 테스트 ===")
    engine = LifeInsuranceEngine()
    
    results = engine.recommend(
        gender_input="남자",
        premium=50000,
        coverage=20000000,
        age=25,
        job_text="사무직",
        k=10,
        sort_by="coverage"
    )
    
    print(f"\n추천 결과: {len(results)}개")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['product']}")
        print(f"   보험료: {item['premium']:,}원, 보장금액: {item['coverage']:,}원")
        print()