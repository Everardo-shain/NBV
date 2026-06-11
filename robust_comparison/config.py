"""
robust_comparison/config.py
--------------
Compares robust optimization across lambda values against the non-robust
baseline (lambda=0) across two environments and two optimization methods.

group_id  : same environment + same optimization method
rank_group: same lambda value (G1-G6)

Selection criterion:
  1. Primary filter: pct_retrieved >= PCT_THRESHOLD (all 4 sub-experiments)
  2. Among valid lambda values: select the minimum lambda for which
     delta_f improves by at least DELTA_F_MIN_IMPROVEMENT_PCT relative
     to lambda=0 (Rob.1).
  3. If no lambda passes the filter: robustness not viable with this setup.

totalrank is computed normally and reported to quantify the performance
cost of robustness. delta_f_accum is the primary robustness metric and
does not enter totalrank.
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "robust_comparison",
    "caption_prefix": "Robust Optimization Comparison",
}

# ── Metrics to include ────────────────────────────────────────────────────────
METRICS = ["distance", "energy", "retrieved", "quality", "time", "delta_f"]

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    # Study Room — (1+1)-ES
    "stu_evol_lam0":   {"id": "7.1.01", "group_id": "7.1", "rank_group": "7.Y.01", "environment": "Study Room",  "method": "ES",            "lambda": r"$0$"},
    "stu_evol_lam01":  {"id": "7.1.02", "group_id": "7.1", "rank_group": "7.Y.02", "environment": "Study Room",  "method": "ES",            "lambda": r"$0.1$"},
    "stu_evol_lam02":  {"id": "7.1.03", "group_id": "7.1", "rank_group": "7.Y.03", "environment": "Study Room",  "method": "ES",            "lambda": r"$0.2$"},
    "stu_evol_lam03":  {"id": "7.1.04", "group_id": "7.1", "rank_group": "7.Y.04", "environment": "Study Room",  "method": "ES",            "lambda": r"$0.3$"},
    "stu_evol_lam05":  {"id": "7.1.05", "group_id": "7.1", "rank_group": "7.Y.05", "environment": "Study Room",  "method": "ES",            "lambda": r"$0.5$"},
    "stu_evol_lam07":  {"id": "7.1.06", "group_id": "7.1", "rank_group": "7.Y.06", "environment": "Study Room",  "method": "ES",            "lambda": r"$0.7$"},

    # Study Room — Simulated Annealing
    "stu_anne_lam0":   {"id": "7.2.01", "group_id": "7.2", "rank_group": "7.Y.01", "environment": "Study Room",  "method": "SA", "lambda": r"$0$"},
    "stu_anne_lam01":  {"id": "7.2.02", "group_id": "7.2", "rank_group": "7.Y.02", "environment": "Study Room",  "method": "SA", "lambda": r"$0.1$"},
    "stu_anne_lam02":  {"id": "7.2.03", "group_id": "7.2", "rank_group": "7.Y.03", "environment": "Study Room",  "method": "SA", "lambda": r"$0.2$"},
    "stu_anne_lam03":  {"id": "7.2.04", "group_id": "7.2", "rank_group": "7.Y.04", "environment": "Study Room",  "method": "SA", "lambda": r"$0.3$"},
    "stu_anne_lam05":  {"id": "7.2.05", "group_id": "7.2", "rank_group": "7.Y.05", "environment": "Study Room",  "method": "SA", "lambda": r"$0.5$"},
    "stu_anne_lam07":  {"id": "7.2.06", "group_id": "7.2", "rank_group": "7.Y.06", "environment": "Study Room",  "method": "SA", "lambda": r"$0.7$"},

    # Laboratory — (1+1)-ES
    "lab_evol_lam0":   {"id": "7.3.01", "group_id": "7.3", "rank_group": "7.Y.01", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0$"},
    "lab_evol_lam01":  {"id": "7.3.02", "group_id": "7.3", "rank_group": "7.Y.02", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0.1$"},
    "lab_evol_lam02":  {"id": "7.3.03", "group_id": "7.3", "rank_group": "7.Y.03", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0.2$"},
    "lab_evol_lam03":  {"id": "7.3.04", "group_id": "7.3", "rank_group": "7.Y.04", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0.3$"},
    "lab_evol_lam05":  {"id": "7.3.05", "group_id": "7.3", "rank_group": "7.Y.05", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0.5$"},
    "lab_evol_lam07":  {"id": "7.3.06", "group_id": "7.3", "rank_group": "7.Y.06", "environment": "Laboratory",  "method": "ES",            "lambda": r"$0.7$"},

    # Laboratory — Simulated Annealing
    "lab_anne_lam0":   {"id": "7.4.01", "group_id": "7.4", "rank_group": "7.Y.01", "environment": "Laboratory",  "method": "SA", "lambda": r"$0$"},
    "lab_anne_lam01":  {"id": "7.4.02", "group_id": "7.4", "rank_group": "7.Y.02", "environment": "Laboratory",  "method": "SA", "lambda": r"$0.1$"},
    "lab_anne_lam02":  {"id": "7.4.03", "group_id": "7.4", "rank_group": "7.Y.03", "environment": "Laboratory",  "method": "SA", "lambda": r"$0.2$"},
    "lab_anne_lam03":  {"id": "7.4.04", "group_id": "7.4", "rank_group": "7.Y.04", "environment": "Laboratory",  "method": "SA", "lambda": r"$0.3$"},
    "lab_anne_lam05":  {"id": "7.4.05", "group_id": "7.4", "rank_group": "7.Y.05", "environment": "Laboratory",  "method": "SA", "lambda": r"$0.5$"},
    "lab_anne_lam07":  {"id": "7.4.06", "group_id": "7.4", "rank_group": "7.Y.06", "environment": "Laboratory",  "method": "SA", "lambda": r"$0.7$"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "7.Y.01": {"lambda": r"$0$   (baseline)"},
    "7.Y.02": {"lambda": r"$0.1$"},
    "7.Y.03": {"lambda": r"$0.2$"},
    "7.Y.04": {"lambda": r"$0.3$"},
    "7.Y.05": {"lambda": r"$0.5$"},
    "7.Y.06": {"lambda": r"$0.7$"},
}

GROUP_PARAMS_COLUMNS = [
    ("lambda", r"$\lambda$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environ."),
    ("method",      "Method"),
    ("lambda",      r"$\lambda$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Robust comparison specific configuration ──────────────────────────────────
ROBUST_COMPARISON        = True
ROBUST_BASELINE_RG       = "7.Y.01"   # lambda=0
DELTA_F_MIN_IMPROVEMENT  = 10.0       # minimum % improvement in delta_f to
                                       # consider a lambda value as robust

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None