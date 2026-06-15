"""
Case 1: Uplift Modeling for Churn Retention Campaign
=====================================================

Business Context:
- Overall churn rate: 2% per month
- Proposed treatment: 20 CHF/month discount for 6 months
- Target population: 50,000 "at risk" customers
- Question: Should we do it? Who actually changes behavior due to the discount?

Key Insight:
We don't want to predict WHO WILL CHURN. We want to predict WHO WILL CHANGE
THEIR BEHAVIOR because of the treatment. This is the difference between
propensity modeling and uplift modeling.

Customer Segments (Uplift Framework):
1. Persuadables: Would churn WITHOUT discount, stay WITH discount → TARGET THESE
2. Sure Things: Will stay regardless → Don't waste money
3. Lost Causes: Will churn regardless → Don't waste money
4. Sleeping Dogs: Would stay, but discount triggers shopping behavior → AVOID

Packages used: causalml, sklift (scikit-uplift)
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import sys
import os

# Add the data preprocessing skill folder to the path for cross-skill imports.
_data_skill_dir = os.path.join(os.path.dirname(__file__), "..", "data-preprocessing")
sys.path.insert(0, _data_skill_dir)
from telco_preprocessing import (
    generate_synthetic_telco_data,
    handle_missing_values,
    engineer_telco_features,
    encode_categoricals,
)


def generate_uplift_experiment_data(n_customers: int = 50_000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic RCT data for uplift modeling.
    Simulates a past experiment where discount was randomly assigned.
    """
    rng = np.random.default_rng(seed)

    # Generate base customer features
    df = generate_synthetic_telco_data(n_customers, seed)
    df = handle_missing_values(df)
    df = engineer_telco_features(df)

    # Simulate random treatment assignment (past RCT)
    df["treatment"] = rng.choice([0, 1], n_customers, p=[0.5, 0.5])

    # Simulate churn outcome with heterogeneous treatment effects
    # Base churn probability depends on features
    base_churn_prob = (
        0.02  # baseline 2%
        + 0.03 * (df["contract_type"] == "month_to_month").astype(float)
        + 0.02 * (df["num_support_calls_6m"] > 3).astype(float)
        + 0.015 * (df["tenure_months"] < 12).astype(float)
        - 0.01 * (df["has_family_plan"] == 1).astype(float)
        + 0.01 * (df["days_since_last_interaction"] > 180).astype(float)
    ).clip(0.01, 0.25)

    # Treatment effect (uplift) - varies by segment
    # Persuadables: month-to-month, mid-tenure, some support calls
    uplift_effect = (
        -0.04 * (df["contract_type"] == "month_to_month").astype(float)
        * (df["tenure_months"].between(6, 36)).astype(float)
        - 0.02 * (df["num_support_calls_6m"].between(1, 3)).astype(float)
        - 0.01 * (df["nps_score"].between(5, 7)).astype(float)
        + 0.005 * (df["tenure_months"] > 60).astype(float)  # Sleeping dogs
    )

    # Final churn probability
    churn_prob = base_churn_prob + df["treatment"] * uplift_effect
    churn_prob = churn_prob.clip(0.005, 0.30)

    df["churned"] = (rng.random(n_customers) < churn_prob).astype(int)

    # Store true uplift for evaluation
    df["true_uplift"] = uplift_effect

    return df


def train_uplift_model_causalml(df: pd.DataFrame):
    """
    Train uplift model using causalml's meta-learner approach.
    Uses T-Learner (Two Model approach) and S-Learner (Single Model).
    """
    from causalml.inference.meta import BaseTClassifier, BaseSClassifier, BaseXClassifier
    from sklearn.ensemble import GradientBoostingClassifier
    from xgboost import XGBClassifier

    # Prepare features
    feature_cols = [
        "tenure_months", "monthly_charge_chf", "num_support_calls_6m",
        "data_usage_gb", "days_since_last_interaction", "nps_score",
        "age", "has_family_plan", "num_lines", "annual_revenue",
        "engagement_score", "is_high_value", "arpu_per_line"
    ]

    df_model = encode_categoricals(
        df[feature_cols + ["treatment", "churned", "customer_id", "product_type", "contract_type", "canton", "language"]],
        method="onehot"
    )

    # Identify the encoded feature columns (all except treatment, churned, customer_id)
    X_cols = [c for c in df_model.columns if c not in ["treatment", "churned", "customer_id"]]

    X = df_model[X_cols].values
    treatment = df_model["treatment"].values
    y = df_model["churned"].values

    # T-Learner: separate models for treatment and control
    t_learner = BaseTClassifier(
        learner=XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42, use_label_encoder=False, eval_metric="logloss"
        )
    )

    # X-Learner: better for imbalanced treatment effects
    x_learner = BaseXClassifier(
        learner=XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42, use_label_encoder=False, eval_metric="logloss"
        )
    )

    # Fit and predict uplift
    # Note: for churn, negative uplift = treatment REDUCES churn = GOOD
    t_uplift = t_learner.fit_predict(X=X, treatment=treatment, y=y)
    x_uplift = x_learner.fit_predict(X=X, treatment=treatment, y=y)

    return t_uplift, x_uplift, t_learner, x_learner


def train_uplift_model_sklift(df: pd.DataFrame):
    """
    Train uplift model using sklift (scikit-uplift).
    Alternative implementation using Solo Model and Class Transformation.
    """
    from sklift.models import SoloModel, ClassTransformation
    from sklift.metrics import uplift_auc_score, qini_auc_score
    from sklearn.ensemble import GradientBoostingClassifier

    feature_cols = [
        "tenure_months", "monthly_charge_chf", "num_support_calls_6m",
        "data_usage_gb", "days_since_last_interaction", "nps_score",
        "age", "has_family_plan", "num_lines", "annual_revenue",
        "engagement_score", "is_high_value", "arpu_per_line"
    ]

    df_model = encode_categoricals(
        df[feature_cols + ["treatment", "churned", "product_type", "contract_type", "canton", "language"]],
        method="onehot"
    )

    X_cols = [c for c in df_model.columns if c not in ["treatment", "churned"]]
    X = df_model[X_cols]
    treatment = df_model["treatment"]
    y = df_model["churned"]

    X_train, X_test, trt_train, trt_test, y_train, y_test = train_test_split(
        X, treatment, y, test_size=0.3, random_state=42, stratify=y
    )

    # Solo Model (S-Learner equivalent in sklift)
    solo_model = SoloModel(
        estimator=GradientBoostingClassifier(
            n_estimators=200, max_depth=5, random_state=42
        )
    )
    solo_model.fit(X_train, y_train, trt_train)
    uplift_solo = solo_model.predict(X_test)

    # Class Transformation approach
    ct_model = ClassTransformation(
        estimator=GradientBoostingClassifier(
            n_estimators=200, max_depth=5, random_state=42
        )
    )
    ct_model.fit(X_train, y_train, trt_train)
    uplift_ct = ct_model.predict(X_test)

    # Evaluate
    auc_solo = uplift_auc_score(y_test, uplift_solo, trt_test)
    qini_solo = qini_auc_score(y_test, uplift_solo, trt_test)

    print(f"Solo Model - Uplift AUC: {auc_solo:.4f}, Qini AUC: {qini_solo:.4f}")

    return uplift_solo, uplift_ct, X_test, y_test, trt_test


if __name__ == "__main__":
    print("=" * 60)
    print("Case 1: Uplift Modeling for Churn Retention")
    print("=" * 60)

    # Generate experimental data
    print("\n1. Generating synthetic RCT data...")
    df = generate_uplift_experiment_data(n_customers=50_000)
    print(f"   Dataset shape: {df.shape}")
    print(f"   Treatment split: {df['treatment'].value_counts().to_dict()}")
    print(f"   Churn rate (control): {df[df['treatment']==0]['churned'].mean():.3%}")
    print(f"   Churn rate (treatment): {df[df['treatment']==1]['churned'].mean():.3%}")
    print(f"   Average Treatment Effect: {df[df['treatment']==1]['churned'].mean() - df[df['treatment']==0]['churned'].mean():.4f}")

    # Try sklift first (lighter dependency)
    try:
        print("\n2. Training uplift model (sklift)...")
        uplift_solo, uplift_ct, X_test, y_test, trt_test = train_uplift_model_sklift(df)
        print("   ✓ Model trained successfully")
    except ImportError as e:
        print(f"   ⚠ sklift not installed: {e}")
        print("   Install with: pip install scikit-uplift")

    # Try causalml
    try:
        print("\n3. Training uplift model (causalml)...")
        t_uplift, x_uplift, _, _ = train_uplift_model_causalml(df)
        print("   ✓ Model trained successfully")
        print(f"   Mean uplift (T-Learner): {t_uplift.mean():.4f}")
        print(f"   Mean uplift (X-Learner): {x_uplift.mean():.4f}")
    except ImportError as e:
        print(f"   ⚠ causalml not installed: {e}")
        print("   Install with: pip install causalml")
