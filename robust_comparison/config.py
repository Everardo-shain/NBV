"""
robust_comparison/config.py
--------------
Compares robust optimization across mu values against the non-robust
baseline (mu=0) across two environments and two optimization methods.

group_id  : same environment + same optimization method
rank_group: same mu value (G1-G6)

Selection criterion:
  1. Primary filter: pct_retrieved >= PCT_THRESHOLD (all 4 sub-experiments)
  2. Among valid mu values: select the minimum mu for which
     delta_f improves by at least DELTA_F_MIN_IMPROVEMENT_PCT relative
     to mu=0 (Rob.1).
  3. If no mu passes the filter: robustness not viable with this setup.

totalrank is computed normally and reported to quantify the performance
cost of robustness. delta_f_accum is the primary robustness metric and
does not enter totalrank.
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "robust_comparison",
    "caption_prefix": "Robust Optimization Comparison",
    "type":           "comparison",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time", "delta_f"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    # Study Room — (1+1)-ES
    "stu_evol_0":   {"id": "7.1.01", "group_id": "7.1", "rank_group": "7.Y.01", "environment": "Study Room",  "method": "ES",            "mu": r"$0$"},
    "stu_evol_4":  {"id": "7.1.05", "group_id": "7.1", "rank_group": "7.Y.05", "environment": "Study Room",  "method": "ES",            "mu": r"$0.4$"},

    # Study Room — Simulated Annealing
    "stu_anne_0":   {"id": "7.2.01", "group_id": "7.2", "rank_group": "7.Y.01", "environment": "Study Room",  "method": "SA", "mu": r"$0$"},
    "stu_anne_4":  {"id": "7.2.05", "group_id": "7.2", "rank_group": "7.Y.05", "environment": "Study Room",  "method": "SA", "mu": r"$0.4$"},

    # Laboratory — (1+1)-ES
    "lab_evol_0":   {"id": "7.3.01", "group_id": "7.3", "rank_group": "7.Y.01", "environment": "Laboratory",  "method": "ES",            "mu": r"$0$"},
    "lab_evol_4":  {"id": "7.3.05", "group_id": "7.3", "rank_group": "7.Y.05", "environment": "Laboratory",  "method": "ES",            "mu": r"$0.4$"},

    # Laboratory — Simulated Annealing
    "lab_anne_0":   {"id": "7.4.01", "group_id": "7.4", "rank_group": "7.Y.01", "environment": "Laboratory",  "method": "SA", "mu": r"$0$"},
    "lab_anne_4":  {"id": "7.4.05", "group_id": "7.4", "rank_group": "7.Y.05", "environment": "Laboratory",  "method": "SA", "mu": r"$0.4$"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "7.Y.01": {"mu": r"$0$"},
    "7.Y.05": {"mu": r"$0.4$"},
}

GROUP_PARAMS_COLUMNS = [
    ("mu", r"$\mu$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("mu",      r"$\mu$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Robust comparison specific configuration ──────────────────────────────────
ROBUST_COMPARISON        = True
ROBUST_BASELINE_RG       = "7.Y.01"   # mu=0
DELTA_F_MIN_IMPROVEMENT  = 10.0       # minimum % improvement in delta_f to
                                       # consider a mu value as robust

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None