import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.neighbors import NearestNeighbors


def fit_propensity(frame: pd.DataFrame, formula: str):
    model = smf.logit(formula=formula, data=frame).fit(disp=False)
    scores = model.predict(frame)
    return model, scores


def _smd_numeric(x_t: np.ndarray, x_c: np.ndarray) -> float:
    mt, mc = np.mean(x_t), np.mean(x_c)
    vt, vc = np.var(x_t, ddof=1), np.var(x_c, ddof=1)
    denom = np.sqrt((vt + vc) / 2)
    if denom == 0 or np.isnan(denom):
        return 0.0
    return float((mt - mc) / denom)


def _smd_binary(x_t: np.ndarray, x_c: np.ndarray) -> float:
    pt, pc = np.mean(x_t), np.mean(x_c)
    p = (pt + pc) / 2
    denom = np.sqrt(p * (1 - p))
    if denom == 0 or np.isnan(denom):
        return 0.0
    return float((pt - pc) / denom)


def smd_table(
    frame_before_t: pd.DataFrame,
    frame_before_c: pd.DataFrame,
    frame_after_t: pd.DataFrame,
    frame_after_c: pd.DataFrame,
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> pd.DataFrame:
    rows = []
    for col in numeric_cols:
        before = _smd_numeric(frame_before_t[col].to_numpy(), frame_before_c[col].to_numpy())
        after = _smd_numeric(frame_after_t[col].to_numpy(), frame_after_c[col].to_numpy())
        rows.append({"variable": col, "smd_before": before, "smd_after": after})

    for col in categorical_cols:
        levels = sorted(set(frame_before_t[col].astype(str)).union(set(frame_before_c[col].astype(str))))
        for level in levels:
            bt = (frame_before_t[col].astype(str) == level).astype(float).to_numpy()
            bc = (frame_before_c[col].astype(str) == level).astype(float).to_numpy()
            at = (frame_after_t[col].astype(str) == level).astype(float).to_numpy()
            ac = (frame_after_c[col].astype(str) == level).astype(float).to_numpy()
            before = _smd_binary(bt, bc)
            after = _smd_binary(at, ac)
            rows.append({"variable": f"{col}={level}", "smd_before": before, "smd_after": after})

    out = pd.DataFrame(rows)
    out["abs_smd_before"] = out["smd_before"].abs()
    out["abs_smd_after"] = out["smd_after"].abs()
    out["balance_grade_after"] = np.select(
        [out["abs_smd_after"] > 0.20, out["abs_smd_after"] >= 0.10],
        ["poor", "acceptable"],
        default="good",
    )
    return out.sort_values("abs_smd_after", ascending=False).reset_index(drop=True)


def run_matching(
    frame: pd.DataFrame,
    caliper: float = 0.02,
    ratio: int = 1,
    strata_col: str | None = None,
) -> dict:
    work = frame.copy()
    y_col = "churned"
    t_col = "has_booster"
    ps_col = "propensity_score"

    if strata_col is None:
        work["_stratum"] = "ALL"
        strata_col = "_stratum"

    pairs = []
    treated_total = int((work[t_col] == 1).sum())

    for stratum, block in work.groupby(strata_col, observed=True):
        treated = block[block[t_col] == 1].copy()
        control = block[block[t_col] == 0].copy()
        if len(treated) == 0 or len(control) == 0:
            continue

        n_neighbors = min(max(ratio, 1), len(control))
        nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
        nn.fit(control[[ps_col]])
        distances, indices = nn.kneighbors(treated[[ps_col]])

        treated = treated.reset_index(drop=True)
        control = control.reset_index(drop=True)

        for i in range(len(treated)):
            d_i = distances[i]
            j_i = indices[i]
            valid = [(d, j) for d, j in zip(d_i, j_i) if d <= caliper]
            if len(valid) < ratio:
                continue
            valid = valid[:ratio]
            for d, j in valid:
                tr = treated.iloc[i]
                co = control.iloc[j]
                pairs.append(
                    {
                        "stratum": stratum,
                        "treated_orig": int(tr["_orig_index"]),
                        "control_orig": int(co["_orig_index"]),
                        "treated_outcome": float(tr[y_col]),
                        "control_outcome": float(co[y_col]),
                        "match_distance": float(d),
                    }
                )

    pairs = pd.DataFrame(pairs)
    if len(pairs) == 0:
        return {
            "pairs": pairs,
            "att": np.nan,
            "n_pairs": 0,
            "matched_treated": 0,
            "coverage": 0.0,
            "avg_distance": np.nan,
            "treated_effects": pd.Series(dtype=float),
        }

    treated_effects = (
        pairs.groupby("treated_orig", as_index=False)
        .agg(treated_outcome=("treated_outcome", "first"), control_mean=("control_outcome", "mean"))
    )
    treated_effects["effect"] = treated_effects["treated_outcome"] - treated_effects["control_mean"]

    att = float(treated_effects["effect"].mean())
    matched_treated = int(treated_effects["treated_orig"].nunique())
    n_pairs = int(len(pairs))
    coverage = matched_treated / treated_total if treated_total > 0 else 0.0
    avg_distance = float(pairs["match_distance"].mean())

    return {
        "pairs": pairs,
        "att": att,
        "n_pairs": n_pairs,
        "matched_treated": matched_treated,
        "coverage": coverage,
        "avg_distance": avg_distance,
        "treated_effects": treated_effects,
    }


def overlap_report(frame: pd.DataFrame, ps_col: str = "propensity_score", t_col: str = "has_booster") -> dict:
    treated = frame.loc[frame[t_col] == 1, ps_col]
    control = frame.loc[frame[t_col] == 0, ps_col]
    low = max(float(treated.min()), float(control.min()))
    high = min(float(treated.max()), float(control.max()))
    outside = ((frame[ps_col] < low) | (frame[ps_col] > high)).mean()
    return {
        "treated_min": float(treated.min()),
        "treated_max": float(treated.max()),
        "control_min": float(control.min()),
        "control_max": float(control.max()),
        "support_low": low,
        "support_high": high,
        "outside_support_pct": float(outside * 100),
    }
