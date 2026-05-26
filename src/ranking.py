"""
src/ranking.py
--------------
Ranking methodology.

Rankings are computed WITHIN each group_id so that only comparable experiments
(same scene + same optimization method) are ranked against each other.
rank_group is used separately to aggregate results for the grouped table.

Group selection follows a two-stage lexicographic procedure:
  1. Sort by success_count descending (n_s = number of valid sub-experiments)
  2. Within same n_s, sort by mean totalrank of valid sub-experiments ascending
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


def extract_summary(experiments: dict, experiments_cfg: dict = None) -> pd.DataFrame:
    """
    Build one-row-per-experiment summary from a dict of {id: (meta, df)}.

    group_id  : used for within-group ranking (same scene + method)
    rank_group: used for aggregation in the grouped table (same parameter value)
    """
    id_to_cfg = {}
    if experiments_cfg:
        for fname, ecfg in experiments_cfg.items():
            id_to_cfg[ecfg["id"]] = ecfg

    rows = []
    for exp_id, (meta, df) in experiments.items():
        last = df.iloc[-1]
        ecfg = id_to_cfg.get(exp_id, {})

        if "group_id" in ecfg:
            group_id = ecfg["group_id"]
        else:
            parts    = str(exp_id).split(".")
            group_id = ".".join(parts[:-1]) if len(parts) > 2 else exp_id

        rank_group = ecfg.get("rank_group", group_id)

        rows.append({
            "experiment_id": exp_id,
            "group_id":      group_id,
            "rank_group":    rank_group,
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
    Compute ranks WITHIN each group_id separately.
    Invalid experiments (below threshold) are marked with is_valid=False
    and receive a penalty totalrank, but are kept in the DataFrame.
    """
    results = []

    for group_id, group_df in summary.groupby("group_id"):
        group_df = group_df.copy()

        if pct_threshold is not None:
            valid_mask = group_df["pct_retrieved"] >= pct_threshold
            valid_df   = group_df[valid_mask].copy()
            invalid_df = group_df[~valid_mask].copy()
            if valid_df.empty:
                rank_cols = ["drank", "erank", "retrrank", "qrank",
                             "timerank", "frank", "totalrank"]
                for col in rank_cols:
                    group_df[col] = 0.0
                group_df["totalrank"] = penalty_multiplier * 100.0
                group_df["is_valid"]  = False
                results.append(group_df)
                continue
        else:
            valid_df   = group_df.copy()
            invalid_df = pd.DataFrame()

        # ── Rank valid experiments within this group only ─────────────────────
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

        valid_df["is_valid"] = True

        # ── Penalize invalid within this group ────────────────────────────────
        rank_cols = ["drank", "erank", "retrrank", "qrank",
                     "timerank", "frank", "totalrank"]
        if not invalid_df.empty:
            totalrank_max = valid_df["totalrank"].max()
            penalty       = penalty_multiplier * totalrank_max
            for col in rank_cols:
                invalid_df[col] = 0.0
            invalid_df["totalrank"] = penalty
            invalid_df["is_valid"]  = False

        results.append(pd.concat([valid_df, invalid_df]))

    return pd.concat(results).sort_values("totalrank").reset_index(drop=True)


def rank_experiments(
    experiments: dict,
    pct_threshold: float = None,
    totalrank_formula=None,
    penalty_multiplier: float = 2.0,
    experiments_cfg: dict = None,
) -> pd.DataFrame:
    """One-call pipeline: experiments dict -> ranked summary DataFrame."""
    return compute_ranks(
        extract_summary(experiments, experiments_cfg=experiments_cfg),
        pct_threshold=pct_threshold,
        totalrank_formula=totalrank_formula,
        penalty_multiplier=penalty_multiplier,
    )


def rank_groups(ranked_df: pd.DataFrame, groups_cfg: dict) -> pd.DataFrame:
    """
    Two-stage lexicographic group ranking (Eq. success_count / mean_totalrank):
      1. success_count = number of valid sub-experiments (higher = better)
      2. mean_totalrank over valid sub-experiments only (lower = better)

    Also determines the winning criterion for table highlighting:
      'success_count' if the winner was decided by n_s
      'totalrank'     if decided by mean_totalrank (tie in n_s)
    """
    if "rank_group" not in ranked_df.columns:
        ranked_df = ranked_df.copy()
        ranked_df["rank_group"] = ranked_df["group_id"]

    rows = []
    for rg in groups_cfg.keys():
        sub = ranked_df[ranked_df["rank_group"] == rg]

        if "is_valid" in sub.columns:
            valid_sub     = sub[sub["is_valid"] == True]
            success_count = len(valid_sub)
        else:
            valid_sub     = sub
            success_count = len(sub)

        mean_totalrank = valid_sub["totalrank"].mean() if not valid_sub.empty else float("nan")

        raw_cols  = ["acc_dist_m", "acc_energy", "pct_retrieved",
                     "mean_quality", "total_time_s"]
        available = [c for c in raw_cols if c in valid_sub.columns]
        raw_means = valid_sub[available].mean().to_dict() if not valid_sub.empty else {}

        rows.append({
            "experiment_id": rg,
            "success_count": success_count,
            "totalrank":     mean_totalrank,
            **raw_means,
        })

    grouped = pd.DataFrame(rows)

    # Lexicographic sort: success_count desc, then totalrank asc
    grouped = grouped.sort_values(
        ["success_count", "totalrank"],
        ascending=[False, True],
    ).reset_index(drop=True)

    # Determine winning criterion
    if len(grouped) > 1:
        winner_ns   = grouped.iloc[0]["success_count"]
        second_ns   = grouped.iloc[1]["success_count"]
        winning_by  = "success_count" if winner_ns > second_ns else "totalrank"
    else:
        winning_by = "success_count"

    grouped["winning_criterion"] = ""
    grouped.at[grouped.index[0], "winning_criterion"] = winning_by

    return grouped
