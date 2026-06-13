"""
quality/final_objective_function_validation.py
--------------
group_id  : who competes against whom for ranking
            (same scene + same optimization method)
rank_group: how results are aggregated in the grouped table
            (same parameter value, labeled G1-G7)
METRICS controls which metrics appear in results tables, rank tables,
and comparison grid figures. Valid keys:

  "distance"   →  results: acc_dist_m      rank: drank
  "energy"     →  results: acc_energy      rank: erank
  "retrieved"  →  results: pct_retrieved   rank: retrrank   (always ranked)
  "quality"    →  results: mean_quality    rank: qrank
  "time"       →  results: total_time_s    rank: timerank
  "delta_f"    → summary col: acc_delta_f  rank col: none

"retrieved" is always included in ranking even if omitted here (pct_threshold).
"totalrank" always appears in the ranked table.
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "final_obj_comparison",
    "caption_prefix": "Final Objective Function Comparison",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_1a5m5q":  {"id": "5.1.01", "group_id": "5.1", "rank_group": "5.Y.01", "environment": "Study Room",  "method": "ES",            "w_m": 0.5, "sw_d": 0.3, "sw_e": 0.7, "w_q": 0.5},
    "stu_evol_original":  {"id": "5.1.02", "group_id": "5.1", "rank_group": "5.Y.02", "environment": "Study Room",  "method": "ES",            "w_m": 1, "sw_d": 0.7, "sw_e": 0.3, "w_q": 0},


    "stu_anne_1a5m5q":  {"id": "5.2.01", "group_id": "5.2", "rank_group": "5.Y.01", "environment": "Study Room",  "method": "SA", "w_m": 0.5, "sw_d": 0.3, "sw_e": 0.7, "w_q": 0.5},
    "stu_anne_original":  {"id": "5.2.02", "group_id": "5.2", "rank_group": "5.Y.02", "environment": "Study Room",  "method": "SA", "w_m": 1, "sw_d": 0.7, "sw_e": 0.3, "w_q": 0},


    "lab_evol_1a5m5q":  {"id": "5.3.01", "group_id": "5.3", "rank_group": "5.Y.01", "environment": "Laboratory",  "method": "ES",            "w_m": 0.5, "sw_d": 0.3, "sw_e": 0.7, "w_q": 0.5},
    "lab_evol_original":  {"id": "5.3.02", "group_id": "5.3", "rank_group": "5.Y.02", "environment": "Laboratory",  "method": "ES",            "w_m": 1, "sw_d": 0.7, "sw_e": 0.3, "w_q": 0},
 

    "lab_anne_1a5m5q":  {"id": "5.4.01", "group_id": "5.4", "rank_group": "5.Y.01", "environment": "Laboratory",  "method": "SA", "w_m": 0.5, "sw_d": 0.3, "sw_e": 0.7, "w_q": 0.5},
    "lab_anne_original":  {"id": "5.4.02", "group_id": "5.4", "rank_group": "5.Y.02", "environment": "Laboratory",  "method": "SA", "w_m": 1, "sw_d": 0.7, "sw_e": 0.3, "w_q": 0},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "5.Y.01": {"w_m": 0.5, "sw_d": 0.3, "sw_e": 0.7, "w_q": 0.5},
    "5.Y.02": {"w_m": 1, "sw_d": 0.7, "sw_e": 0.3, "w_q": 0},
}

GROUP_PARAMS_COLUMNS = [
    ("w_m",  r"$w_{\text{M}}$"),
    ("sw_d",  r"$\mathit{sw}_{\text{D}}$"),
    ("sw_e",  r"$\mathit{sw}_{\text{E}}$"),
    ("w_q",  r"$w_{\text{Q}}$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None