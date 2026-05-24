"""
area/config.py
--------------
HOW TO EDIT THIS FILE
---------------------
1. EXPERIMENTS: map each log filename (without .log) to its experiment ID and
   any extra columns you want in the parameters table.
2. PARAMS_COLUMNS: define which extra columns appear in the parameters table
   and how they are labeled in LaTeX.
3. RANKING: set the retrieval threshold and the frank/totalrank formulas.
4. SECTION_META: labels used in captions, file prefixes, and figure titles.

DO NOT edit anything in src/ — all logic lives there.
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":       "area",                  # used in all output filenames
    "caption_prefix": "Area factor",         # used in LaTeX table captions
    "scene_name":   "Area factor",           # used in figure suptitles
}

# ── Experiment registry ───────────────────────────────────────────────────────
# Key   : log filename stem (the file must exist at area/logs/<key>.log)
# Value : dict with mandatory key "id" (shown in tables/figures)
#         plus any extra columns for the parameters table.
EXPERIMENTS = {
    "lab_anne_34": {"id": "1.01.01", "group_id": "1.01", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.34},
    "lab_evol_34": {"id": "1.01.02", "group_id": "1.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.34},
    "stu_anne_34": {"id": "1.01.03", "group_id": "1.01", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.34},
    "stu_evol_34": {"id": "1.01.04", "group_id": "1.01", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.34},

    "lab_anne_40": {"id": "1.02.01", "group_id": "1.02", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.40},
    "lab_evol_40": {"id": "1.02.02", "group_id": "1.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.40},
    "stu_anne_40": {"id": "1.02.03", "group_id": "1.02", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.40},
    "stu_evol_40": {"id": "1.02.04", "group_id": "1.02", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.40},

    "lab_anne_50": {"id": "1.03.01", "group_id": "1.03", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.50},
    "lab_evol_50": {"id": "1.03.02", "group_id": "1.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.50},
    "stu_anne_50": {"id": "1.03.03", "group_id": "1.03", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.50},
    "stu_evol_50": {"id": "1.03.04", "group_id": "1.03", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.50},

    "lab_anne_60": {"id": "1.04.01", "group_id": "1.04", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.60},
    "lab_evol_60": {"id": "1.04.02", "group_id": "1.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.60},
    "stu_anne_60": {"id": "1.04.03", "group_id": "1.04", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.60},
    "stu_evol_60": {"id": "1.04.04", "group_id": "1.04", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.60},

    "lab_anne_70": {"id": "1.05.01", "group_id": "1.05", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.70},
    "lab_evol_70": {"id": "1.05.02", "group_id": "1.05", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.70},
    "stu_anne_70": {"id": "1.05.03", "group_id": "1.05", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.70},
    "stu_evol_70": {"id": "1.05.04", "group_id": "1.05", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.70},

    "lab_anne_80": {"id": "1.06.01", "group_id": "1.06", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.80},
    "lab_evol_80": {"id": "1.06.02", "group_id": "1.06", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.80},
    "stu_anne_80": {"id": "1.06.03", "group_id": "1.06", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.80},
    "stu_evol_80": {"id": "1.06.04", "group_id": "1.06", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.80},

    "lab_anne_90": {"id": "1.07.01", "group_id": "1.07", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.90},
    "lab_evol_90": {"id": "1.07.02", "group_id": "1.07", "environment": "Laboratory",  "method": "(1+1)-ES",            "alpha": 0.90},
    "stu_anne_90": {"id": "1.07.03", "group_id": "1.07", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.90},
    "stu_evol_90": {"id": "1.07.04", "group_id": "1.07", "environment": "Study Room",  "method": "(1+1)-ES",            "alpha": 0.90},
}

GROUPS = {
    "1.01": {"alpha": 0.34},
    "1.02": {"alpha": 0.40},
    "1.03": {"alpha": 0.50},
    "1.04": {"alpha": 0.60},
    "1.05": {"alpha": 0.70},
    "1.06": {"alpha": 0.80},
    "1.07": {"alpha": 0.90},
}

GROUP_PARAMS_COLUMNS = [
    ("alpha", r"$\alpha$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
# Defines which extra keys from EXPERIMENTS appear in the parameters table,
# in what order, and with what LaTeX column header.
# Format: [(key_in_EXPERIMENTS, latex_header), ...]
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("alpha",       r"$\alpha$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
# Minimum %retrieved an experiment must have to be included in the ranked table.
# Set to None to include all experiments regardless of retrieval.
PCT_THRESHOLD = 85.0   # e.g. 45.0

# frank and totalrank formulas as lambda expressions.
# Available variables inside the lambda (all are pd.Series):
#   drank, erank, retrrank, timerank
# (These are always computed; you choose how to combine them here.)
TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

PENALTY_MULTIPLIER = 2.0   # k in the paper