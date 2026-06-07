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

Metric selection is driven by the METRICS list in config.py.
Valid keys and their mapping:
  "distance"  → summary col: acc_dist_m     rank col: drank       decr
  "energy"    → summary col: acc_energy     rank col: erank       decr
  "retrieved" → summary col: pct_retrieved  rank col: retrrank    incr  (always ranked)
  "quality"   → summary col: mean_quality   rank col: qrank       incr
  "time"      → summary col: total_time_s   rank col: timerank    decr
  "delta_f"   → summary col: acc_delta_f    rank col: none
"""

import numpy as np
import pandas as pd
from pathlib import Path


# ── Metric registry ───────────────────────────────────────────────────────────
# key → (summary_col, rank_col, direction)   direction: "decr" | "incr"
METRIC_REGISTRY = {
    "distance":  ("acc_dist_m",    "drank",        "decr"),
    "energy":    ("acc_energy",    "erank",        "decr"),
    "retrieved": ("pct_retrieved", "retrrank",     "incr"),
    "quality":   ("mean_quality",  "qrank",        "incr"),
    "time":      ("total_time_s",  "timerank",     "decr"),
    "delta_f":   ("acc_delta_f",   None,           None),
}

# "retrieved" is always included in ranking (used for threshold filtering)
_ALWAYS_RANKED = {"retrieved"}

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


def extract_summary(
    experiments: dict,
    experiments_cfg: dict = None,
    metrics: list = None,
) -> pd.DataFrame:
    """
    Build one-row-per-experiment summary.

    Only summary columns needed by the active metrics are populated.
    acc_delta_f is included only when "delta_f" is in metrics AND the
    parsed DataFrame contains cum_delta_f.
    """
    if metrics is None:
        metrics = list(METRIC_REGISTRY.keys())

    active_metrics = set(metrics) | _ALWAYS_RANKED

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

        row = {
            "experiment_id": exp_id,
            "group_id":      group_id,
            "rank_group":    rank_group,
            "method":        meta.get("method", "unknown"),
            "scene":         Path(meta.get("scene", "")).stem,
        }

        for mkey in active_metrics:
            if mkey not in METRIC_REGISTRY:
                continue
            summary_col, _, _ = METRIC_REGISTRY[mkey]
            if mkey == "distance":
                row[summary_col] = float(last["cum_travelled_m"])
            elif mkey == "energy":
                row[summary_col] = float(last["cum_energy"])
            elif mkey == "retrieved":
                row[summary_col] = float(last["tri_imaged_pct"])
            elif mkey == "quality":
                row[summary_col] = float(last["tri_quality"])
            elif mkey == "time":
                row[summary_col] = float(last["total_time"])
            elif mkey == "delta_f":
                if "cum_delta_f" in df.columns:
                    row[summary_col] = float(last["cum_delta_f"])

        rows.append(row)

    return pd.DataFrame(rows)


def compute_ranks(
    summary: pd.DataFrame,
    pct_threshold: float = None,
    totalrank_formula=None,
    metrics: list = None,
) -> pd.DataFrame:
    """
    Compute ranks WITHIN each group_id separately.
    Invalid experiments (below threshold) receive NaN in all rank columns.
    """
    if metrics is None:
        metrics = list(METRIC_REGISTRY.keys())

    active_metrics = set(metrics) | _ALWAYS_RANKED

    available = [
        mkey for mkey in active_metrics
        if mkey in METRIC_REGISTRY 
        and METRIC_REGISTRY[mkey][0] in summary.columns
        and METRIC_REGISTRY[mkey][1] is not None
    ]

    rank_cols = [METRIC_REGISTRY[m][1] for m in available] + ["frank", "totalrank"]

    results = []

    for group_id, group_df in summary.groupby("group_id"):
        group_df = group_df.copy()

        if pct_threshold is not None:
            valid_mask = group_df["pct_retrieved"] >= pct_threshold
            valid_df   = group_df[valid_mask].copy()
            invalid_df = group_df[~valid_mask].copy()
            if valid_df.empty:
                for col in rank_cols:
                    group_df[col] = float("nan")
                group_df["is_valid"] = False
                results.append(group_df)
                continue
        else:
            valid_df   = group_df.copy()
            invalid_df = pd.DataFrame()

        # ── Rank valid experiments ────────────────────────────────────────────
        for mkey in available:
            summary_col, rank_col, direction = METRIC_REGISTRY[mkey]
            if direction == "decr":
                valid_df[rank_col] = _safe_decr(valid_df[summary_col])
            else:
                valid_df[rank_col] = _safe_incr(valid_df[summary_col])

        # frank = mean of all individual ranks
        indiv_rank_cols = [METRIC_REGISTRY[m][1] for m in available]
        valid_df["frank"] = valid_df[indiv_rank_cols].mean(axis=1)

        if totalrank_formula is not None:
            # Build kwargs from available rank columns
            rank_kwargs = {
                METRIC_REGISTRY[m][1]: valid_df[METRIC_REGISTRY[m][1]]
                for m in available
            }
            def _get(col):
                return valid_df.get(col, pd.Series(0.0, index=valid_df.index))

            valid_df["totalrank"] = totalrank_formula(
                _get("drank"), _get("erank"), _get("retrrank"),
                _get("qrank"), _get("timerank"), **{
                    k: v for k, v in rank_kwargs.items()
                    if k not in ("drank", "erank", "retrrank", "qrank", "timerank")
                }
            )
        else:
            valid_df["totalrank"] = 0.7 * valid_df["frank"] + 0.3 * valid_df.get(
                "timerank", pd.Series(0.0, index=valid_df.index)
            )

        valid_df["is_valid"] = True

        # ── Invalid: NaN ──────────────────────────────────────────────────────
        if not invalid_df.empty:
            for col in rank_cols:
                invalid_df[col] = float("nan")
            invalid_df["is_valid"] = False

        results.append(pd.concat([valid_df, invalid_df]))

    return pd.concat(results).sort_values("totalrank").reset_index(drop=True)


def rank_experiments(
    experiments: dict,
    pct_threshold: float = None,
    totalrank_formula=None,
    experiments_cfg: dict = None,
    metrics: list = None,
) -> pd.DataFrame:
    """One-call pipeline: experiments dict -> ranked summary DataFrame."""
    return compute_ranks(
        extract_summary(experiments, experiments_cfg=experiments_cfg, metrics=metrics),
        pct_threshold=pct_threshold,
        totalrank_formula=totalrank_formula,
        metrics=metrics,
    )


def rank_groups(
    ranked_df: pd.DataFrame,
    groups_cfg: dict,
    metrics: list = None,
) -> pd.DataFrame:
    """
    Two-stage lexicographic group ranking:
      1. success_count desc
      2. mean_totalrank asc (valid sub-experiments only)
    """
    if metrics is None:
        metrics = list(METRIC_REGISTRY.keys())

    if "rank_group" not in ranked_df.columns:
        ranked_df = ranked_df.copy()
        ranked_df["rank_group"] = ranked_df["group_id"]

    active_metrics = set(metrics) | _ALWAYS_RANKED
    raw_cols = [
        METRIC_REGISTRY[m][0] for m in active_metrics
        if m in METRIC_REGISTRY and METRIC_REGISTRY[m][0] in ranked_df.columns
    ]

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
        available      = [c for c in raw_cols if c in valid_sub.columns]
        raw_means      = valid_sub[available].mean().to_dict() if not valid_sub.empty else {}

        rows.append({
            "experiment_id": rg,
            "success_count": success_count,
            "totalrank":     mean_totalrank,
            **raw_means,
        })

    grouped = pd.DataFrame(rows)
    grouped = grouped.sort_values(
        ["success_count", "totalrank"], ascending=[False, True]
    ).reset_index(drop=True)

    if len(grouped) > 1:
        winner_ns  = grouped.iloc[0]["success_count"]
        second_ns  = grouped.iloc[1]["success_count"]
        winning_by = "success_count" if winner_ns > second_ns else "totalrank"
    else:
        winning_by = "success_count"

    grouped["winning_criterion"] = ""
    grouped.at[grouped.index[0], "winning_criterion"] = winning_by

    return grouped