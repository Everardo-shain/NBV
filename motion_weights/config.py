"""
motion_weights/config.py
--------------
group_id  : who competes against whom for ranking
            (same scene + same optimization method)
rank_group: how results are aggregated in the grouped table
            (same parameter value, labeled G1-G7)
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "motion_weights",
    "caption_prefix": "Motion factor weights",
    "scene_name":     "Motion factor weights",
}

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_d_e2_73":  {"id": "3.01.01", "group_id": "3.01", "rank_group": "3.XX.01", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "stu_evol_d_e2_55":  {"id": "3.01.02", "group_id": "3.01", "rank_group": "3.XX.02", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.5f_{dist2} + 0.5f_{energ1}$"},
    "stu_evol_d_e2_37":  {"id": "3.01.03", "group_id": "3.01", "rank_group": "3.XX.03", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.3f_{dist2} + 0.7f_{energ1}$"},
    "stu_evol_d_e2_10":  {"id": "3.01.04", "group_id": "3.01", "rank_group": "3.XX.04", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$f_{dist2}$"},
    "stu_evol_d_e2_01":  {"id": "3.01.05", "group_id": "3.01", "rank_group": "3.XX.05", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$f_{energ1}$"},
    "stu_evol_40":       {"id": "3.01.06", "group_id": "3.01", "rank_group": "3.XX.06", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": 1},

    "stu_anne_d_e2_73":  {"id": "3.02.01", "group_id": "3.02", "rank_group": "3.XX.01", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "stu_anne_d_e2_55":  {"id": "3.02.02", "group_id": "3.02", "rank_group": "3.XX.02", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.5f_{dist2} + 0.5f_{energ1}$"},
    "stu_anne_d_e2_37":  {"id": "3.02.03", "group_id": "3.02", "rank_group": "3.XX.03", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.3f_{dist2} + 0.7f_{energ1}$"},
    "stu_anne_d_e2_10":  {"id": "3.02.04", "group_id": "3.02", "rank_group": "3.XX.04", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$f_{dist2}$"},
    "stu_anne_d_e2_01":  {"id": "3.02.05", "group_id": "3.02", "rank_group": "3.XX.05", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$f_{energ1}$"},
    "stu_anne_40":       {"id": "3.02.06", "group_id": "3.02", "rank_group": "3.XX.06", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": 1},

    "lab_evol_d_e2_73":  {"id": "3.03.01", "group_id": "3.03", "rank_group": "3.XX.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "lab_evol_d_e2_55":  {"id": "3.03.02", "group_id": "3.03", "rank_group": "3.XX.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.5f_{dist2} + 0.5f_{energ1}$"},
    "lab_evol_d_e2_37":  {"id": "3.03.03", "group_id": "3.03", "rank_group": "3.XX.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.3f_{dist2} + 0.7f_{energ1}$"},
    "lab_evol_d_e2_10":  {"id": "3.03.04", "group_id": "3.03", "rank_group": "3.XX.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$f_{dist2}$"},
    "lab_evol_d_e2_01":  {"id": "3.03.05", "group_id": "3.03", "rank_group": "3.XX.05", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$f_{energ1}$"},
    "lab_evol_40":       {"id": "3.03.06", "group_id": "3.03", "rank_group": "3.XX.06", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": 1},

    "lab_anne_d_e2_73":  {"id": "3.04.01", "group_id": "3.04", "rank_group": "3.XX.01", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "lab_anne_d_e2_55":  {"id": "3.04.02", "group_id": "3.04", "rank_group": "3.XX.02", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.5f_{dist2} + 0.5f_{energ1}$"},
    "lab_anne_d_e2_37":  {"id": "3.04.03", "group_id": "3.04", "rank_group": "3.XX.03", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.3f_{dist2} + 0.7f_{energ1}$"},
    "lab_anne_d_e2_10":  {"id": "3.04.04", "group_id": "3.04", "rank_group": "3.XX.04", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$f_{dist2}$"},
    "lab_anne_d_e2_01":  {"id": "3.04.05", "group_id": "3.04", "rank_group": "3.XX.05", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$f_{energ1}$"},
    "lab_anne_40":       {"id": "3.04.06", "group_id": "3.04", "rank_group": "3.XX.06", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": 1},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "3.XX.01": {"fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "3.XX.02": {"fmotion": r"$0.5f_{dist2} + 0.5f_{energ1}$"},
    "3.XX.03": {"fmotion": r"$0.3f_{dist2} + 0.7f_{energ1}$"},
    "3.XX.04": {"fmotion": r"$f_{dist2}$"},
    "3.XX.05": {"fmotion": r"$f_{energ1}$"},
    "3.XX.06": {"fmotion": 1}
}

GROUP_PARAMS_COLUMNS = [
    ("fmotion",  r"$f_{motion}$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("fmotion",  r"$f_{motion}$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None