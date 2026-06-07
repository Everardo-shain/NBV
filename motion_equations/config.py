"""
motion_equations/config.py
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
    "prefix":         "motion_equations",
    "caption_prefix": "Motion Factor Equations",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_d2_e2_73": {"id": "2.1.01", "group_id": "2.1", "rank_group": "2.Y.01", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ1}}$"},
    "stu_evol_d2_e_73":  {"id": "2.1.02", "group_id": "2.1", "rank_group": "2.Y.02", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ2}}$"},
    "stu_evol_d_e2_73":  {"id": "2.1.03", "group_id": "2.1", "rank_group": "2.Y.03", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ1}}$"},
    "stu_evol_d_e_73":   {"id": "2.1.04", "group_id": "2.1", "rank_group": "2.Y.04", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ2}}$"},

    "stu_anne_d2_e2_73": {"id": "2.2.01", "group_id": "2.2", "rank_group": "2.Y.01", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ1}}$"},
    "stu_anne_d2_e_73":  {"id": "2.2.02", "group_id": "2.2", "rank_group": "2.Y.02", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ2}}$"},
    "stu_anne_d_e2_73":  {"id": "2.2.03", "group_id": "2.2", "rank_group": "2.Y.03", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ1}}$"},
    "stu_anne_d_e_73":   {"id": "2.2.04", "group_id": "2.2", "rank_group": "2.Y.04", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ2}}$"},

    "lab_evol_d2_e2_73": {"id": "2.3.01", "group_id": "2.3", "rank_group": "2.Y.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ1}}$"},
    "lab_evol_d2_e_73":  {"id": "2.3.02", "group_id": "2.3", "rank_group": "2.Y.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ2}}$"},
    "lab_evol_d_e2_73":  {"id": "2.3.03", "group_id": "2.3", "rank_group": "2.Y.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ1}}$"},
    "lab_evol_d_e_73":   {"id": "2.3.04", "group_id": "2.3", "rank_group": "2.Y.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ2}}$"},

    "lab_anne_d2_e2_73": {"id": "2.4.01", "group_id": "2.4", "rank_group": "2.Y.01", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ1}}$"},
    "lab_anne_d2_e_73":  {"id": "2.4.02", "group_id": "2.4", "rank_group": "2.Y.02", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ2}}$"},
    "lab_anne_d_e2_73":  {"id": "2.4.03", "group_id": "2.4", "rank_group": "2.Y.03", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ1}}$"},
    "lab_anne_d_e_73":   {"id": "2.4.04", "group_id": "2.4", "rank_group": "2.Y.04", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ2}}$"},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "2.Y.01": {"fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ1}}$"},
    "2.Y.02": {"fmotion": r"$0.7f_{\text{dist1}} + 0.3f_{\text{energ2}}$"},
    "2.Y.03": {"fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ1}}$"},
    "2.Y.04": {"fmotion": r"$0.7f_{\text{dist2}} + 0.3f_{\text{energ2}}$"},
}

GROUP_PARAMS_COLUMNS = [
    ("fmotion",  r"$f_{\text{motion}}$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("fmotion",  r"$f_{\text{motion}}$"),
]
# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None