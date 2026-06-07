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
    "prefix":         "final_validation",
    "caption_prefix": "Final Objective Function Validation",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_1a5m5q":  {"id": "5.1.01", "group_id": "5.1", "rank_group": "5.Y.01", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "stu_evol_original":  {"id": "5.1.02", "group_id": "5.1", "rank_group": "5.Y.02", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},


    "stu_anne_1a5m5q":  {"id": "5.2.01", "group_id": "5.2", "rank_group": "5.Y.01", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "stu_anne_original":  {"id": "5.2.02", "group_id": "5.2", "rank_group": "5.Y.02", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},


    "lab_evol_1a5m5q":  {"id": "5.3.01", "group_id": "5.3", "rank_group": "5.Y.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "lab_evol_original":  {"id": "5.3.02", "group_id": "5.3", "rank_group": "5.Y.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
 

    "lab_anne_1a5m5q":  {"id": "5.4.01", "group_id": "5.4", "rank_group": "5.Y.01", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "lab_anne_original":  {"id": "5.4.02", "group_id": "5.4", "rank_group": "5.Y.02", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "5.Y.01": {"f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "5.Y.02": {"f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
}

GROUP_PARAMS_COLUMNS = [
    ("f",  r"$f$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("f",  r"$f$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None