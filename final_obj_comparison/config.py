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
    "caption_prefix": "Objective function final comparison",
    "type":           "comparison",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["retrieved"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_1a5m5q":  {"id": "4.1.03", "group_id": "1", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "ES",            "Role": "Proposed"},
    "stu_evol_original":  {"id": "3.1.01", "group_id": "1", "rank_group": "3.Y.01", "environment": "Study Room",  "method": "ES",            "Role": "Baseline"},


    "stu_anne_1a5m5q":  {"id": "4.2.03", "group_id": "2", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "SA", "Role": "Proposed"},
    "stu_anne_original":  {"id": "3.2.01", "group_id": "2", "rank_group": "3.Y.01", "environment": "Study Room",  "method": "SA", "Role": "Baseline"},


    "lab_evol_1a5m5q":  {"id": "4.3.03", "group_id": "3", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "ES",            "Role": "Proposed"},
    "lab_evol_original":  {"id": "3.3.01", "group_id": "3", "rank_group": "3.Y.01", "environment": "Laboratory",  "method": "ES",            "Role": "Baseline"},
 

    "lab_anne_1a5m5q":  {"id": "4.4.03", "group_id": "4", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "SA", "Role": "Proposed"},
    "lab_anne_original":  {"id": "3.4.01", "group_id": "4", "rank_group": "3.Y.01", "environment": "Laboratory",  "method": "SA", "Role": "Baseline"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "4.Y.03": {"Role": "Proposed"},
    "3.Y.01": {"Role": "Baseline"},
}

GROUP_PARAMS_COLUMNS = [
    ("Role",  "Role"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("Role",  "Role"),
    ("environment", "Scene"),
    ("method",      "Method"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None