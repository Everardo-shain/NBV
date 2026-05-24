"""
motion_equations/config.py
"""

# ── Section identity ──────────────────────────────────────────────────────────
SECTION_META = {
    "prefix":         "motion_equations",
    "caption_prefix": "Motion factor equations",
    "scene_name":     "Motion factor equations",
}

# ── Experiment registry ───────────────────────────────────────────────────────
EXPERIMENTS = {
    "lab_anne_d2_e2_73": {"id": "2.01.01", "group_id": "2.01", "environment": "Laboratory",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "lab_evol_d2_e2_73": {"id": "2.01.02", "group_id": "2.01", "environment": "Laboratory",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "stu_anne_d2_e2_73": {"id": "2.01.03", "group_id": "2.01", "environment": "Study Room",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "stu_evol_d2_e2_73": {"id": "2.01.04", "group_id": "2.01", "environment": "Study Room",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},

    "lab_anne_d2_e_73":  {"id": "2.02.01", "group_id": "2.02", "environment": "Laboratory",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "lab_evol_d2_e_73":  {"id": "2.02.02", "group_id": "2.02", "environment": "Laboratory",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "stu_anne_d2_e_73":  {"id": "2.02.03", "group_id": "2.02", "environment": "Study Room",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "stu_evol_d2_e_73":  {"id": "2.02.04", "group_id": "2.02", "environment": "Study Room",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},

    "lab_anne_d_e2_73":  {"id": "2.03.01", "group_id": "2.03", "environment": "Laboratory",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "lab_evol_d_e2_73":  {"id": "2.03.02", "group_id": "2.03", "environment": "Laboratory",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "stu_anne_d_e2_73":  {"id": "2.03.03", "group_id": "2.03", "environment": "Study Room",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "stu_evol_d_e2_73":  {"id": "2.03.04", "group_id": "2.03", "environment": "Study Room",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},

    "lab_anne_d_e_73":   {"id": "2.04.01", "group_id": "2.04", "environment": "Laboratory",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "lab_evol_d_e_73":   {"id": "2.04.02", "group_id": "2.04", "environment": "Laboratory",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "stu_anne_d_e_73":   {"id": "2.04.03", "group_id": "2.04", "environment": "Study Room",  "method": "Simulated Annealing", "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "stu_evol_d_e_73":   {"id": "2.04.04", "group_id": "2.04", "environment": "Study Room",  "method": "(1+1)-ES",            "fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
}

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "2.01": {"fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "2.02": {"fdist": r"Eq.~\ref{eq:fun_dist_1}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
    "2.03": {"fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_1}"},
    "2.04": {"fdist": r"Eq.~\ref{eq:fun_dist_2}", "fenerg": r"Eq.~\ref{eq:fun_energ_2}"},
}

GROUP_PARAMS_COLUMNS = [
    ("fdist",  r"$f_{dist}$"),
    ("fenerg", r"$f_{energ}$"),
]

# ── Parameters table columns ──────────────────────────────────────────────────
PARAMS_COLUMNS = [
    ("environment", "Environment"),
    ("method",      "Local Opt. Method"),
    ("fdist",       r"$f_{dist}$"),
    ("fenerg",      r"$f_{energ}$"),
]

# ── Ranking configuration ─────────────────────────────────────────────────────
PCT_THRESHOLD = 85.0

TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * ((drank + erank + retrrank + qrank) / 4.0) + 0.3 * timerank
)

PENALTY_MULTIPLIER = 2.0

# ── Google Sheets ─────────────────────────────────────────────────────────────
SPREADSHEET_ID = None