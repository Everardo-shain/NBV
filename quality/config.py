"""
quality/config.py
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
    "prefix":         "quality",
    "caption_prefix": "Quality factor",
    "type":           "standard",
}
# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_1a1m":    {"id": "4.1.01", "group_id": "4.1", "rank_group": "4.Y.01", "environment": "Study Room",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 1, "y_q": 0, "w_q": 0},
    "stu_evol_1a7m3q":  {"id": "4.1.02", "group_id": "4.1", "rank_group": "4.Y.02", "environment": "Study Room",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.7, "y_q": 0, "w_q": 0.3},
    "stu_evol_1a5m5q":  {"id": "4.1.03", "group_id": "4.1", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.5, "y_q": 0, "w_q": 0.5},
    "stu_evol_1a3m7q":  {"id": "4.1.04", "group_id": "4.1", "rank_group": "4.Y.04", "environment": "Study Room",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.3, "y_q": 0, "w_q": 0.7},
    "stu_evol_1m7a3q":  {"id": "4.1.05", "group_id": "4.1", "rank_group": "4.Y.05", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.7, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.3},
    "stu_evol_1m5a5q":  {"id": "4.1.06", "group_id": "4.1", "rank_group": "4.Y.06", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.5, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.5},
    "stu_evol_1m3a7q":  {"id": "4.1.07", "group_id": "4.1", "rank_group": "4.Y.07", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.3, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.7},
    "stu_evol_1q7a3m":  {"id": "4.1.08", "group_id": "4.1", "rank_group": "4.Y.08", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.7, "y_m": 0, "w_m": 0.3, "y_q": 1, "w_q": 0},
    "stu_evol_1q5a5m":  {"id": "4.1.09", "group_id": "4.1", "rank_group": "4.Y.09", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.5, "y_m": 0, "w_m": 0.5, "y_q": 1, "w_q": 0},
    "stu_evol_1q3a7m":  {"id": "4.1.10", "group_id": "4.1", "rank_group": "4.Y.10", "environment": "Study Room",  "method": "ES",            "y_a": 0, "w_a": 0.3, "y_m": 0, "w_m": 0.7, "y_q": 1, "w_q": 0},

    "stu_anne_1a1m":    {"id": "4.2.01", "group_id": "4.2", "rank_group": "4.Y.01", "environment": "Study Room",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 1, "y_q": 0, "w_q": 0},
    "stu_anne_1a7m3q":  {"id": "4.2.02", "group_id": "4.2", "rank_group": "4.Y.02", "environment": "Study Room",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.7, "y_q": 0, "w_q": 0.3},
    "stu_anne_1a5m5q":  {"id": "4.2.03", "group_id": "4.2", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.5, "y_q": 0, "w_q": 0.5},
    "stu_anne_1a3m7q":  {"id": "4.2.04", "group_id": "4.2", "rank_group": "4.Y.04", "environment": "Study Room",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.3, "y_q": 0, "w_q": 0.7},
    "stu_anne_1m7a3q":  {"id": "4.2.05", "group_id": "4.2", "rank_group": "4.Y.05", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.7, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.3},
    "stu_anne_1m5a5q":  {"id": "4.2.06", "group_id": "4.2", "rank_group": "4.Y.06", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.5, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.5},
    "stu_anne_1m3a7q":  {"id": "4.2.07", "group_id": "4.2", "rank_group": "4.Y.07", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.3, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.7},
    "stu_anne_1q7a3m":  {"id": "4.2.08", "group_id": "4.2", "rank_group": "4.Y.08", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.7, "y_m": 0, "w_m": 0.3, "y_q": 1, "w_q": 0},
    "stu_anne_1q5a5m":  {"id": "4.2.09", "group_id": "4.2", "rank_group": "4.Y.09", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.5, "y_m": 0, "w_m": 0.5, "y_q": 1, "w_q": 0},
    "stu_anne_1q3a7m":  {"id": "4.2.10", "group_id": "4.2", "rank_group": "4.Y.10", "environment": "Study Room",  "method": "SA", "y_a": 0, "w_a": 0.3, "y_m": 0, "w_m": 0.7, "y_q": 1, "w_q": 0},

    "lab_evol_1a1m":    {"id": "4.3.01", "group_id": "4.3", "rank_group": "4.Y.01", "environment": "Laboratory",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 1, "y_q": 0, "w_q": 0},
    "lab_evol_1a7m3q":  {"id": "4.3.02", "group_id": "4.3", "rank_group": "4.Y.02", "environment": "Laboratory",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.7, "y_q": 0, "w_q": 0.3},
    "lab_evol_1a5m5q":  {"id": "4.3.03", "group_id": "4.3", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.5, "y_q": 0, "w_q": 0.5},
    "lab_evol_1a3m7q":  {"id": "4.3.04", "group_id": "4.3", "rank_group": "4.Y.04", "environment": "Laboratory",  "method": "ES",            "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.3, "y_q": 0, "w_q": 0.7},
    "lab_evol_1m7a3q":  {"id": "4.3.05", "group_id": "4.3", "rank_group": "4.Y.05", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.7, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.3},
    "lab_evol_1m5a5q":  {"id": "4.3.06", "group_id": "4.3", "rank_group": "4.Y.06", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.5, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.5},
    "lab_evol_1m3a7q":  {"id": "4.3.07", "group_id": "4.3", "rank_group": "4.Y.07", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.3, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.7},
    "lab_evol_1q7a3m":  {"id": "4.3.08", "group_id": "4.3", "rank_group": "4.Y.08", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.7, "y_m": 0, "w_m": 0.3, "y_q": 1, "w_q": 0},
    "lab_evol_1q5a5m":  {"id": "4.3.09", "group_id": "4.3", "rank_group": "4.Y.09", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.5, "y_m": 0, "w_m": 0.5, "y_q": 1, "w_q": 0},
    "lab_evol_1q3a7m":  {"id": "4.3.10", "group_id": "4.3", "rank_group": "4.Y.10", "environment": "Laboratory",  "method": "ES",            "y_a": 0, "w_a": 0.3, "y_m": 0, "w_m": 0.7, "y_q": 1, "w_q": 0},

    "lab_anne_1a1m":    {"id": "4.4.01", "group_id": "4.4", "rank_group": "4.Y.01", "environment": "Laboratory",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 1, "y_q": 0, "w_q": 0},
    "lab_anne_1a7m3q":  {"id": "4.4.02", "group_id": "4.4", "rank_group": "4.Y.02", "environment": "Laboratory",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.7, "y_q": 0, "w_q": 0.3},
    "lab_anne_1a5m5q":  {"id": "4.4.03", "group_id": "4.4", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.5, "y_q": 0, "w_q": 0.5},
    "lab_anne_1a3m7q":  {"id": "4.4.04", "group_id": "4.4", "rank_group": "4.Y.04", "environment": "Laboratory",  "method": "SA", "y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.3, "y_q": 0, "w_q": 0.7},
    "lab_anne_1m7a3q":  {"id": "4.4.05", "group_id": "4.4", "rank_group": "4.Y.05", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.7, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.3},
    "lab_anne_1m5a5q":  {"id": "4.4.06", "group_id": "4.4", "rank_group": "4.Y.06", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.5, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.5},
    "lab_anne_1m3a7q":  {"id": "4.4.07", "group_id": "4.4", "rank_group": "4.Y.07", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.3, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.7},
    "lab_anne_1q7a3m":  {"id": "4.4.08", "group_id": "4.4", "rank_group": "4.Y.08", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.7, "y_m": 0, "w_m": 0.3, "y_q": 1, "w_q": 0},
    "lab_anne_1q5a5m":  {"id": "4.4.09", "group_id": "4.4", "rank_group": "4.Y.09", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.5, "y_m": 0, "w_m": 0.5, "y_q": 1, "w_q": 0},
    "lab_anne_1q3a7m":  {"id": "4.4.10", "group_id": "4.4", "rank_group": "4.Y.10", "environment": "Laboratory",  "method": "SA", "y_a": 0, "w_a": 0.3, "y_m": 0, "w_m": 0.7, "y_q": 1, "w_q": 0},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "4.Y.01": {"y_a": 1, "w_a": 0, "y_m": 0, "w_m": 1, "y_q": 0, "w_q": 0},
    "4.Y.02": {"y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.7, "y_q": 0, "w_q": 0.3},
    "4.Y.03": {"y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.5, "y_q": 0, "w_q": 0.5},
    "4.Y.04": {"y_a": 1, "w_a": 0, "y_m": 0, "w_m": 0.3, "y_q": 0, "w_q": 0.7},
    "4.Y.05": {"y_a": 0, "w_a": 0.7, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.3},
    "4.Y.06": {"y_a": 0, "w_a": 0.5, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.5},
    "4.Y.07": {"y_a": 0, "w_a": 0.3, "y_m": 1, "w_m": 0, "y_q": 0, "w_q": 0.7},
    "4.Y.08": {"y_a": 0, "w_a": 0.7, "y_m": 0, "w_m": 0.3, "y_q": 1, "w_q": 0},
    "4.Y.09": {"y_a": 0, "w_a": 0.5, "y_m": 0, "w_m": 0.5, "y_q": 1, "w_q": 0},
    "4.Y.10": {"y_a": 0, "w_a": 0.3, "y_m": 0, "w_m": 0.7, "y_q": 1, "w_q": 0},
}

GROUP_PARAMS_COLUMNS = [
    ("y_a",  r"$y_{\text{A}}$"), ("w_a",  r"$w_{\text{A}}$"), ("y_m",  r"$y_{\text{M}}$"), ("w_m",  r"$w_{\text{M}}$"), ("y_q",  r"$y_{\text{Q}}$"), ("w_q",  r"$w_{\text{Q}}$")
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("y_a",  r"$y_{\text{A}}$"), 
    ("w_a",  r"$w_{\text{A}}$"), 
    ("y_m",  r"$y_{\text{M}}$"), 
    ("w_m",  r"$w_{\text{M}}$"), 
    ("y_q",  r"$y_{\text{Q}}$"), 
    ("w_q",  r"$w_{\text{Q}}$")
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None