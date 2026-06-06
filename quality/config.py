"""
quality/config.py
--------------
group_id  : who competes against whom for ranking
            (same scene + same optimization method)
rank_group: how results are aggregated in the grouped table
            (same parameter value, labeled G1-G7)
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "quality",
    "caption_prefix": "Quality factor",
}

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "stu_evol_1a1m":    {"id": "4.1.01", "group_id": "4.1", "rank_group": "4.Y.01", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
    "stu_evol_1a1m1q":  {"id": "4.1.02", "group_id": "4.1", "rank_group": "4.Y.02", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$ \cdot f_{\text{quality}}$"},
    "stu_evol_1a7m3q":  {"id": "4.1.03", "group_id": "4.1", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.7f_{\text{motion}} + 0.3f_{\text{quality}})$"},
    "stu_evol_1a5m5q":  {"id": "4.1.04", "group_id": "4.1", "rank_group": "4.Y.04", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "stu_evol_1a3m7q":  {"id": "4.1.05", "group_id": "4.1", "rank_group": "4.Y.05", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.3f_{\text{motion}} + 0.7f_{\text{quality}})$"},
    "stu_evol_1m7a3q":  {"id": "4.1.06", "group_id": "4.1", "rank_group": "4.Y.06", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.7f_{\text{area}} + 0.3f_{\text{quality}})$"},
    "stu_evol_1m5a5q":  {"id": "4.1.07", "group_id": "4.1", "rank_group": "4.Y.07", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.5f_{\text{area}} + 0.5f_{\text{quality}})$"},
    "stu_evol_1m3a7q":  {"id": "4.1.08", "group_id": "4.1", "rank_group": "4.Y.08", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.3f_{\text{area}} + 0.7f_{\text{quality}})$"},
    "stu_evol_1q7a3m":  {"id": "4.1.09", "group_id": "4.1", "rank_group": "4.Y.09", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.7f_{\text{area}} + 0.3f_{\text{motion}})$"},
    "stu_evol_1q5a5m":  {"id": "4.1.10", "group_id": "4.1", "rank_group": "4.Y.10", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.5f_{\text{area}} + 0.5f_{\text{motion}})$"},
    "stu_evol_1q3a7m":  {"id": "4.1.11", "group_id": "4.1", "rank_group": "4.Y.11", "environment": "Study Room",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.3f_{\text{area}} + 0.7f_{\text{motion}})$"},

    "stu_anne_1a1m":    {"id": "4.2.01", "group_id": "4.2", "rank_group": "4.Y.01", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
    "stu_anne_1a1m1q":  {"id": "4.2.02", "group_id": "4.2", "rank_group": "4.Y.02", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$ \cdot f_{\text{quality}}$"},
    "stu_anne_1a7m3q":  {"id": "4.2.03", "group_id": "4.2", "rank_group": "4.Y.03", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.7f_{\text{motion}} + 0.3f_{\text{quality}})$"},
    "stu_anne_1a5m5q":  {"id": "4.2.04", "group_id": "4.2", "rank_group": "4.Y.04", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "stu_anne_1a3m7q":  {"id": "4.2.05", "group_id": "4.2", "rank_group": "4.Y.05", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.3f_{\text{motion}} + 0.7f_{\text{quality}})$"},
    "stu_anne_1m7a3q":  {"id": "4.2.06", "group_id": "4.2", "rank_group": "4.Y.06", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.7f_{\text{area}} + 0.3f_{\text{quality}})$"},
    "stu_anne_1m5a5q":  {"id": "4.2.07", "group_id": "4.2", "rank_group": "4.Y.07", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.5f_{\text{area}} + 0.5f_{\text{quality}})$"},
    "stu_anne_1m3a7q":  {"id": "4.2.08", "group_id": "4.2", "rank_group": "4.Y.08", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.3f_{\text{area}} + 0.7f_{\text{quality}})$"},
    "stu_anne_1q7a3m":  {"id": "4.2.09", "group_id": "4.2", "rank_group": "4.Y.09", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.7f_{\text{area}} + 0.3f_{\text{motion}})$"},
    "stu_anne_1q5a5m":  {"id": "4.2.10", "group_id": "4.2", "rank_group": "4.Y.10", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.5f_{\text{area}} + 0.5f_{\text{motion}})$"},
    "stu_anne_1q3a7m":  {"id": "4.2.11", "group_id": "4.2", "rank_group": "4.Y.11", "environment": "Study Room",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.3f_{\text{area}} + 0.7f_{\text{motion}})$"},

    "lab_evol_1a1m":    {"id": "4.3.01", "group_id": "4.3", "rank_group": "4.Y.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
    "lab_evol_1a1m1q":  {"id": "4.3.02", "group_id": "4.3", "rank_group": "4.Y.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$ \cdot f_{\text{quality}}$"},
    "lab_evol_1a7m3q":  {"id": "4.3.03", "group_id": "4.3", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.7f_{\text{motion}} + 0.3f_{\text{quality}})$"},
    "lab_evol_1a5m5q":  {"id": "4.3.04", "group_id": "4.3", "rank_group": "4.Y.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "lab_evol_1a3m7q":  {"id": "4.3.05", "group_id": "4.3", "rank_group": "4.Y.05", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{area}}(0.3f_{\text{motion}} + 0.7f_{\text{quality}})$"},
    "lab_evol_1m7a3q":  {"id": "4.3.06", "group_id": "4.3", "rank_group": "4.Y.06", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.7f_{\text{area}} + 0.3f_{\text{quality}})$"},
    "lab_evol_1m5a5q":  {"id": "4.3.07", "group_id": "4.3", "rank_group": "4.Y.07", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.5f_{\text{area}} + 0.5f_{\text{quality}})$"},
    "lab_evol_1m3a7q":  {"id": "4.3.08", "group_id": "4.3", "rank_group": "4.Y.08", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{motion}}(0.3f_{\text{area}} + 0.7f_{\text{quality}})$"},
    "lab_evol_1q7a3m":  {"id": "4.3.09", "group_id": "4.3", "rank_group": "4.Y.09", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.7f_{\text{area}} + 0.3f_{\text{motion}})$"},
    "lab_evol_1q5a5m":  {"id": "4.3.10", "group_id": "4.3", "rank_group": "4.Y.10", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.5f_{\text{area}} + 0.5f_{\text{motion}})$"},
    "lab_evol_1q3a7m":  {"id": "4.3.11", "group_id": "4.3", "rank_group": "4.Y.11", "environment": "Laboratory",  "method": "(1+1)-ES",            "f": r"$f_{\text{quality}}(0.3f_{\text{area}} + 0.7f_{\text{motion}})$"},

    "lab_anne_1a1m":    {"id": "4.4.01", "group_id": "4.4", "rank_group": "4.Y.01", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
    "lab_anne_1a1m1q":  {"id": "4.4.02", "group_id": "4.4", "rank_group": "4.Y.02", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}} \cdot f_{\text{motion}}$ \cdot f_{\text{quality}}$"},
    "lab_anne_1a7m3q":  {"id": "4.4.03", "group_id": "4.4", "rank_group": "4.Y.03", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.7f_{\text{motion}} + 0.3f_{\text{quality}})$"},
    "lab_anne_1a5m5q":  {"id": "4.4.04", "group_id": "4.4", "rank_group": "4.Y.04", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "lab_anne_1a3m7q":  {"id": "4.4.05", "group_id": "4.4", "rank_group": "4.Y.05", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{area}}(0.3f_{\text{motion}} + 0.7f_{\text{quality}})$"},
    "lab_anne_1m7a3q":  {"id": "4.4.06", "group_id": "4.4", "rank_group": "4.Y.06", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.7f_{\text{area}} + 0.3f_{\text{quality}})$"},
    "lab_anne_1m5a5q":  {"id": "4.4.07", "group_id": "4.4", "rank_group": "4.Y.07", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.5f_{\text{area}} + 0.5f_{\text{quality}})$"},
    "lab_anne_1m3a7q":  {"id": "4.4.08", "group_id": "4.4", "rank_group": "4.Y.08", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{motion}}(0.3f_{\text{area}} + 0.7f_{\text{quality}})$"},
    "lab_anne_1q7a3m":  {"id": "4.4.09", "group_id": "4.4", "rank_group": "4.Y.09", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.7f_{\text{area}} + 0.3f_{\text{motion}})$"},
    "lab_anne_1q5a5m":  {"id": "4.4.10", "group_id": "4.4", "rank_group": "4.Y.10", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.5f_{\text{area}} + 0.5f_{\text{motion}})$"},
    "lab_anne_1q3a7m":  {"id": "4.4.11", "group_id": "4.4", "rank_group": "4.Y.11", "environment": "Laboratory",  "method": "Simulated Annealing", "f": r"$f_{\text{quality}}(0.3f_{\text{area}} + 0.7f_{\text{motion}})$"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "4.Y.01": {"f": r"$f_{\text{area}} \cdot f_{\text{motion}}$"},
    "4.Y.02": {"f": r"$f_{\text{area}} \cdot f_{\text{motion}}$ \cdot f_{\text{quality}}$"},
    "4.Y.03": {"f": r"$f_{\text{area}}(0.7f_{\text{motion}} + 0.3f_{\text{quality}})$"},
    "4.Y.04": {"f": r"$f_{\text{area}}(0.5f_{\text{motion}} + 0.5f_{\text{quality}})$"},
    "4.Y.05": {"f": r"$f_{\text{area}}(0.3f_{\text{motion}} + 0.7f_{\text{quality}})$"},
    "4.Y.06": {"f": r"$f_{\text{motion}}(0.7f_{\text{area}} + 0.3f_{\text{quality}})$"},
    "4.Y.07": {"f": r"$f_{\text{motion}}(0.5f_{\text{area}} + 0.5f_{\text{quality}})$"},
    "4.Y.08": {"f": r"$f_{\text{motion}}(0.3f_{\text{area}} + 0.7f_{\text{quality}})$"},
    "4.Y.09": {"f": r"$f_{\text{quality}}(0.7f_{\text{area}} + 0.3f_{\text{motion}})$"},
    "4.Y.10": {"f": r"$f_{\text{quality}}(0.5f_{\text{area}} + 0.5f_{\text{motion}})$"},
    "4.Y.11": {"f": r"$f_{\text{quality}}(0.3f_{\text{area}} + 0.7f_{\text{motion}})$"},
}

GROUP_PARAMS_COLUMNS = [
    ("f",  r"$f$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("f",  r"$f$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None