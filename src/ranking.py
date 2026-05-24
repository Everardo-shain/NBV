"""
src/ranking.py
--------------
Ranking methodology from thesis Section 6.5 (Eq. 6.2 – 6.5).

  ranking_decr(v) = 100 * |v - v_min| / v_min     lower raw value = better
  ranking_incr(v) = 100 * |v - v_max| / v_max     higher raw value = better

  frank     = unweighted average of drank, erank, retrrank, qrank
  totalrank = 0.7 * frank + 0.3 * timerank  (default, overridable per section)
"""

import numpy as np
import pandas as pd
from pathlib import Path


def _safe_decr(series: pd.Series) -> pd.Series:
    v_min = series.min()
    if v_min == 0:
        v_rng = series.max()
        return pd.Series(
            np.zeros(len(series)) if v_rng == 0 else 100 * (series - v_min) / v_rng,
            index=series.index,
        )
    return 100 * np.abs(series - v_min) / v_min


def _safe_incr(series: pd.Series) -> pd.Series:
    v_max = series.max()
    if v_max == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return 100 * np.abs(series - v_max) / v_max


def extract_summary(experiments: dict) -> pd.DataFrame:
    """
    Build one-row-per-experiment summary from a dict of {id: (meta, df)}.
    Uses the last view's cumulative values as the final metric.
    group_id is derived from experiment_id by dropping the last level
    (e.g. "1.01.02" → "1.01"). For sections without sub-experiments,
    group_id equals experiment_id.
    """
    rows = []
    for exp_id, (meta, df) in experiments.items():
        last = df.iloc[-1]
        parts    = str(exp_id).split(".")
        group_id = ".".join(parts[:-1]) if len(parts) > 2 else exp_id
        rows.append({
            "experiment_id": exp_id,
            "group_id":      group_id,
            "method":        meta.get("method", "unknown"),
            "scene":         Path(meta.get("scene", "")).stem,
            "acc_dist_m":    float(last["cum_travelled_m"]),
            "acc_energy":    float(last["cum_energy"]),
            "pct_retrieved": float(last["tri_imaged_pct"]),
            "mean_quality":  float(last["tri_quality"]),
            "total_time_s":  float(last["total_time"]),
        })
    return pd.DataFrame(rows)


def compute_ranks(
    summary: pd.DataFrame,
    pct_threshold: float = None,
    totalrank_formula=None,
    penalty_multiplier: float = 2.0,
) -> pd.DataFrame:
    """
    Compute ranks for all experiments.
    Invalid experiments (below threshold) are penalized instead of excluded.
    """
    df = summary.copy()

    # ── Split valid / invalid ─────────────────────────────────────────────────
    if pct_threshold is not None:
        valid_mask = df["pct_retrieved"] >= pct_threshold
        valid_df   = df[valid_mask].copy()
        invalid_df = df[~valid_mask].copy()
        if valid_df.empty:
            raise ValueError(f"No experiments passed {pct_threshold}% retrieval threshold.")
    else:
        valid_df   = df.copy()
        invalid_df = pd.DataFrame()

    # ── Rank valid experiments ────────────────────────────────────────────────
    valid_df["drank"]    = _safe_decr(valid_df["acc_dist_m"])
    valid_df["erank"]    = _safe_decr(valid_df["acc_energy"])
    valid_df["retrrank"] = _safe_incr(valid_df["pct_retrieved"])
    valid_df["qrank"]    = _safe_incr(valid_df["mean_quality"])
    valid_df["timerank"] = _safe_decr(valid_df["total_time_s"])
    valid_df["frank"]    = (valid_df["drank"] + valid_df["erank"] +
                            valid_df["retrrank"] + valid_df["qrank"]) / 4.0

    if totalrank_formula is not None:
        valid_df["totalrank"] = totalrank_formula(
            valid_df["drank"], valid_df["erank"],
            valid_df["retrrank"], valid_df["qrank"],
            valid_df["timerank"],
        )
    else:
        valid_df["totalrank"] = 0.7 * valid_df["frank"] + 0.3 * valid_df["timerank"]

    # ── Penalize invalid experiments ──────────────────────────────────────────
    rank_cols = ["drank", "erank", "retrrank", "qrank", "timerank", "frank", "totalrank"]
    if not invalid_df.empty:
        totalrank_max = valid_df["totalrank"].max()
        penalty       = penalty_multiplier * totalrank_max
        for col in rank_cols:
            invalid_df[col] = 0.0
        invalid_df["totalrank"] = penalty
        invalid_df["is_valid"]  = False        # ← marca inválidos

    valid_df["is_valid"] = True                # ← marca válidos

    # ── Recombine ─────────────────────────────────────────────────────────────
    return pd.concat([valid_df, invalid_df]).sort_values("totalrank").reset_index(drop=True)


def rank_experiments(
    experiments: dict,
    pct_threshold: float = None,
    totalrank_formula=None,
    penalty_multiplier: float = 2.0,
) -> pd.DataFrame:
    """One-call pipeline: experiments dict → ranked summary DataFrame."""
    return compute_ranks(
        extract_summary(experiments),
        pct_threshold=pct_threshold,
        totalrank_formula=totalrank_formula,
        penalty_multiplier=penalty_multiplier,
    )


def rank_groups(ranked_df: pd.DataFrame, groups_cfg: dict) -> pd.DataFrame:
    """
    Average totalrank by group_id (includes penalized invalid sub-experiments).
    Also averages raw metrics for context columns in the grouped table.
    """
    grouped = (
        ranked_df.groupby("group_id")["totalrank"]
        .mean()
        .reset_index()
        .rename(columns={"group_id": "experiment_id", "totalrank": "mean_totalrank"})
    )

    raw_cols  = ["acc_dist_m", "acc_energy", "pct_retrieved", "mean_quality", "total_time_s"]
    available = [c for c in raw_cols if c in ranked_df.columns]
    raw_means = (
        ranked_df.groupby("group_id")[available]
        .mean()
        .reset_index()
        .rename(columns={"group_id": "experiment_id"})
    )

    grouped = grouped.merge(raw_means, on="experiment_id")
    grouped = grouped.rename(columns={"mean_totalrank": "totalrank"})
    return grouped.sort_values("totalrank").reset_index(drop=True)