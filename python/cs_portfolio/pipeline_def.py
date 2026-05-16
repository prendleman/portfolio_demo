"""Feature columns + **sklearn** preprocessing / logistic regression pipeline (no MLflow).

Spark ML twin (StringIndexer, OneHotEncoder, VectorAssembler, ``pyspark.ml`` LogisticRegression)
lives in ``cs_portfolio.sparkml_renewal_variant`` — same ``FEATURE_COLUMNS`` / ``CAT_COLUMNS`` / label ``renewed``.
"""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

FEATURE_COLUMNS = [
    "tenure_months",
    "monthly_rent",
    "rent_to_market_ratio",
    "late_payment_count_12m",
    "work_order_count_12m",
    "prior_renewal_count",
    "bedrooms",
    "is_long_tenure",
    "high_service_load",
]
CAT_COLUMNS = ["metro"]


def build_pipeline() -> Pipeline:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric, FEATURE_COLUMNS),
            ("cat", categorical, CAT_COLUMNS),
        ]
    )

    clf = LogisticRegression(max_iter=200, solver="lbfgs", class_weight="balanced")
    return Pipeline(steps=[("prep", preprocessor), ("clf", clf)])
