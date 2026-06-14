"""
motion/config.py
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
    "prefix":         "motion",
    "caption_prefix": "Motion factor",
    "type":           "standard",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_d_e2_73":  {"id": "3.1.01", "group_id": "3.1", "rank_group": "3.Y.01", "environment": "Study Room",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.7, "sw_e": 0.3},
    "stu_evol_d_e2_55":  {"id": "3.1.02", "group_id": "3.1", "rank_group": "3.Y.02", "environment": "Study Room",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.5, "sw_e": 0.5},
    "stu_evol_d_e2_37":  {"id": "3.1.03", "group_id": "3.1", "rank_group": "3.Y.03", "environment": "Study Room",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.3, "sw_e": 0.7},
    "stu_evol_d_e2_10":  {"id": "3.1.04", "group_id": "3.1", "rank_group": "3.Y.04", "environment": "Study Room",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 1, "sw_e": 0},
    "stu_evol_d_e2_01":  {"id": "3.1.05", "group_id": "3.1", "rank_group": "3.Y.05", "environment": "Study Room",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0, "sw_e": 1},
    "stu_evol_40":       {"id": "3.1.06", "group_id": "3.1", "rank_group": "3.Y.06", "environment": "Study Room",  "method": "ES",            "alpha_sf": 0, "w_m": 0, "sw_d": 0.7, "sw_e": 0.3},

    "stu_anne_d_e2_73":  {"id": "3.2.01", "group_id": "3.2", "rank_group": "3.Y.01", "environment": "Study Room",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.7, "sw_e": 0.3},
    "stu_anne_d_e2_55":  {"id": "3.2.02", "group_id": "3.2", "rank_group": "3.Y.02", "environment": "Study Room",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.5, "sw_e": 0.5},
    "stu_anne_d_e2_37":  {"id": "3.2.03", "group_id": "3.2", "rank_group": "3.Y.03", "environment": "Study Room",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.3, "sw_e": 0.7},
    "stu_anne_d_e2_10":  {"id": "3.2.04", "group_id": "3.2", "rank_group": "3.Y.04", "environment": "Study Room",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 1, "sw_e": 0},
    "stu_anne_d_e2_01":  {"id": "3.2.05", "group_id": "3.2", "rank_group": "3.Y.05", "environment": "Study Room",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0, "sw_e": 1},
    "stu_anne_40":       {"id": "3.2.06", "group_id": "3.2", "rank_group": "3.Y.06", "environment": "Study Room",  "method": "SA", "alpha_sf": 0, "w_m": 0, "sw_d": 0.7, "sw_e": 0.3},

    "lab_evol_d_e2_73":  {"id": "3.3.01", "group_id": "3.3", "rank_group": "3.Y.01", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.7, "sw_e": 0.3},
    "lab_evol_d_e2_55":  {"id": "3.3.02", "group_id": "3.3", "rank_group": "3.Y.02", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.5, "sw_e": 0.5},
    "lab_evol_d_e2_37":  {"id": "3.3.03", "group_id": "3.3", "rank_group": "3.Y.03", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0.3, "sw_e": 0.7},
    "lab_evol_d_e2_10":  {"id": "3.3.04", "group_id": "3.3", "rank_group": "3.Y.04", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 1, "sw_e": 0},
    "lab_evol_d_e2_01":  {"id": "3.3.05", "group_id": "3.3", "rank_group": "3.Y.05", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 1, "w_m": 1, "sw_d": 0, "sw_e": 1},
    "lab_evol_40":       {"id": "3.3.06", "group_id": "3.3", "rank_group": "3.Y.06", "environment": "Laboratory",  "method": "ES",            "alpha_sf": 0, "w_m": 0, "sw_d": 0.7, "sw_e": 0.3},

    "lab_anne_d_e2_73":  {"id": "3.4.01", "group_id": "3.4", "rank_group": "3.Y.01", "environment": "Laboratory",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.7, "sw_e": 0.3},
    "lab_anne_d_e2_55":  {"id": "3.4.02", "group_id": "3.4", "rank_group": "3.Y.02", "environment": "Laboratory",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.5, "sw_e": 0.5},
    "lab_anne_d_e2_37":  {"id": "3.4.03", "group_id": "3.4", "rank_group": "3.Y.03", "environment": "Laboratory",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0.3, "sw_e": 0.7},
    "lab_anne_d_e2_10":  {"id": "3.4.04", "group_id": "3.4", "rank_group": "3.Y.04", "environment": "Laboratory",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 1, "sw_e": 0},
    "lab_anne_d_e2_01":  {"id": "3.4.05", "group_id": "3.4", "rank_group": "3.Y.05", "environment": "Laboratory",  "method": "SA", "alpha_sf": 1, "w_m": 1, "sw_d": 0, "sw_e": 1},
    "lab_anne_40":       {"id": "3.4.06", "group_id": "3.4", "rank_group": "3.Y.06", "environment": "Laboratory",  "method": "SA", "alpha_sf": 0, "w_m": 0, "sw_d": 0.7, "sw_e": 0.3},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "3.Y.01": {"alpha_sf": 1, "w_m": 1, "sw_d": 0.7, "sw_e": 0.3},
    "3.Y.02": {"alpha_sf": 1, "w_m": 1, "sw_d": 0.5, "sw_e": 0.5},
    "3.Y.03": {"alpha_sf": 1, "w_m": 1, "sw_d": 0.3, "sw_e": 0.7},
    "3.Y.04": {"alpha_sf": 1, "w_m": 1, "sw_d": 1, "sw_e": 0},
    "3.Y.05": {"alpha_sf": 1, "w_m": 1, "sw_d": 0, "sw_e": 1},
    "3.Y.06": {"alpha_sf": 0, "w_m": 0, "sw_d": 0.7, "sw_e": 0.3}
}

GROUP_PARAMS_COLUMNS = [
    ("alpha_sf",  r"$\alpha_{\text{sf}}$"), ("w_m",  r"$w_{\text{M}}$"), ("sw_d",  r"$\mathit{sw}_{\text{d}}$"), ("sw_e",  r"$\mathit{sw}_{\text{e}}$")
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("alpha_sf",  r"$\alpha_{\text{sf}}$"),
    ("w_m",  r"$w_{\text{M}}$"),
    ("sw_d",  r"$\mathit{sw}_{\text{d}}$"),
    ("sw_e",  r"$\mathit{sw}_{\text{e}}$")
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None