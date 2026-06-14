"""
area/config.py
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
    "prefix":         "area",
    "caption_prefix": "Area factor",
    "type":           "standard",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_34": {"id": "1.1.01", "group_id": "1.1", "rank_group": "1.Y.01", "environment": "Study Room",  "method": "ES", "alpha": 0.34},
    "stu_evol_40": {"id": "1.1.02", "group_id": "1.1", "rank_group": "1.Y.02", "environment": "Study Room",  "method": "ES", "alpha": 0.40},
    "stu_evol_50": {"id": "1.1.03", "group_id": "1.1", "rank_group": "1.Y.03", "environment": "Study Room",  "method": "ES", "alpha": 0.50},
    "stu_evol_60": {"id": "1.1.04", "group_id": "1.1", "rank_group": "1.Y.04", "environment": "Study Room",  "method": "ES", "alpha": 0.60},
    "stu_evol_70": {"id": "1.1.05", "group_id": "1.1", "rank_group": "1.Y.05", "environment": "Study Room",  "method": "ES", "alpha": 0.70},
    "stu_evol_80": {"id": "1.1.06", "group_id": "1.1", "rank_group": "1.Y.06", "environment": "Study Room",  "method": "ES", "alpha": 0.80},
    "stu_evol_90": {"id": "1.1.07", "group_id": "1.1", "rank_group": "1.Y.07", "environment": "Study Room",  "method": "ES", "alpha": 0.90},

    "stu_anne_34": {"id": "1.2.01", "group_id": "1.2", "rank_group": "1.Y.01", "environment": "Study Room",  "method": "SA", "alpha": 0.34},
    "stu_anne_40": {"id": "1.2.02", "group_id": "1.2", "rank_group": "1.Y.02", "environment": "Study Room",  "method": "SA", "alpha": 0.40},
    "stu_anne_50": {"id": "1.2.03", "group_id": "1.2", "rank_group": "1.Y.03", "environment": "Study Room",  "method": "SA", "alpha": 0.50},
    "stu_anne_60": {"id": "1.2.04", "group_id": "1.2", "rank_group": "1.Y.04", "environment": "Study Room",  "method": "SA", "alpha": 0.60},
    "stu_anne_70": {"id": "1.2.05", "group_id": "1.2", "rank_group": "1.Y.05", "environment": "Study Room",  "method": "SA", "alpha": 0.70},
    "stu_anne_80": {"id": "1.2.06", "group_id": "1.2", "rank_group": "1.Y.06", "environment": "Study Room",  "method": "SA", "alpha": 0.80},
    "stu_anne_90": {"id": "1.2.07", "group_id": "1.2", "rank_group": "1.Y.07", "environment": "Study Room",  "method": "SA", "alpha": 0.90},

    "lab_evol_34": {"id": "1.3.01", "group_id": "1.3", "rank_group": "1.Y.01", "environment": "Laboratory",  "method": "ES", "alpha": 0.34},
    "lab_evol_40": {"id": "1.3.02", "group_id": "1.3", "rank_group": "1.Y.02", "environment": "Laboratory",  "method": "ES", "alpha": 0.40},
    "lab_evol_50": {"id": "1.3.03", "group_id": "1.3", "rank_group": "1.Y.03", "environment": "Laboratory",  "method": "ES", "alpha": 0.50},
    "lab_evol_60": {"id": "1.3.04", "group_id": "1.3", "rank_group": "1.Y.04", "environment": "Laboratory",  "method": "ES", "alpha": 0.60},
    "lab_evol_70": {"id": "1.3.05", "group_id": "1.3", "rank_group": "1.Y.05", "environment": "Laboratory",  "method": "ES", "alpha": 0.70},
    "lab_evol_80": {"id": "1.3.06", "group_id": "1.3", "rank_group": "1.Y.06", "environment": "Laboratory",  "method": "ES", "alpha": 0.80},
    "lab_evol_90": {"id": "1.3.07", "group_id": "1.3", "rank_group": "1.Y.07", "environment": "Laboratory",  "method": "ES", "alpha": 0.90},

    "lab_anne_34": {"id": "1.4.01", "group_id": "1.4", "rank_group": "1.Y.01", "environment": "Laboratory",  "method": "SA", "alpha": 0.34},
    "lab_anne_40": {"id": "1.4.02", "group_id": "1.4", "rank_group": "1.Y.02", "environment": "Laboratory",  "method": "SA", "alpha": 0.40},
    "lab_anne_50": {"id": "1.4.03", "group_id": "1.4", "rank_group": "1.Y.03", "environment": "Laboratory",  "method": "SA", "alpha": 0.50},
    "lab_anne_60": {"id": "1.4.04", "group_id": "1.4", "rank_group": "1.Y.04", "environment": "Laboratory",  "method": "SA", "alpha": 0.60},
    "lab_anne_70": {"id": "1.4.05", "group_id": "1.4", "rank_group": "1.Y.05", "environment": "Laboratory",  "method": "SA", "alpha": 0.70},
    "lab_anne_80": {"id": "1.4.06", "group_id": "1.4", "rank_group": "1.Y.06", "environment": "Laboratory",  "method": "SA", "alpha": 0.80},
    "lab_anne_90": {"id": "1.4.07", "group_id": "1.4", "rank_group": "1.Y.07", "environment": "Laboratory",  "method": "SA", "alpha": 0.90},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "1.Y.01": {"alpha": 0.34},
    "1.Y.02": {"alpha": 0.40},
    "1.Y.03": {"alpha": 0.50},
    "1.Y.04": {"alpha": 0.60},
    "1.Y.05": {"alpha": 0.70},
    "1.Y.06": {"alpha": 0.80},
    "1.Y.07": {"alpha": 0.90},
}

GROUP_PARAMS_COLUMNS = [
    ("alpha", r"$\alpha$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("alpha",       r"$\alpha$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None
