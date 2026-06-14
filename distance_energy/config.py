"""
distance_energy/config.py
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
    "prefix":         "distance_energy",
    "caption_prefix": "Distance and energy sub-factors",
    "type":           "standard",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time"]


# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_d2_e2_73": {"id": "2.1.01", "group_id": "2.1", "rank_group": "2.Y.01", "environment": "Study Room",  "method": "ES",            "k_d": 2, "k_e": 2},
    "stu_evol_d2_e_73":  {"id": "2.1.02", "group_id": "2.1", "rank_group": "2.Y.02", "environment": "Study Room",  "method": "ES",            "k_d": 2, "k_e": 1},
    "stu_evol_d_e2_73":  {"id": "2.1.03", "group_id": "2.1", "rank_group": "2.Y.03", "environment": "Study Room",  "method": "ES",            "k_d": 1, "k_e": 2},
    "stu_evol_d_e_73":   {"id": "2.1.04", "group_id": "2.1", "rank_group": "2.Y.04", "environment": "Study Room",  "method": "ES",            "k_d": 1, "k_e": 1},

    "stu_anne_d2_e2_73": {"id": "2.2.01", "group_id": "2.2", "rank_group": "2.Y.01", "environment": "Study Room",  "method": "SA", "k_d": 2, "k_e": 2},
    "stu_anne_d2_e_73":  {"id": "2.2.02", "group_id": "2.2", "rank_group": "2.Y.02", "environment": "Study Room",  "method": "SA", "k_d": 2, "k_e": 1},
    "stu_anne_d_e2_73":  {"id": "2.2.03", "group_id": "2.2", "rank_group": "2.Y.03", "environment": "Study Room",  "method": "SA", "k_d": 1, "k_e": 2},
    "stu_anne_d_e_73":   {"id": "2.2.04", "group_id": "2.2", "rank_group": "2.Y.04", "environment": "Study Room",  "method": "SA", "k_d": 1, "k_e": 1},

    "lab_evol_d2_e2_73": {"id": "2.3.01", "group_id": "2.3", "rank_group": "2.Y.01", "environment": "Laboratory",  "method": "ES",            "k_d": 2, "k_e": 2},
    "lab_evol_d2_e_73":  {"id": "2.3.02", "group_id": "2.3", "rank_group": "2.Y.02", "environment": "Laboratory",  "method": "ES",            "k_d": 2, "k_e": 1},
    "lab_evol_d_e2_73":  {"id": "2.3.03", "group_id": "2.3", "rank_group": "2.Y.03", "environment": "Laboratory",  "method": "ES",            "k_d": 1, "k_e": 2},
    "lab_evol_d_e_73":   {"id": "2.3.04", "group_id": "2.3", "rank_group": "2.Y.04", "environment": "Laboratory",  "method": "ES",            "k_d": 1, "k_e": 1},

    "lab_anne_d2_e2_73": {"id": "2.4.01", "group_id": "2.4", "rank_group": "2.Y.01", "environment": "Laboratory",  "method": "SA", "k_d": 2, "k_e": 2},
    "lab_anne_d2_e_73":  {"id": "2.4.02", "group_id": "2.4", "rank_group": "2.Y.02", "environment": "Laboratory",  "method": "SA", "k_d": 2, "k_e": 1},
    "lab_anne_d_e2_73":  {"id": "2.4.03", "group_id": "2.4", "rank_group": "2.Y.03", "environment": "Laboratory",  "method": "SA", "k_d": 1, "k_e": 2},
    "lab_anne_d_e_73":   {"id": "2.4.04", "group_id": "2.4", "rank_group": "2.Y.04", "environment": "Laboratory",  "method": "SA", "k_d": 1, "k_e": 1},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "2.Y.01": {"k_d": 2, "k_e": 2},
    "2.Y.02": {"k_d": 2, "k_e": 1},
    "2.Y.03": {"k_d": 1, "k_e": 2},
    "2.Y.04": {"k_d": 1, "k_e": 1},
}

GROUP_PARAMS_COLUMNS = [
    ("k_d",  r"$k_{\text{d}}$"), ("k_e",  r"$k_{\text{e}}$")
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("k_d",  r"$k_{\text{d}}$"),
    ("k_e",  r"$k_{\text{e}}$")
]
# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None