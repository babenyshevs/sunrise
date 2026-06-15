"""
Telco Data Preprocessing Pipeline
Handles common telco data issues: missing values, categorical encoding,
feature engineering for churn/cross-sell models.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Tuple, List, Optional


def generate_synthetic_telco_data(n_customers: int = 100_000, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic telco customer data resembling a Swiss operator."""
    rng = np.random.default_rng(seed)

    data = pd.DataFrame({
        "customer_id": [f"CH{i:08d}" for i in range(n_customers)],
        "tenure_months": rng.integers(1, 120, n_customers),
        "monthly_charge_chf": rng.normal(65, 25, n_customers).clip(19.90, 199.90).round(2),
        "product_type": rng.choice(
            ["mobile_only", "internet_only", "converged", "tv_bundle"],
            n_customers, p=[0.4, 0.25, 0.25, 0.1]
        ),
        "contract_type": rng.choice(
            ["month_to_month", "12_month", "24_month"],
            n_customers, p=[0.45, 0.30, 0.25]
        ),
        "num_support_calls_6m": rng.poisson(1.5, n_customers),
        "data_usage_gb": rng.exponential(15, n_customers).round(1),
        "roaming_usage_chf": rng.exponential(5, n_customers).round(2),
        "days_since_last_interaction": rng.integers(0, 365, n_customers),
        "nps_score": rng.integers(0, 11, n_customers),
        "age": rng.integers(18, 80, n_customers),
        "canton": rng.choice(
            ["ZH", "BE", "VD", "GE", "AG", "SG", "LU", "TI", "VS", "BS"],
            n_customers
        ),
        "language": rng.choice(["DE", "FR", "IT"], n_customers, p=[0.65, 0.25, 0.10]),
        "has_family_plan": rng.choice([0, 1], n_customers, p=[0.7, 0.3]),
        "num_lines": rng.integers(1, 5, n_customers),
    })

    # Introduce realistic missing values
    missing_mask_nps = rng.random(n_customers) < 0.15
    data.loc[missing_mask_nps, "nps_score"] = np.nan

    missing_mask_roaming = rng.random(n_customers) < 0.30
    data.loc[missing_mask_roaming, "roaming_usage_chf"] = np.nan

    return data


def handle_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Handle missing values with telco-aware imputation."""
    df = df.copy()

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            if strategy == "median":
                df[col] = df[col].fillna(df[col].median())
            elif strategy == "mean":
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == "zero":
                df[col] = df[col].fillna(0)

    for col in categorical_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])

    return df


def encode_categoricals(
    df: pd.DataFrame,
    categorical_cols: Optional[List[str]] = None,
    method: str = "onehot"
) -> pd.DataFrame:
    """Encode categorical variables."""
    df = df.copy()

    if categorical_cols is None:
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        # Exclude ID columns
        categorical_cols = [c for c in categorical_cols if "id" not in c.lower()]

    if method == "onehot":
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    elif method == "label":
        le = LabelEncoder()
        for col in categorical_cols:
            df[col] = le.fit_transform(df[col].astype(str))

    return df


def engineer_telco_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create telco-specific features for modeling."""
    df = df.copy()

    # Revenue at risk
    df["annual_revenue"] = df["monthly_charge_chf"] * 12

    # Engagement score (composite)
    df["engagement_score"] = (
        (df["days_since_last_interaction"] < 30).astype(int) * 2 +
        (df["num_support_calls_6m"] == 0).astype(int) * 1 +
        (df["data_usage_gb"] > df["data_usage_gb"].median()).astype(int) * 1
    )

    # Tenure bucket
    df["tenure_bucket"] = pd.cut(
        df["tenure_months"],
        bins=[0, 6, 12, 24, 60, 999],
        labels=["0-6m", "6-12m", "1-2y", "2-5y", "5y+"]
    )

    # High value flag (top 20% by revenue)
    df["is_high_value"] = (
        df["monthly_charge_chf"] >= df["monthly_charge_chf"].quantile(0.8)
    ).astype(int)

    # ARPU per line
    df["arpu_per_line"] = df["monthly_charge_chf"] / df["num_lines"]

    return df


def prepare_modeling_dataset(
    df: pd.DataFrame,
    target_col: str,
    exclude_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare final X, y for modeling."""
    if exclude_cols is None:
        exclude_cols = ["customer_id"]

    X = df.drop(columns=[target_col] + exclude_cols, errors="ignore")
    y = df[target_col]

    # Remove any remaining non-numeric columns
    X = X.select_dtypes(include=[np.number])

    return X, y


if __name__ == "__main__":
    print("Generating synthetic telco data...")
    df = generate_synthetic_telco_data(n_customers=50_000)
    print(f"Shape: {df.shape}")
    print(f"Missing values:\n{df.isna().sum()[df.isna().sum() > 0]}")

    df = handle_missing_values(df)
    df = engineer_telco_features(df)
    print(f"\nFeatures after engineering: {df.shape[1]}")
    print(df.head())
