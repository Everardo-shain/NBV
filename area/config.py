"""
area/config.py
--------------
group_id  : who competes against whom for ranking
            (same scene + same optimization method)
rank_group: how results are aggregated in the grouped table
            (same parameter value, labeled G1-G7)
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "area",
    "caption_prefix": "Area factor",
    "scene_name":     "Area factor",
}

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_34": {"id": "1.01.01", "group_id": "1.01", "rank_group": "1.XX.01", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.34},
    "stu_evol_40": {"id": "1.01.02", "group_id": "1.01", "rank_group": "1.XX.02", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.40},
    "stu_evol_50": {"id": "1.01.03", "group_id": "1.01", "rank_group": "1.XX.03", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.50},
    "stu_evol_60": {"id": "1.01.04", "group_id": "1.01", "rank_group": "1.XX.04", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.60},
    "stu_evol_70": {"id": "1.01.05", "group_id": "1.01", "rank_group": "1.XX.05", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.70},
    "stu_evol_80": {"id": "1.01.06", "group_id": "1.01", "rank_group": "1.XX.06", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.80},
    "stu_evol_90": {"id": "1.01.07", "group_id": "1.01", "rank_group": "1.XX.07", "environment": "Study Room",  "method": "(1+1)-ES", "alpha": 0.90},

    "stu_anne_34": {"id": "1.02.01", "group_id": "1.02", "rank_group": "1.XX.01", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.34},
    "stu_anne_40": {"id": "1.02.02", "group_id": "1.02", "rank_group": "1.XX.02", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.40},
    "stu_anne_50": {"id": "1.02.03", "group_id": "1.02", "rank_group": "1.XX.03", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.50},
    "stu_anne_60": {"id": "1.02.04", "group_id": "1.02", "rank_group": "1.XX.04", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.60},
    "stu_anne_70": {"id": "1.02.05", "group_id": "1.02", "rank_group": "1.XX.05", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.70},
    "stu_anne_80": {"id": "1.02.06", "group_id": "1.02", "rank_group": "1.XX.06", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.80},
    "stu_anne_90": {"id": "1.02.07", "group_id": "1.02", "rank_group": "1.XX.07", "environment": "Study Room",  "method": "Simulated Annealing", "alpha": 0.90},

    "lab_evol_34": {"id": "1.03.01", "group_id": "1.03", "rank_group": "1.XX.01", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.34},
    "lab_evol_40": {"id": "1.03.02", "group_id": "1.03", "rank_group": "1.XX.02", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.40},
    "lab_evol_50": {"id": "1.03.03", "group_id": "1.03", "rank_group": "1.XX.03", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.50},
    "lab_evol_60": {"id": "1.03.04", "group_id": "1.03", "rank_group": "1.XX.04", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.60},
    "lab_evol_70": {"id": "1.03.05", "group_id": "1.03", "rank_group": "1.XX.05", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.70},
    "lab_evol_80": {"id": "1.03.06", "group_id": "1.03", "rank_group": "1.XX.06", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.80},
    "lab_evol_90": {"id": "1.03.07", "group_id": "1.03", "rank_group": "1.XX.07", "environment": "Laboratory",  "method": "(1+1)-ES", "alpha": 0.90},

    "lab_anne_34": {"id": "1.04.01", "group_id": "1.04", "rank_group": "1.XX.01", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.34},
    "lab_anne_40": {"id": "1.04.02", "group_id": "1.04", "rank_group": "1.XX.02", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.40},
    "lab_anne_50": {"id": "1.04.03", "group_id": "1.04", "rank_group": "1.XX.03", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.50},
    "lab_anne_60": {"id": "1.04.04", "group_id": "1.04", "rank_group": "1.XX.04", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.60},
    "lab_anne_70": {"id": "1.04.05", "group_id": "1.04", "rank_group": "1.XX.05", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.70},
    "lab_anne_80": {"id": "1.04.06", "group_id": "1.04", "rank_group": "1.XX.06", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.80},
    "lab_anne_90": {"id": "1.04.07", "group_id": "1.04", "rank_group": "1.XX.07", "environment": "Laboratory",  "method": "Simulated Annealing", "alpha": 0.90},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "1.XX.01": {"alpha": 0.34},
    "1.XX.02": {"alpha": 0.40},
    "1.XX.03": {"alpha": 0.50},
    "1.XX.04": {"alpha": 0.60},
    "1.XX.05": {"alpha": 0.70},
    "1.XX.06": {"alpha": 0.80},
    "1.XX.07": {"alpha": 0.90},
}

GROUP_PARAMS_COLUMNS = [
    ("alpha", r"$\alpha$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("alpha",       r"$\alpha$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None
