from pathlib import Path

import pandas as pd

USAGE_ORDER = ["Low", "Medium", "High", "Extreme"]
MODEL_COLUMNS = [
    "churned",
    "has_booster",
    "age",
    "tenure",
    "internet_usage",
    "tv_product",
    "mobile_product",
    "commune",
]


def load_analysis_data(csv_path: str | Path = "processed/df_analysis.csv") -> pd.DataFrame:
    """Load the processed analysis dataset produced by 01_data_wrangling."""
    return pd.read_csv(Path(csv_path))


def prepare_model_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return cleaned modeling frame with stable categorical encodings."""
    frame = df[MODEL_COLUMNS].dropna().copy()
    frame["internet_usage"] = pd.Categorical(
        frame["internet_usage"], categories=USAGE_ORDER, ordered=True
    )
    for col in ["tv_product", "mobile_product", "commune"]:
        frame[col] = frame[col].astype("category")
    return frame
