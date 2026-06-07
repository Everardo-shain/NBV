"""
area/k_sensitivity.py
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
    "prefix":         "k_sensitivity",
    "caption_prefix": "Sensitivity Analysis of $k$",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time", "delta_f"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_k3": {"id": "6.1.01", "group_id": "6.1", "rank_group": "6.Y.01", "environment": "Study Room",  "method": "(1+1)-ES", "k": 3},
    "stu_evol_k5": {"id": "6.1.02", "group_id": "6.1", "rank_group": "6.Y.02", "environment": "Study Room",  "method": "(1+1)-ES", "k": 5},
    "stu_evol_k7": {"id": "6.1.03", "group_id": "6.1", "rank_group": "6.Y.03", "environment": "Study Room",  "method": "(1+1)-ES", "k": 7},
    "stu_evol_k10": {"id": "6.1.04", "group_id": "6.1", "rank_group": "6.Y.04", "environment": "Study Room",  "method": "(1+1)-ES", "k": 10},

    "stu_anne_k3": {"id": "6.2.01", "group_id": "6.2", "rank_group": "6.Y.01", "environment": "Study Room",  "method": "Simulated Annealing", "k": 3},
    "stu_anne_k5": {"id": "6.2.02", "group_id": "6.2", "rank_group": "6.Y.02", "environment": "Study Room",  "method": "Simulated Annealing", "k": 5},
    "stu_anne_k7": {"id": "6.2.03", "group_id": "6.2", "rank_group": "6.Y.03", "environment": "Study Room",  "method": "Simulated Annealing", "k": 7},
    "stu_anne_k10": {"id": "6.2.04", "group_id": "6.2", "rank_group": "6.Y.04", "environment": "Study Room",  "method": "Simulated Annealing", "k": 10},

    "lab_evol_k3": {"id": "6.3.01", "group_id": "6.3", "rank_group": "6.Y.01", "environment": "Laboratory",  "method": "(1+1)-ES", "k": 3},
    "lab_evol_k5": {"id": "6.3.02", "group_id": "6.3", "rank_group": "6.Y.02", "environment": "Laboratory",  "method": "(1+1)-ES", "k": 5},
    "lab_evol_k7": {"id": "6.3.03", "group_id": "6.3", "rank_group": "6.Y.03", "environment": "Laboratory",  "method": "(1+1)-ES", "k": 7},
    "lab_evol_k10": {"id": "6.3.04", "group_id": "6.3", "rank_group": "6.Y.04", "environment": "Laboratory",  "method": "(1+1)-ES", "k": 10},
    
    "lab_anne_k3": {"id": "6.4.01", "group_id": "6.4", "rank_group": "6.Y.01", "environment": "Laboratory",  "method": "Simulated Annealing", "k": 3},
    "lab_anne_k5": {"id": "6.4.02", "group_id": "6.4", "rank_group": "6.Y.02", "environment": "Laboratory",  "method": "Simulated Annealing", "k": 5},
    "lab_anne_k7": {"id": "6.4.03", "group_id": "6.4", "rank_group": "6.Y.03", "environment": "Laboratory",  "method": "Simulated Annealing", "k": 7},
    "lab_anne_k10": {"id": "6.4.04", "group_id": "6.4", "rank_group": "6.Y.04", "environment": "Laboratory",  "method": "Simulated Annealing", "k": 10},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "6.Y.01": {"k": 3},
    "6.Y.02": {"k": 5},
    "6.Y.03": {"k": 7},
    "6.Y.04": {"k": 10},
}

GROUP_PARAMS_COLUMNS = [
    ("k", r"$k$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("k",       r"$k$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Sensitivity analysis configuration ───────────────────────────────────────
# Generates an additional stability table comparing totalrank change (%)
# between consecutive k values. The selected k is the smallest for which
# the change falls below this threshold.
K_STABILITY_THRESHOLD = 5.0   # percent
K_VALUES_ORDER = [3, 5, 7, 10] # must match k values in GROUPS

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None
