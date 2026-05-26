"""
motion_equations/config.py
--------------
group_id  : who competes against whom for ranking
            (same scene + same optimization method)
rank_group: how results are aggregated in the grouped table
            (same parameter value, labeled G1-G7)
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "motion_equations",
    "caption_prefix": "Motion factor equations",
    "scene_name":     "Motion factor equations",
}

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_d2_e2_73": {"id": "2.01.01", "group_id": "2.01", "rank_group": "2.XX.01", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist1} + 0.3f_{energ1}$"},
    "stu_evol_d2_e_73":  {"id": "2.01.02", "group_id": "2.01", "rank_group": "2.XX.02", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist1} + 0.3f_{energ2}$"},
    "stu_evol_d_e2_73":  {"id": "2.01.03", "group_id": "2.01", "rank_group": "2.XX.03", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "stu_evol_d_e_73":   {"id": "2.01.04", "group_id": "2.01", "rank_group": "2.XX.04", "environment": "Study Room",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ2}$"},

    "stu_anne_d2_e2_73": {"id": "2.02.01", "group_id": "2.02", "rank_group": "2.XX.01", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist1} + 0.3f_{energ1}$"},
    "stu_anne_d2_e_73":  {"id": "2.02.02", "group_id": "2.02", "rank_group": "2.XX.02", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist1} + 0.3f_{energ2}$"},
    "stu_anne_d_e2_73":  {"id": "2.02.03", "group_id": "2.02", "rank_group": "2.XX.03", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "stu_anne_d_e_73":   {"id": "2.02.04", "group_id": "2.02", "rank_group": "2.XX.04", "environment": "Study Room",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ2}$"},

    "lab_evol_d2_e2_73": {"id": "2.03.01", "group_id": "2.03", "rank_group": "2.XX.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist1} + 0.3f_{energ1}$"},
    "lab_evol_d2_e_73":  {"id": "2.03.02", "group_id": "2.03", "rank_group": "2.XX.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist1} + 0.3f_{energ2}$"},
    "lab_evol_d_e2_73":  {"id": "2.03.03", "group_id": "2.03", "rank_group": "2.XX.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "lab_evol_d_e_73":   {"id": "2.03.04", "group_id": "2.03", "rank_group": "2.XX.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "fmotion": r"$0.7f_{dist2} + 0.3f_{energ2}$"},

    "lab_anne_d2_e2_73": {"id": "2.04.01", "group_id": "2.04", "rank_group": "2.XX.01", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist1} + 0.3f_{energ1}$"},
    "lab_anne_d2_e_73":  {"id": "2.04.02", "group_id": "2.04", "rank_group": "2.XX.02", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist1} + 0.3f_{energ2}$"},
    "lab_anne_d_e2_73":  {"id": "2.04.03", "group_id": "2.04", "rank_group": "2.XX.03", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "lab_anne_d_e_73":   {"id": "2.04.04", "group_id": "2.04", "rank_group": "2.XX.04", "environment": "Laboratory",  "method": "Simulated Annealing", "fmotion": r"$0.7f_{dist2} + 0.3f_{energ2}$"},
}

# ── Groups (for grouped ranked table) ─────────────────────────────────────────
# Keys match rank_group values in EXPERIMENTS
GROUPS = {
    "2.XX.01": {"fmotion": r"$0.7f_{dist1} + 0.3f_{energ1}$"},
    "2.XX.02": {"fmotion": r"$0.7f_{dist1} + 0.3f_{energ2}$"},
    "2.XX.03": {"fmotion": r"$0.7f_{dist2} + 0.3f_{energ1}$"},
    "2.XX.04": {"fmotion": r"$0.7f_{dist2} + 0.3f_{energ2}$"},
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