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
## 기본 구조 & 의존성
from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
import pandas as pd
from difflib import get_close_matches
from sklearn.preprocessing import LabelEncoder, StandardScaler

데이터 핸들링(pandas/numpy), 문자열 근사 매칭(difflib), 전처리(LabelEncoder, StandardScaler) 사용.

KNN류 거리 계산 전에 숫자화(LabelEncoder), **스케일 통일(StandardScaler)**이 필요.

LabelEncoder는 “문자열→정수”이지만 크기 의미는 없음. 거리 계산에는 투입하지 않고, 설명 필드로만 쓰거나 스케일링 대상에서 분리해 둠.


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


# In[2]:

from google.colab import files
upload = files.upload()


# In[3]:

#4325 rows × 10 columns

insurance_df = pd.read_csv('insurance_core.csv')
insurance_df


# In[4]:

# 결측치는 없음..
insurance_df.info()


# In[5]:

insurance_df.columns


# In[6]:

# 전처리 해야하지만
# 랜덤포레스트 모델 사용할거면 안 해도 됨..
# KNN 분류 모델 할거면 전처리
insurance_df.describe()


# In[7]:

from sklearn.preprocessing import LabelEncoder

# 학습 전 문자열을 숫자로 바꾸는 과정
job = LabelEncoder()
jobrisk = LabelEncoder()
product = LabelEncoder()
gender = LabelEncoder()

insurance_df["직업"] = job.fit_transform(insurance_df["직업"])
insurance_df["직업 위험도"] = jobrisk.fit_transform(insurance_df["직업 위험도"])
insurance_df["상품명"] = product.fit_transform(insurance_df["상품명"])
insurance_df["성별"] = gender.fit_transform(insurance_df["성별"])


# In[8]:

data = insurance_df[['남자(보험료)','지급금액','직업','나이','여자(보험료)','성별','직업 위험도','가입금액']].to_numpy()

target = insurance_df['상품명'].to_numpy()


# In[9]:

data


# In[10]:

target


# In[11]:

# 훈련세트 와 테스트 세트 나누기

# 8:2로 나누기

from sklearn.model_selection import train_test_split

#test_size=0.2 20% 한다.
train_input, test_input, train_target, test_target = train_test_split(data, target, test_size=0.2, random_state=42)


# 전처리 : 표준화하기

from sklearn.preprocessing import StandardScaler

ss = StandardScaler()
ss.fit(train_input) # 훈련데이터에서 훈련한다..

train_scaled = ss.transform(train_input) # 훈련 세트 변환
test_scaled = ss.transform(test_input) # 테스트 세트 변환


from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# 여자 데이터셋
df_f = insurance_df[insurance_df["성별"]==0].copy()
X_f = df_f[["여자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
scaler_f = StandardScaler().fit(X_f)
X_f_scaled = scaler_f.transform(X_f)
knn_f = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(X_f_scaled)

# 남자 데이터셋
df_m = insurance_df[insurance_df["성별"]==1].copy()
X_m = df_m[["남자(보험료)", "지급금액", "나이", "직업", "직업 위험도"]].astype(float).values
scaler_m = StandardScaler().fit(X_m)
X_m_scaled = scaler_m.transform(X_m)
knn_m = NearestNeighbors(n_neighbors=5, metric="euclidean").fit(X_m_scaled)


from sklearn.neighbors import NearestNeighbors
from difflib import get_close_matches
import numpy as np
import pandas as pd

# (선행) 이미 존재: insurance_df, job, jobrisk, product, df_f/df_m, scaler_f/m, knn_f/m

def build_job_to_risk_lookup(df, job_col="직업(원문)", risk_col="직업 위험도(원문)"):
    if job_col in df.columns and risk_col in df.columns:
        return df.groupby(job_col)[risk_col].agg(lambda s: s.mode().iloc[0]).to_dict()
    return None

job2risk_lookup = build_job_to_risk_lookup(insurance_df)

def _coerce_gender(g):
    if isinstance(g, str):
        g = g.strip()
        if g in ("남", "남자", "M", "male", "Male"):
            return 1
        if g in ("여", "여자", "F", "female", "Female"):
            return 0
        raise ValueError(f"성별 해석 불가: {g}")
    return int(g)

def _to_job_code(job_text):
    labels = list(job.classes_)
    if job_text in labels:
        return int(job.transform([job_text])[0])
    cand = get_close_matches(job_text, labels, n=1, cutoff=0.6)
    if not cand:
        raise ValueError(f"알 수 없는 직업: {job_text}")
    return int(job.transform([cand[0]])[0])

def _infer_risk_from_job(job_text):
    if job2risk_lookup and job_text in job2risk_lookup:
        risk_text = job2risk_lookup[job_text]
        return int(jobrisk.transform([risk_text])[0])
    try:
        j_code = _to_job_code(job_text)
    except:
        return None
    sub = insurance_df[insurance_df["직업"] == j_code]
    if sub.empty:
        return None
    mode_val = sub["직업 위험도"].mode()
    return int(mode_val.iloc[0]) if not mode_val.empty else None

def _restore_product_names(series_like):
    """
    series_like: rec_rows["상품명"] (숫자 or 문자열)
    - 이미 문자열이면 그대로 반환
    - 숫자라면 LabelEncoder(product)로 inverse_transform
    - 엣지케이스도 예외 없이 통과
    """
    try:
        # 이미 문자열이면 그대로
        if series_like.dtype == object:
            return series_like
        # 숫자라면 inverse
        return pd.Series(product.inverse_transform(series_like.astype(int)), index=series_like.index)
    except Exception:
        # 만약 product encoder가 없거나 타입 불일치면 원본 유지
        return series_like

def recommend_top_k(gender_input, premium, coverage, age, job_text, k=5, sort_by="distance"):
    """
    sort_by: "distance" | "premium" | "coverage"
      - "distance": (기본값) 전체 피처 벡터 거리 기준
      - "premium": 보험료 차이 절댓값 기준
      - "coverage": 지급금액 차이 절댓값 기준
    """
    g = _coerce_gender(gender_input)
    j_code = _to_job_code(job_text)
    r_code = _infer_risk_from_job(job_text)
    if r_code is None:
        r_code = int(insurance_df["직업 위험도"].mode().iloc[0])

    base_vec = np.array([[float(premium), float(coverage), float(age), float(j_code), float(r_code)]], dtype=float)

    if g == 0:
        premium_col = "여자(보험료)"
        pool_df = df_f
        q_scaled = scaler_f.transform(base_vec)
        X_pool_scaled = X_f_scaled
    else:
        premium_col = "남자(보험료)"
        pool_df = df_m
        q_scaled = scaler_m.transform(base_vec)
        X_pool_scaled = X_m_scaled

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
    rec_rows["상품명"] = _restore_product_names(rec_rows["상품명"])
    rec_rows["_distance"] = dists

    # === 정렬 옵션 ===
    if sort_by == "premium":
        rec_rows["_sortkey"] = (rec_rows[premium_col] - premium).abs()
    elif sort_by == "coverage":
        rec_rows["_sortkey"] = (rec_rows["지급금액"] - coverage).abs()
    else:  # distance
        rec_rows["_sortkey"] = rec_rows["_distance"]

    rec_rows = rec_rows.sort_values(by="_sortkey", ascending=True).head(k)

    show_cols = ["상품명", premium_col, "지급금액", "나이"]
    if "직업(원문)" in pool_df.columns:
        show_cols += ["직업(원문)", "직업 위험도(원문)"]

    return rec_rows[show_cols].reset_index(drop=True)


# In[28]:


res = recommend_top_k(
    gender_input="남자",
    premium=50000,
    coverage=10000000,
    age=25,
    job_text="사무직",
    k=10,                # 추천 개수
    sort_by="distance"    # 정렬 기준: "distance" | "premium" | "coverage"
)

display(res)


google.colab 의존 제거 → 일반 파이썬 패키지로 구조화

성별별(StandardScaler) 스케일링 유지, 직업→위험도 mode 추정 로직 유지/보강

Recommender 클래스로 캡슐화: fit_csv() → recommend_top_k() 사용.

CLI 데모(scripts/demo.py) 제공: 깃허브 README의 커맨드 그대로 실행.

바로 쓰는 순서:

repo 초기화 → 캔버스의 트리/파일들 그대로 생성

insurance_core.csv를 루트에 두고

pip install -r requirements.txt

README에 있는 python scripts/demo.py ... 실행


1) 기본 구조 & 의존성
from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
import pandas as pd
from difflib import get_close_matches
from sklearn.preprocessing import LabelEncoder, StandardScaler
무엇을: 데이터 핸들링(pandas/numpy), 문자열 근사 매칭(difflib), 전처리(LabelEncoder, StandardScaler) 사용.

왜: KNN류 거리 계산 전에 숫자화(LabelEncoder), **스케일 통일(StandardScaler)**이 필요.

주의점: LabelEncoder는 “문자열→정수”이지만 크기 의미는 없음(범주 ID일 뿐). 거리 계산에는 투입하지 않고, 설명 필드로만 쓰거나 스케일링 대상에서 분리해 둠.

## 2) 인코더 묶음과 리코멘더 뼈대

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
        
인코더 4종(직업/위험도/상품/성별)을 하나로 관리하고, 성별 풀 분리/스케일러/스케일된 행렬 보관.

성별별 스케일링을 위해.

인스턴스 상태가 많으니 fit을 먼저 호출하지 않으면 recommend_top_k가 오류 내지 않도록 함.


## 3) 학습 데이터 적재 & 전처리 (fit_csv / fit_df)

def fit_csv(self, csv_path: str) -> "Recommender":
    df = pd.read_csv(csv_path)
    return self.fit_df(df)

def fit_df(self, df: pd.DataFrame) -> "Recommender":
    self.df = df.copy()
    required = ["상품명","성별","남자(보험료)","여자(보험료)","지급금액","가입금액","나이","직업","직업 위험도"]


# 라벨 인코딩
job = LabelEncoder(); jobrisk = LabelEncoder()
product = LabelEncoder(); gender = LabelEncoder()

self.df["직업"] = job.fit_transform(self.df["직업"].astype(str))
self.df["직업 위험도"] = jobrisk.fit_transform(self.df["직업 위험도"].astype(str))
self.df["상품명"] = product.fit_transform(self.df["상품명"].astype(str))
self.df["성별"] = gender.fit_transform(self.df["성별"].astype(str))

self.enc = _Encoders(job=job, jobrisk=jobrisk, product=product, gender=gender)

# 직업→위험도 룩업 & 성별 분리
self.job2risk_lookup = self._build_job_to_risk_lookup(self.df)
self.df_f = self.df[self.df["성별"] == 0].copy()
self.df_m = self.df[self.df["성별"] == 1].copy()
self._fit_gender_pool()


## 4) 성별 풀 스케일링 (_fit_gender_pool)

# Female
X_f = self.df_f[["여자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
self.scaler_f = StandardScaler().fit(X_f)
self.X_f_scaled = self.scaler_f.transform(X_f)

# Male
X_m = self.df_m[["남자(보험료)","지급금액","나이","직업","직업 위험도"]].astype(float).values
self.scaler_m = StandardScaler().fit(X_m)
self.X_m_scaled = self.scaler_m.transform(X_m)


선택 컬럼 의존성 가드

build_job_to_risk_lookup가 직업(원문), 직업 위험도(원문)에 의존 → CSV에 없으면 None으로 동작하도록 이미 처리되어 있음(OK).

결과 표시 시 해당 컬럼이 없으면 자동으로 빼도록 이미 조건문 처리(OK).

성별 인코딩 전제 확인

df_f = 성별==0, df_m = 성별==1은 현재 LabelEncoder 결과가 여자=0, 남자=1일 때 맞음.

실제 CSV 성별 값이 “남/여/M/F” 혼재라도 _coerce_gender가 문자열 처리해서 입력 쪽은 안전.

만약 LabelEncoder가 데이터에 따라 남=0, 여=1로 학습되는 경우가 걱정되면, 성별을 분리하기 전에 문자열을 먼저 남→1, 여→0으로 직접 맵핑함.

