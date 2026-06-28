from pathlib import Path
from sys import prefix
from wsgiref import headers
import pandas as pd
import re

# ── Full column registry ──────────────────────────────────────────────────────
# metric_key → (results_col, results_header, results_hib,
#               rank_col,    rank_header,    rank_hib,    alignment)
_METRIC_REGISTRY = {

    "distance":  ("acc_dist_m",    r"\thead{Acc.\\ dist. (m)}", False,

                  "drank",         r"$d_{\text{rank}}$",        False, "r"),

    "energy":    ("acc_energy",    r"\thead{Acc.\\ energy}",    False,

                  "erank",         r"$e_{\text{rank}}$",        False, "r"),

    "retrieved": ("pct_retrieved", r"\thead{Retr.\\ (\%)}",     True,

                  "retrrank",      r"$r_{\text{rank}}$",        False, "r"),

    "quality":   ("mean_quality",  r"\thead{Mean\\ quality}",   True,

                  "qrank",         r"$q_{\text{rank}}$",        False, "r"),

    "time":      ("total_time_s",  r"\thead{Time\\ (s)}",       False,

                  "timerank",      r"$t_{\text{rank}}$",        False, "r"),

    "delta_f":   ("acc_delta_f",   r"\thead{Acc.\\ $\Delta f$}",False,

                  None,            None,                        False, "r"),

}



# "totalrank" is always the last rank column
_TOTALRANK_HDR = (r"$\text{total}_{\text{rank}}$", False, "r")

HIGH_PRECISION_COLS = {"mean_quality", "tri_quality", "acc_delta_f"}

COL_ALIGN = {
    "experiment_id": "l",
    "method":        "l",
    "id":            "l",
    "environment":   "l",
    "success_count": "c",
    "totalrank":     "r",
}


def _active_metrics(metrics: list) -> list:
    """Return metric keys present in the registry, preserving order."""
    return [m for m in metrics if m in _METRIC_REGISTRY]


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(v, dec=2):
    if pd.isna(v):
        return "--"
    if isinstance(v, int) or (isinstance(v, float) and v == int(v)):
        return str(int(v))
    return f"{float(v):.{dec}f}"


def _italic(s):  return r"\textit{" + s + "}"


def _bold(s):
    # 1. LIMPIEZA INICIAL: Si la cadena contiene "rank", la estandarizamos
    if "rank" in s:
        # Removemos la sintaxis vieja de LaTeX para extraer el texto limpio
        s_clean = s.replace("$", "").replace(r"\bm", "").replace(r"\text", "")
        s_clean = s_clean.replace("{", "").replace("}", "").strip()
        
        if "_" in s_clean:
            base = s_clean.split("_")[0].strip()
            
            # Si la base es "total", envolvemos en $...$ usando \textbf para un negro intenso
            if base == "total":
                return r"$\textbf{total}_{\textbf{rank}}$"
            
            # Si es una letra individual (d, e, r, q, t), combinamos \bm y \textbf
            elif len(base) == 1:
                return rf"$\bm{{{base}}}_{{\textbf{{rank}}}}$"

    # 2. CASO ESTÁNDAR: Si es una fórmula matemática pura de principio a fin: $...$
    if s.startswith("$") and s.endswith("$"):
        content = s[1:-1]
        return r"$\bm{" + content + "}$"
    
    # 3. CASO MIXTO: Si la cadena contiene una mezcla de texto y fórmulas general
    if "$" in s:
        return re.sub(r'\$(.*?)\$', r'$\\\bm{\1}$', s)
    
    # 4. CASO TEXTO: Si es texto común y corriente sin matemáticas (como "ID")
    return r"\textbf{" + s + "}"


def _parse_id(x):
    parts = str(x).split(".")
    result = []
    for p in parts:
        clean = p.lstrip("Gg")
        try:    result.append(int(clean))
        except: result.append(p)
    return result


def _sort_by_id(df):
    df = df.copy()
    df["_sort_key"] = df["experiment_id"].apply(_parse_id)
    return df.sort_values("_sort_key").drop(columns="_sort_key").reset_index(drop=True)


def _col_spec(display, col_defs):
    aligns = []
    for i, c in enumerate(display):
        if c in COL_ALIGN:
            aligns.append(COL_ALIGN[c])
        elif c in col_defs:
            aligns.append(col_defs[c])
        else:
            aligns.append("l" if i == 0 else "r")
    return "@{}" + "".join(aligns) + "@{}"


# ── Core LaTeX builder ────────────────────────────────────────────────────────

def _to_latex(fmt_df, cols, col_aligns, headers,
              caption, label, include_method,
              two_col=False, group_col=None,
              group_separator=r"\noalign{\smallskip}"):
    display = ["experiment_id"]
    if include_method and "method" in fmt_df.columns:
        display.append("method")
    display += [c for c in cols if c in fmt_df.columns]

    hdr_map = {"experiment_id": "ID", "method": "Method"}
    hdr_map.update(headers)

    spec       = _col_spec(display, col_aligns)
    header_row = " & ".join(_bold(hdr_map.get(c, c)) for c in display) + r" \\"
    table_env  = "table*" if two_col else "table"

    rows = []
    prev_group = None
    for _, row in fmt_df.iterrows():
        current_group = row.get(group_col) if group_col else None
        if group_col and prev_group is not None and current_group != prev_group:
            rows.append(group_separator)
        rows.append(" & ".join(str(row[c]) for c in display) + r" \\")
        prev_group = current_group

    body = "\n    ".join(rows)

    return (
        rf"\begin{{{table_env}}}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        rf"\end{{{table_env}}}"
    )


# ── Results table ─────────────────────────────────────────────────────────────

def _format_results(df, metrics):
    out       = df.copy().astype(object)
    has_valid = "is_valid" in df.columns
    active    = _active_metrics(metrics)

    for mkey in active:
        res_col, _, hib, _, _, _, _ = _METRIC_REGISTRY[mkey]
        if res_col not in df.columns:
            continue
        series = df[res_col].astype(float)
        dec    = 3 if res_col in HIGH_PRECISION_COLS else 2
        out[res_col] = series.map(lambda v, d=dec: _fmt(v, d))

        if has_valid:
            for idx in df[df["is_valid"] == False].index:
                out.at[idx, res_col] = _italic(out.at[idx, res_col])

        if "group_id" in df.columns:
            for _, grp in df.groupby("group_id"):
                valid_grp = grp[grp["is_valid"] == True] if has_valid else grp
                if valid_grp.empty:
                    continue
                grp_series = series[valid_grp.index]
                best_idx   = grp_series.idxmax() if hib else grp_series.idxmin()
                out.at[best_idx, res_col] = _bold(out.at[best_idx, res_col])
        else:
            valid_s  = series[df["is_valid"] == True] if has_valid else series
            best_idx = valid_s.idxmax() if hib else valid_s.idxmin()
            out.at[best_idx, res_col] = _bold(out.at[best_idx, res_col])

    return out


def results_table(df, caption, label, include_method=True,
                  two_col=False, metrics=None):
    if metrics is None:
        metrics = list(_METRIC_REGISTRY.keys())
    active  = _active_metrics(metrics)
    cols    = [_METRIC_REGISTRY[m][0] for m in active]
    aligns  = {_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][6] for m in active}
    headers = {_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][1] for m in active}

    fmt = _format_results(df, metrics)
    if "group_id" in df.columns:
        fmt["group_id"] = df["group_id"].values

    return _to_latex(fmt, cols, aligns, headers, caption, label,
                     include_method, two_col,
                     group_col="group_id" if "group_id" in df.columns else None)


# ── Ranked table ──────────────────────────────────────────────────────────────

def _format_ranked(df, metrics):
    out    = df.copy().astype(object)
    active = _active_metrics(metrics)
    rank_entries = [(m, _METRIC_REGISTRY[m][3], _METRIC_REGISTRY[m][5])
                    for m in active if _METRIC_REGISTRY[m][3] is not None]
    rank_entries.append(("_totalrank", "totalrank", False))

    for _, rank_col, hib in rank_entries:
        if rank_col not in df.columns:
            continue
        series = df[rank_col].astype(float)
        out[rank_col] = series.map(lambda v: _fmt(v, 3))

        if "group_id" in df.columns:
            for _, grp in df.groupby("group_id"):
                grp_s    = series[grp.index]
                best_idx = grp_s.idxmax() if hib else grp_s.idxmin()
                out.at[best_idx, rank_col] = _bold(out.at[best_idx, rank_col])
        else:
            best_idx = series.idxmax() if hib else series.idxmin()
            out.at[best_idx, rank_col] = _bold(out.at[best_idx, rank_col])

    return out


def ranked_table(df, caption, label, include_method=True,
                 two_col=False, metrics=None):
    if metrics is None:
        metrics = list(_METRIC_REGISTRY.keys())
    active = _active_metrics(metrics)

    rank_cols    = [_METRIC_REGISTRY[m][3] for m in active if _METRIC_REGISTRY[m][3] is not None] + ["totalrank"]
    rank_aligns  = {_METRIC_REGISTRY[m][3]: _METRIC_REGISTRY[m][6] for m in active if _METRIC_REGISTRY[m][3] is not None}
    rank_aligns["totalrank"] = "r"
    rank_headers = {_METRIC_REGISTRY[m][3]: _METRIC_REGISTRY[m][4] for m in active if _METRIC_REGISTRY[m][3] is not None}
    rank_headers["totalrank"] = _TOTALRANK_HDR[0]

    fmt = _format_ranked(df, metrics)
    if "group_id" in df.columns:
        fmt["group_id"] = df["group_id"].values

    return _to_latex(fmt, rank_cols, rank_aligns, rank_headers, caption, label,
                     include_method, two_col,
                     group_col="group_id" if "group_id" in df.columns else None)


# ── Params table ──────────────────────────────────────────────────────────────

def params_table(experiments_cfg, params_columns, caption, label, note=None):
    col_keys    = ["id"] + [k for k, _ in params_columns]
    col_headers = {"id": "ID", **{k: h for k, h in params_columns}}
    spec        = "@{}" + "l" * len(col_keys) + "@{}"
    header_row  = " & ".join(_bold(col_headers[k]) for k in col_keys) + r" \\"

    rows, prev_group = [], None
    for cfg in experiments_cfg.values():
        current_group = cfg.get("group_id")
        if prev_group is not None and current_group != prev_group:
            rows.append(r"\noalign{\smallskip}")
        rows.append(" & ".join(str(cfg.get(k, "")) for k in col_keys) + r" \\")
        prev_group = current_group

    body     = "\n    ".join(rows)
    note_tex = f"\n\\vspace{{2pt}}\n\\raggedright\\footnotesize {note}" if note else ""

    return (
        r"\begin{table}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        r"\hline" "\n"
        r"\end{tabular}"
        f"{note_tex}\n"
        r"\end{table}"
    )


# ── Grouped ranked table ──────────────────────────────────────────────────────

def grouped_ranked_table(groups_cfg, grouped_df, group_params_columns,
                         caption, label):
    grp_sorted     = _sort_by_id(grouped_df)
    groups_with_id = {k: {"id": k, **v} for k, v in groups_cfg.items()}
    n_total        = 4

    param_col_keys = (["id"] + [k for k, _ in group_params_columns]
                      + ["success_count", "totalrank"])
    param_col_hdrs = {
        "id":            "ID",
        "success_count": rf"$n_s/{n_total}$",
        "totalrank":     r"$\textbf{group}_{\textbf{rank}}$",
        **{k: h for k, h in group_params_columns},
    }
    param_aligns = (["l"] * (1 + len(group_params_columns)) + ["c", "r"])
    spec         = "@{}" + "".join(param_aligns) + "@{}"
    header_row   = " & ".join(_bold(param_col_hdrs[k]) for k in param_col_keys) + r" \\"

    if not grouped_df.empty and "success_count" in grouped_df.columns:
        sorted_w   = grouped_df.sort_values(["success_count", "totalrank"],
                                             ascending=[False, True])
        winner_id  = sorted_w.iloc[0]["experiment_id"]
        winning_by = sorted_w.iloc[0].get("winning_criterion", "")
        if not winning_by and len(sorted_w) > 1:
            winning_by = ("success_count"
                          if sorted_w.iloc[0]["success_count"] > sorted_w.iloc[1]["success_count"]
                          else "totalrank")
    else:
        winner_id  = grp_sorted.iloc[0]["experiment_id"] if not grp_sorted.empty else None
        winning_by = ""

    rows = []
    for gid, gdata in groups_with_id.items():
        match = grp_sorted[grp_sorted["experiment_id"] == gid]
        if match.empty:
            cells  = [str(gdata.get(k, "")) for k in ["id"] + [k for k, _ in group_params_columns]]
            cells += ["--", "--"]
            rows.append(" & ".join(cells) + r" \\")
            continue

        tr        = match["totalrank"].values[0]
        ns        = int(match["success_count"].values[0]) if "success_count" in match.columns else 0
        is_winner = (gid == winner_id)
        tr_fmt    = "--" if pd.isna(tr) else _fmt(tr)
        ns_fmt    = str(ns)

        if is_winner:
            param_cells = [_bold(str(gdata.get(k, "")))
                           for k in ["id"] + [k for k, _ in group_params_columns]]
            if winning_by == "success_count":
                ns_fmt = _bold(r"\underline{" + ns_fmt + "}")
                tr_fmt = _bold(tr_fmt)
            else:
                ns_fmt = _bold(ns_fmt)
                tr_fmt = _bold(r"\underline{" + tr_fmt + "}") if not pd.isna(tr) else _bold(tr_fmt)
            cells = param_cells + [ns_fmt, tr_fmt]
        else:
            cells = ([str(gdata.get(k, ""))
                      for k in ["id"] + [k for k, _ in group_params_columns]]
                     + [ns_fmt, tr_fmt])

        rows.append(" & ".join(cells) + r" \\")

    body = "\n    ".join(rows)
    return (
        r"\begin{table}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        r"\end{table}"
    )


def robust_comparison_table(
    ranked_df, grouped_df, experiments_cfg,
    baseline_rg, delta_f_min_improvement,
    caption, label,
):
    """
    Side-by-side comparison table for all mu values.
    Columns: mu | n_s/4 | totalrank | acc_delta_f | delta_f improvement % | Selected
    """
    baseline_row = grouped_df[grouped_df["experiment_id"] == baseline_rg]
    baseline_df  = float(baseline_row["acc_delta_f"].values[0]) \
                   if not baseline_row.empty and "acc_delta_f" in baseline_row.columns \
                   else float("nan")
    baseline_tr  = float(baseline_row["totalrank"].values[0]) \
                   if not baseline_row.empty else float("nan")

    n_total = 4

    def _sort_key(eid):
        parts = str(eid).replace("Y", "0").split(".")
        try:
            return [int(p) for p in parts]
        except ValueError:
            return [0]

    grouped_df_sorted = grouped_df.copy()
    grouped_df_sorted["_sort_key"] = grouped_df_sorted["experiment_id"].apply(_sort_key)
    grouped_df_sorted = grouped_df_sorted.sort_values("_sort_key").drop(
        columns="_sort_key"
    ).reset_index(drop=True)

    rows     = []
    selected = None

    for _, grp_row in grouped_df_sorted.iterrows():
        rg       = grp_row["experiment_id"]
        ns       = int(grp_row["success_count"]) \
                   if "success_count" in grp_row else n_total
        tr       = float(grp_row["totalrank"]) \
                   if not pd.isna(grp_row["totalrank"]) else float("nan")
        df_val   = float(grp_row["acc_delta_f"]) \
                   if "acc_delta_f" in grp_row and not pd.isna(grp_row["acc_delta_f"]) \
                   else float("nan")

        m_label = grp_row.get("mu", rg)

        if rg == baseline_rg or pd.isna(baseline_df) or pd.isna(df_val):
            improvement = float("nan")
        elif baseline_df == 0:
            improvement = float("nan")
        else:
            improvement = 100.0 * (baseline_df - df_val) / abs(baseline_df)

        if rg == baseline_rg or pd.isna(baseline_tr) or pd.isna(tr):
            tr_cost = float("nan")
        else:
            tr_cost = 100.0 * (tr - baseline_tr) / abs(baseline_tr)

        passes = (ns == n_total) and \
                 (not pd.isna(improvement)) and \
                 (improvement >= delta_f_min_improvement)

        if passes and selected is None and rg != baseline_rg:
            selected = rg

        ns_fmt   = str(ns)
        tr_fmt   = _fmt(tr, 3)     if not pd.isna(tr)      else "--"
        df_fmt   = _fmt(df_val, 3) if not pd.isna(df_val)  else "--"
        imp_fmt  = (f"{improvement:.1f}\\%" if not pd.isna(improvement) else "--")
        cost_fmt = (f"+{tr_cost:.1f}\\%" if (not pd.isna(tr_cost) and tr_cost >= 0)
                    else (f"{tr_cost:.1f}\\%" if not pd.isna(tr_cost) else "--"))
        sel_fmt  = r"\textbf{yes}" if rg == selected else \
                   ("--" if rg == baseline_rg else "no")

        if rg == selected:
            ns_fmt   = _bold(ns_fmt)
            tr_fmt   = _bold(tr_fmt)
            df_fmt   = _bold(df_fmt)
            imp_fmt  = _bold(imp_fmt)
            cost_fmt = _bold(cost_fmt)

        if ns < n_total and rg != baseline_rg:
            ns_fmt  = _italic(ns_fmt)
            tr_fmt  = _italic(tr_fmt)
            df_fmt  = _italic(df_fmt)

        rows.append(
            f"    {m_label} & {ns_fmt} & {tr_fmt} & "
            f"{df_fmt} & {imp_fmt} & {cost_fmt} & {sel_fmt} \\\\"
        )

    if selected is None:
        rows.append(
            r"    \multicolumn{7}{l}{"
            r"\textit{No $\mu > 0$ achieved valid results across all "
            r"sub-experiments with sufficient $\Delta f$ improvement.}} \\"
        )

    spec = "@{}lcrrrrl@{}"
    raw_headers = [
        r"$\mu$", r"$n_s/4$", r"$\text{total}_{\text{rank}}$",
        r"Acc. $\Delta f$", r"$\Delta f$ impr. (\%)",
        r"$\text{total}_{\text{rank}}$ cost (\%)", "Selected"
    ]
    header_row = " & ".join(_bold(h) for h in raw_headers) + r" \\"
    body = "\n".join(rows)

    return (
        r"\begin{table}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"{body}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        r"\end{table}"
    )


# ── Full summary table (params + results + all ranks, no grouping) ───────────

def full_summary_table(
    summary_df, ranked_df,
    experiments_cfg, group_params_columns,
    params_columns, metrics,
    caption, label,
    two_col=False,
):
    """
    Flat table combining params, result cols, individual rank cols, and totalrank.
    No group_id grouping or separators.

    Columns: ID | PARAMS_COLUMNS | METRICS result cols | rank cols | totalrank

    Formatting (all global, excluding invalid rows):
    - Italic: rows where is_valid == False
    - Bold: global winner of each result col, each rank col, and totalrank
    - Underline on all PARAMS_COLUMNS cells of the row where totalrank is bold
    """
    active    = _active_metrics(metrics)
    has_valid = "is_valid" in summary_df.columns
    grp_param_keys = [k for k, _ in group_params_columns]

    # ── Build per-experiment lookup from experiments_cfg ─────────────────────
    exp_lookup = {cfg.get("id", ekey): cfg for ekey, cfg in experiments_cfg.items()}

    # ── Merge summary_df with ranked_df ──────────────────────────────────────
    df = summary_df.copy()

    # Attach rank cols and totalrank from ranked_df if not already present
    rank_cols_needed = (
        [_METRIC_REGISTRY[m][3] for m in active if _METRIC_REGISTRY[m][3] is not None]
        + ["totalrank"]
    )
    if ranked_df is not None:
        rk = ranked_df.set_index("experiment_id")
        for col in rank_cols_needed:
            if col not in df.columns and col in rk.columns:
                df[col] = df["experiment_id"].map(rk[col])

    # Attach params from experiments_cfg (always overwrite to use config values,
    # not raw log values that may differ e.g. "Evolution Strategy" vs "ES")
    for pk in grp_param_keys:
        df[pk] = df["experiment_id"].apply(
            lambda eid, k=pk: exp_lookup.get(eid, {}).get(k, "")
        )

    # ── Sort by experiment_id ─────────────────────────────────────────────────
    df = _sort_by_id(df)

    # ── Identify global winners (excluding invalid rows) ──────────────────────
    valid_df  = df[df["is_valid"] == True] if has_valid else df
    winner_idx = {}  # col → df index of winner

    for mkey in active:
        res_col, _, hib, rank_col, _, rank_hib, _ = _METRIC_REGISTRY[mkey]
        if res_col in df.columns and not valid_df.empty:
            s = valid_df[res_col].astype(float)
            winner_idx[res_col] = s.idxmax() if hib else s.idxmin()
        if rank_col and rank_col in df.columns and not valid_df.empty:
            s = valid_df[rank_col].astype(float)
            winner_idx[rank_col] = s.idxmax() if rank_hib else s.idxmin()

    if "totalrank" in df.columns and not valid_df.empty:
        s = valid_df["totalrank"].astype(float)
        winner_idx["totalrank"] = s.idxmin()

    totalrank_winner_idx = winner_idx.get("totalrank")

    # ── Column order ──────────────────────────────────────────────────────────
    res_cols  = [_METRIC_REGISTRY[m][0] for m in active if _METRIC_REGISTRY[m][0] in df.columns]
    rank_cols = [_METRIC_REGISTRY[m][3] for m in active
                 if _METRIC_REGISTRY[m][3] is not None and _METRIC_REGISTRY[m][3] in df.columns]
    all_cols  = ["experiment_id"] + grp_param_keys + res_cols + rank_cols + ["totalrank"]
    all_cols  = [c for c in all_cols if c in df.columns or c == "experiment_id"]

    col_headers = {
        "experiment_id": "ID",
        "totalrank":     _TOTALRANK_HDR[0],
        **{k: h for k, h in group_params_columns},
        **{_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][1] for m in active},
        **{_METRIC_REGISTRY[m][3]: _METRIC_REGISTRY[m][4]
           for m in active if _METRIC_REGISTRY[m][3] is not None},
    }
    col_align_map = {
        "experiment_id": "l",
        "totalrank":     "r",
        **{k: "l" for k in grp_param_keys},
        **{_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][6] for m in active},
        **{_METRIC_REGISTRY[m][3]: _METRIC_REGISTRY[m][6]
           for m in active if _METRIC_REGISTRY[m][3] is not None},
    }

    spec       = "@{}" + "".join(col_align_map.get(c, "r") for c in all_cols) + "@{}"
    header_row = " & ".join(_bold(col_headers.get(c, c)) for c in all_cols) + r" \\"
    table_env  = "table*" if two_col else "table"

    # ── Build rows ────────────────────────────────────────────────────────────
    rows = []
    for idx, row in df.iterrows():
        invalid  = has_valid and (row.get("is_valid") == False)
        is_tr_winner = (idx == totalrank_winner_idx)

        cells = []
        for c in all_cols:
            if c == "experiment_id":
                cells.append(str(row.get("experiment_id", "")))
                continue

            # PARAMS_COLUMNS: underline if this row wins totalrank
            if c in grp_param_keys:
                val = str(row.get(c, ""))
                if is_tr_winner:
                    val = r"\underline{" + val + "}"
                cells.append(val)
                continue

            # Result cols
            if c in res_cols:
                mkey   = next(m for m in active if _METRIC_REGISTRY[m][0] == c)
                _, _, hib, _, _, _, _ = _METRIC_REGISTRY[mkey]
                dec    = 3 if c in HIGH_PRECISION_COLS else 2
                val    = row.get(c)
                fmt    = _fmt(val, dec)
                if invalid:
                    fmt = _italic(fmt)
                elif winner_idx.get(c) == idx:
                    fmt = _bold(fmt)
                cells.append(fmt)
                continue

            # Rank cols and totalrank
            val = row.get(c)
            fmt = _fmt(val, 2)
            if invalid:
                fmt = _italic(fmt)
            elif winner_idx.get(c) == idx:
                fmt = _bold(fmt)
            cells.append(fmt)

        rows.append(" & ".join(cells) + r" \\")

    body = "\n    ".join(rows)

    return (
        rf"\begin{{{table_env}}}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        rf"\end{{{table_env}}}"
    )


# ── Comparison ranked table (section_type == "comparison") ───────────────────

def comparison_ranked_table(
    summary_df, ranked_df, grouped_df,
    experiments_cfg, groups_cfg,
    params_columns, metrics,
    caption, label,
):
    """
    Combined ranked + grouped table for direct comparison between two
    objective functions (Baseline vs Proposed).

    Upper block columns: ID | PARAMS_COLUMNS | METRICS (result cols) | totalrank
    Rows are sorted by group_id then by rank_group within each group.
    - Italic: rows that did not pass the pct_threshold (is_valid == False)
    - Bold per group_id: winner of each metric col and totalrank
      (excluding invalid rows)

    Below a double \\hline, a second summary block reports n_s/N and
    group_rank per rank_group (e.g. Baseline vs Proposed), using the same
    winner-detection logic as grouped_ranked_table. The summary block's
    label column auto-computes a fixed width (via \\multicolumn{...}{p{Xcm}})
    so its descriptive text wraps onto multiple lines instead of widening
    the table beyond what the upper block already determines.
    """
    active  = _active_metrics(metrics)
    has_valid = "is_valid" in summary_df.columns

    # ── Determine n_total from number of group_ids per rank_group ────────────
    # Each rank_group spans all group_ids → n_total = count of unique group_ids
    if "group_id" in summary_df.columns:
        n_total = summary_df["group_id"].nunique()
    else:
        n_total = 4

    # ── Build per-experiment lookup from experiments_cfg ─────────────────────
    # key: experiment key → cfg dict (with "id", "group_id", "rank_group", params...)
    exp_lookup = {}
    for ekey, cfg in experiments_cfg.items():
        exp_id = cfg.get("id", ekey)
        exp_lookup[exp_id] = cfg

    # ── Merge summary_df with experiments_cfg to get params cols ─────────────
    param_keys = [k for k, _ in params_columns]

    df = summary_df.copy()

    # Always overwrite param cols from experiments_cfg (not raw log values)
    def _get_param(exp_id, key):
        return exp_lookup.get(exp_id, {}).get(key, "")

    for pk in param_keys:
        df[pk] = df["experiment_id"].apply(lambda eid, k=pk: _get_param(eid, k))

    # Attach rank_group and group_id from cfg if not already present
    if "rank_group" not in df.columns:
        df["rank_group"] = df["experiment_id"].apply(
            lambda eid: exp_lookup.get(eid, {}).get("rank_group", "")
        )
    if "group_id" not in df.columns:
        df["group_id"] = df["experiment_id"].apply(
            lambda eid: exp_lookup.get(eid, {}).get("group_id", "")
        )

    # Attach totalrank from ranked_df
    if "totalrank" not in df.columns and ranked_df is not None and "totalrank" in ranked_df.columns:
        tr_lookup = ranked_df.set_index("experiment_id")["totalrank"].to_dict()
        df["totalrank"] = df["experiment_id"].map(tr_lookup)

    # ── Sort: by group_id then rank_group ────────────────────────────────────
    def _sort_key(row):
        gid  = str(row.get("group_id", ""))
        rg   = str(row.get("rank_group", ""))
        return _parse_id(gid) + _parse_id(rg)

    df["_sort_key"] = df.apply(_sort_key, axis=1)
    df = df.sort_values("_sort_key").drop(columns="_sort_key").reset_index(drop=True)

    # ── Determine grouped winner (for the summary block bold+underline) ──────
    grouped_winner_id  = None
    grouped_winning_by = ""
    if grouped_df is not None and not grouped_df.empty and "success_count" in grouped_df.columns:
        sorted_w = grouped_df.sort_values(
            ["success_count", "totalrank"], ascending=[False, True]
        )
        grouped_winner_id  = sorted_w.iloc[0]["experiment_id"]
        grouped_winning_by = sorted_w.iloc[0].get("winning_criterion", "")
        if not grouped_winning_by and len(sorted_w) > 1:
            grouped_winning_by = (
                "success_count"
                if sorted_w.iloc[0]["success_count"] > sorted_w.iloc[1]["success_count"]
                else "totalrank"
            )

    # ── Per-group_id winners for metric cols and totalrank ───────────────────
    # winner_map[group_id][col] = index of winning row
    winner_map = {}
    for gid, grp in df.groupby("group_id"):
        valid_grp = grp[grp["is_valid"] == True] if has_valid else grp
        winner_map[gid] = {}

        for mkey in active:
            res_col, _, hib, _, _, _, _ = _METRIC_REGISTRY[mkey]
            if res_col not in df.columns:
                continue
            if valid_grp.empty:
                continue
            series = valid_grp[res_col].astype(float)
            best_idx = series.idxmax() if hib else series.idxmin()
            winner_map[gid][res_col] = best_idx

        if "totalrank" in df.columns and not valid_grp.empty:
            series = valid_grp["totalrank"].astype(float)
            winner_map[gid]["totalrank"] = series.idxmin()

    # ── Column spec (upper block) ─────────────────────────────────────────────
    # ID | param cols | metric result cols | totalrank
    metric_res_cols = [_METRIC_REGISTRY[m][0] for m in active]
    metric_headers  = {_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][1] for m in active}

    all_col_keys = (
        ["experiment_id"]
        + param_keys
        + metric_res_cols
        + ["totalrank"]
    )
    col_headers = {
        "experiment_id": "ID",
        "totalrank":     _TOTALRANK_HDR[0],
        **{k: h for k, h in params_columns},
        **metric_headers,
    }
    col_align_map = {
        "experiment_id": "l",
        "totalrank":     "r",
        **{k: "l" for k in param_keys},
        **{_METRIC_REGISTRY[m][0]: _METRIC_REGISTRY[m][6] for m in active},
    }
    n_cols = len(all_col_keys)

    spec       = "@{}" + "".join(col_align_map[c] for c in all_col_keys) + "@{}"
    header_row = " & ".join(_bold(col_headers[c]) for c in all_col_keys) + r" \\"

    # ── Build rows (upper block) ──────────────────────────────────────────────
    rows        = []
    prev_gid    = None

    for idx, row in df.iterrows():
        gid     = row.get("group_id", "")
        invalid = has_valid and (row.get("is_valid") == False)

        # separator between group_id blocks (scene+method pairs)
        if prev_gid is not None and gid != prev_gid:
            rows.append(r"\noalign{\smallskip}")
        prev_gid = gid

        cells = []

        # ID
        cells.append(str(row.get("experiment_id", "")))

        # PARAMS_COLUMNS
        for pk in param_keys:
            cells.append(str(row.get(pk, "")))

        # METRIC result cols
        for mkey in active:
            res_col, _, _, _, _, _, _ = _METRIC_REGISTRY[mkey]
            if res_col not in df.columns:
                cells.append("--")
                continue
            val = row.get(res_col)
            dec = 3 if res_col in HIGH_PRECISION_COLS else 2
            fmt_val = _fmt(val, dec)

            if invalid:
                fmt_val = _italic(fmt_val)
            elif winner_map.get(gid, {}).get(res_col) == idx:
                fmt_val = _bold(fmt_val)

            cells.append(fmt_val)

        # totalrank
        tr_val = row.get("totalrank")
        tr_fmt = _fmt(tr_val, 3)
        if invalid:
            tr_fmt = _italic(tr_fmt)
        elif winner_map.get(gid, {}).get("totalrank") == idx:
            tr_fmt = _bold(tr_fmt)
        cells.append(tr_fmt)

        rows.append(" & ".join(cells) + r" \\")

    body = "\n    ".join(rows)

    # ── Summary block (rank_group level: n_s/N and group_rank) ────────────────
    # Estimate a fixed width (in cm) for the merged label column of the summary
    # block, based on the number of columns it spans in the upper block, so the
    # descriptive label wraps onto several lines instead of widening the table
    # beyond what the upper block determines.
    n_label_cols   = max(1, n_cols - 2) 

    summary_rows = []
    ltx_align = r"@{}l"
    if grouped_df is not None and not grouped_df.empty:
        grp_sorted = _sort_by_id(grouped_df)
        for _, grow in grp_sorted.iterrows():
            rg   = grow["experiment_id"]
            role = next(
                (ecfg.get("Role", rg) for ecfg in exp_lookup.values()
                 if ecfg.get("rank_group") == rg),
                rg,
            )
            ns        = int(grow["success_count"]) if "success_count" in grow else n_total
            tr        = grow["totalrank"] if "totalrank" in grow.index else float("nan")
            ns_fmt    = str(ns)
            tr_fmt    = _fmt(tr, 3) if not pd.isna(tr) else "--"
            is_winner = (rg == grouped_winner_id)

            if is_winner:
                role_fmt = _bold(str(role))
                if grouped_winning_by == "success_count":
                    ns_fmt = _bold(r"\underline{" + ns_fmt + "}")
                    tr_fmt = _bold(tr_fmt)
                else:
                    ns_fmt = _bold(ns_fmt)
                    tr_fmt = _bold(r"\underline{" + tr_fmt + "}") if tr_fmt != "--" else _bold(tr_fmt)
            else:
                role_fmt = str(role)



            summary_rows.append(
                rf"    \multicolumn{{{n_label_cols}}}{{{ltx_align}}}{{{role_fmt}}} & {ns_fmt} \\"
                if False else
                rf"    \multicolumn{{{n_label_cols}}}{{{ltx_align}}}{{{role_fmt}}} & {ns_fmt} & {tr_fmt} \\"
            )

    summary_header = (
        rf"    \multicolumn{{{n_label_cols}}}{{{ltx_align}}}{{\textbf{{Aggregated Performance}}}} & "
        rf"$\bm{{n_s/{{{n_total}}}}}$ & "
        r"$\textbf{group}_{\textbf{rank}}$ \\"
    )

    summary_block = ""
    if summary_rows:
        summary_block = (
            "\n\\hline\n"
            "\\noalign{\\smallskip}\n"
            f"{summary_header}\n"
            r"\hline" "\n"
            + "\n".join(summary_rows)
        )

    return (
        r"\begin{table}[!t]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        f"{summary_block}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        r"\end{table}"
    )


# ── Save all tables ───────────────────────────────────────────────────────────

def save_tables(
    ranked_df, output_dir, prefix, caption_prefix,
    full_summary=None, grouped_df=None,
    experiments_cfg=None, groups_cfg=None,
    group_params_columns=None, params_columns=None,
    params_note=None, include_method=True,
    metrics=None,
    robust_comparison_cfg=None,
    section_type="standard",
):
    if metrics is None:
        metrics = list(_METRIC_REGISTRY.keys())

    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    if section_type == "standard":

        if experiments_cfg is not None and params_columns is not None:
            p = params_table(experiments_cfg, params_columns,
                             caption=f"{caption_prefix} experimental mapping and ID definitions.",
                             label=f"tab:{prefix}_params", note=params_note)
            (tables_dir / f"{prefix}_params.tex").write_text(p, encoding="utf-8")

        base_df = full_summary if full_summary is not None else ranked_df
        if "is_valid" not in base_df.columns and "is_valid" in ranked_df.columns:
            valid_col = ranked_df[["experiment_id", "is_valid"]].drop_duplicates()
            base_df   = base_df.merge(valid_col, on="experiment_id", how="left")
            base_df["is_valid"] = base_df["is_valid"].fillna(True)

        res = results_table(_sort_by_id(base_df),
                            caption=f"{caption_prefix} results. Bold indicates the winner per metric and italics rows denote configurations excluded due to $\\text{{Retr.}} < 85\\%$.",
                            label=f"tab:{prefix}_results",
                            include_method=include_method, metrics=metrics)
        (tables_dir / f"{prefix}_results.tex").write_text(res, encoding="utf-8")

        valid_ranked = (ranked_df[ranked_df["is_valid"] == True].copy()
                        if "is_valid" in ranked_df.columns else ranked_df.copy())
        rnk = ranked_table(_sort_by_id(valid_ranked),
                           caption=f"{caption_prefix} ranked results. Only non-excluded configurations are displayed; bold indicates the winner per rank.",
                           label=f"tab:{prefix}_ranked",
                           include_method=include_method, metrics=metrics)
        (tables_dir / f"{prefix}_ranked.tex").write_text(rnk, encoding="utf-8")


        if experiments_cfg is not None and params_columns is not None:
            fst = full_summary_table(
                summary_df      = base_df,
                ranked_df       = ranked_df,
                experiments_cfg = experiments_cfg,
                group_params_columns = group_params_columns,
                params_columns  = params_columns,
                metrics         = metrics,
                caption         = f"{caption_prefix} full summary: parameters, results, and ranks.",
                label           = f"tab:{prefix}_full_summary",
                two_col        = True,
            )
            (tables_dir / f"{prefix}_full_summary.tex").write_text(fst, encoding="utf-8")

        if grouped_df is not None and groups_cfg is not None and group_params_columns is not None:
            grp = grouped_ranked_table(groups_cfg, grouped_df, group_params_columns,
                                       caption=f"{caption_prefix} grouped ranked results. Bold indicates the winning configuration; underlines denote the specific metric ($n_s/4$ or $\\text{{group}}_{{\\text{{rank}}}}$) that determined the selection.",
                                       label=f"tab:{prefix}_grouped_ranked")
            (tables_dir / f"{prefix}_grouped_ranked.tex").write_text(grp, encoding="utf-8")

        # ── Robust comparison table ───────────────────────────────────────────
        if robust_comparison_cfg is not None and grouped_df is not None:
            rc = robust_comparison_table(
                ranked_df               = ranked_df,
                grouped_df              = grouped_df,
                experiments_cfg         = experiments_cfg or {},
                baseline_rg             = robust_comparison_cfg["baseline_rg"],
                delta_f_min_improvement = robust_comparison_cfg["delta_f_min_improvement"],
                caption                 = f"{caption_prefix} experiments mu selection summary.",
                label                   = f"tab:{prefix}_mu_selection",
            )
            (tables_dir / f"{prefix}_mu_selection.tex").write_text(rc, encoding="utf-8")

        print(f"  Tables -> {tables_dir}/{prefix}_{{params,results,ranked,grouped_ranked}}.tex")

    elif section_type == "comparison":
        if experiments_cfg is None or params_columns is None:
            raise ValueError("comparison section_type requires experiments_cfg and params_columns")

        base_df = full_summary if full_summary is not None else ranked_df
        if "is_valid" not in base_df.columns and "is_valid" in ranked_df.columns:
            valid_col = ranked_df[["experiment_id", "is_valid"]].drop_duplicates()
            base_df   = base_df.merge(valid_col, on="experiment_id", how="left")
            base_df["is_valid"] = base_df["is_valid"].fillna(True)

        cmp = comparison_ranked_table(
            summary_df      = base_df,
            ranked_df       = ranked_df,
            grouped_df      = grouped_df,
            experiments_cfg = experiments_cfg,
            groups_cfg      = groups_cfg or {},
            params_columns  = params_columns,
            metrics         = metrics,
            caption         = f"{caption_prefix} of baseline and proposed objective functions. The upper block details results from each scene-method combination (bold indicates the winner per metric and rank). Lower block presents the aggregated results (bold indicates the winning configuration; underline denotes the specific criterion that determined the selection).",
            label           = f"tab:{prefix}_comparison",
        )
        (tables_dir / f"{prefix}_comparison.tex").write_text(cmp, encoding="utf-8")
        print(f"  Tables -> {tables_dir}/{prefix}_comparison.tex")

    else:
        raise ValueError(f"Unknown section_type: {section_type!r}")