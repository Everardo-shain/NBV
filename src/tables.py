from pathlib import Path
from sys import prefix
from wsgiref import headers
import pandas as pd


# ── Full column registry ──────────────────────────────────────────────────────
# metric_key → (results_col, results_header, results_hib,
#               rank_col,    rank_header,    rank_hib,    alignment)
_METRIC_REGISTRY = {
    "distance":  ("acc_dist_m",    r"\thead{Acc.\\ dist. (m)}", False,
                  "drank",         r"$d_{\text{rank}}$",        False, "r"),
    "energy":    ("acc_energy",    r"\thead{Acc.\\ energy}",    False,
                  "erank",         r"$e_{\text{rank}}$",        False, "r"),
    "retrieved": ("pct_retrieved", r"\thead{Retr.\\ (m)}",           True,
                  "retrrank",      r"$r_{\text{rank}}$",     False, "r"),
    "quality":   ("mean_quality",  r"\thead{Mean\\ quality}",   True,
                  "qrank",         r"$q_{\text{rank}}$",        False, "r"),
    "time":      ("total_time_s",  r"\thead{Time\\ (s)}",       False,
                  "timerank",      r"$t_{\text{rank}}$",     False, "r"),
    "delta_f":   ("acc_delta_f",   r"\thead{Acc.\\ $\Delta f$}",False,
                  None,            None,                        False, "r"),
}

# "totalrank" is always the last rank column
_TOTALRANK_HDR = (r"$total_{\text{rank}}$", False, "r")

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
def _bold(s):    return r"\textbf{" + s + "}"


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
        rf"\begin{{{table_env}}}[ht]" "\n"
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
        r"\begin{table}[ht]" "\n"
        r"\centering" "\n"
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
        "totalrank":     r"$group_{\text{rank}}$",
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
        r"\begin{table}[ht]" "\n"
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


# ── Robust comparison grouped table ──────────────────────────────────────────

def robust_comparison_table(
    ranked_df, grouped_df, experiments_cfg,
    baseline_rg, delta_f_min_improvement,
    caption, label,
):
    """
    Side-by-side comparison table for all lambda values.
    Columns: lambda | n_s/4 | totalrank | acc_delta_f | delta_f improvement % | Selected
    """
    # Get baseline delta_f from grouped_df
    baseline_row = grouped_df[grouped_df["experiment_id"] == baseline_rg]
    baseline_df  = float(baseline_row["acc_delta_f"].values[0]) \
                   if not baseline_row.empty and "acc_delta_f" in baseline_row.columns \
                   else float("nan")
    baseline_tr  = float(baseline_row["totalrank"].values[0]) \
                   if not baseline_row.empty else float("nan")

    n_total = 4

    rows     = []
    selected = None

    for _, grp_row in grouped_df.iterrows():
        rg       = grp_row["experiment_id"]
        ns       = int(grp_row["success_count"]) \
                   if "success_count" in grp_row else n_total
        tr       = float(grp_row["totalrank"]) \
                   if not pd.isna(grp_row["totalrank"]) else float("nan")
        df_val   = float(grp_row["acc_delta_f"]) \
                   if "acc_delta_f" in grp_row and not pd.isna(grp_row["acc_delta_f"]) \
                   else float("nan")

        # lambda label from GROUPS
        lam_label = grp_row.get("lambda", rg)

        # compute delta_f improvement vs baseline
        if rg == baseline_rg or pd.isna(baseline_df) or pd.isna(df_val):
            improvement = float("nan")
        elif baseline_df == 0:
            improvement = float("nan")
        else:
            improvement = 100.0 * (baseline_df - df_val) / abs(baseline_df)

        # totalrank cost vs baseline
        if rg == baseline_rg or pd.isna(baseline_tr) or pd.isna(tr):
            tr_cost = float("nan")
        else:
            tr_cost = 100.0 * (tr - baseline_tr) / abs(baseline_tr)

        # selection: minimum lambda with n_s=4 AND improvement >= threshold
        passes = (ns == n_total) and \
                 (not pd.isna(improvement)) and \
                 (improvement >= delta_f_min_improvement)

        if passes and selected is None and rg != baseline_rg:
            selected = rg

        # format cells
        ns_fmt   = str(ns)
        tr_fmt   = _fmt(tr, 3)   if not pd.isna(tr)          else "--"
        df_fmt   = _fmt(df_val, 3) if not pd.isna(df_val)    else "--"
        imp_fmt  = (f"{improvement:.1f}\\%" if not pd.isna(improvement) else "--")
        cost_fmt = (f"+{tr_cost:.1f}\\%" if (not pd.isna(tr_cost) and tr_cost >= 0)
                    else (f"{tr_cost:.1f}\\%" if not pd.isna(tr_cost) else "--"))
        sel_fmt  = r"\textbf{yes}" if rg == selected else \
                   ("--" if rg == baseline_rg else "no")

        # bold entire row if selected
        if rg == selected:
            ns_fmt   = _bold(ns_fmt)
            tr_fmt   = _bold(tr_fmt)
            df_fmt   = _bold(df_fmt)
            imp_fmt  = _bold(imp_fmt)
            cost_fmt = _bold(cost_fmt)

        # italic if n_s < 4 and not baseline
        if ns < n_total and rg != baseline_rg:
            ns_fmt  = _italic(ns_fmt)
            tr_fmt  = _italic(tr_fmt)
            df_fmt  = _italic(df_fmt)

        rows.append(
            f"    {lam_label} & {ns_fmt} & {tr_fmt} & "
            f"{df_fmt} & {imp_fmt} & {cost_fmt} & {sel_fmt} \\\\"
        )

    if selected is None:
        rows.append(
            r"    \multicolumn{7}{l}{"
            r"\textit{No $\lambda > 0$ achieved valid results across all "
            r"sub-experiments with sufficient $\Delta f$ improvement.}} \\"
        )

    spec = "@{}lcrrrrl@{}"
    raw_headers = [
        r"$\lambda$", r"$n_s/4$", r"$total_{\text{rank}}$", 
        r"Acc. $\Delta f$", r"$\Delta f$ impr. (\%)", 
        r"$total_{\text{rank}}$ cost (\%)", "Selected"
    ]
    header_row = " & ".join(_bold(h) for h in raw_headers) + r" \\"
    body = "\n".join(rows)

    return (
        r"\begin{table}[ht]" "\n"
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

# ── Save all tables ───────────────────────────────────────────────────────────

def save_tables(
    ranked_df, output_dir, prefix, caption_prefix,
    full_summary=None, grouped_df=None,
    experiments_cfg=None, groups_cfg=None,
    group_params_columns=None, params_columns=None,
    params_note=None, include_method=True,
    metrics=None,
    robust_comparison_cfg=None, 
):
    if metrics is None:
        metrics = list(_METRIC_REGISTRY.keys())

    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    if experiments_cfg is not None and params_columns is not None:
        p = params_table(experiments_cfg, params_columns,
                         caption=f"{caption_prefix} Experiment Variable Parameters.",
                         label=f"tab:{prefix}_params", note=params_note)
        (tables_dir / f"{prefix}_params.tex").write_text(p, encoding="utf-8")

    base_df = full_summary if full_summary is not None else ranked_df
    if "is_valid" not in base_df.columns and "is_valid" in ranked_df.columns:
        valid_col = ranked_df[["experiment_id", "is_valid"]].drop_duplicates()
        base_df   = base_df.merge(valid_col, on="experiment_id", how="left")
        base_df["is_valid"] = base_df["is_valid"].fillna(True)

    res = results_table(_sort_by_id(base_df),
                        caption=f"{caption_prefix} Experiment Results.",
                        label=f"tab:{prefix}_results",
                        include_method=include_method, metrics=metrics)
    (tables_dir / f"{prefix}_results.tex").write_text(res, encoding="utf-8")

    valid_ranked = (ranked_df[ranked_df["is_valid"] == True].copy()
                    if "is_valid" in ranked_df.columns else ranked_df.copy())
    rnk = ranked_table(_sort_by_id(valid_ranked),
                       caption=f"{caption_prefix} Experiment Ranked Results.",
                       label=f"tab:{prefix}_ranked",
                       include_method=include_method, metrics=metrics)
    (tables_dir / f"{prefix}_ranked.tex").write_text(rnk, encoding="utf-8")

    if grouped_df is not None and groups_cfg is not None and group_params_columns is not None:
        grp = grouped_ranked_table(groups_cfg, grouped_df, group_params_columns,
                                   caption=f"{caption_prefix} Grouped Ranked Results.",
                                   label=f"tab:{prefix}_grouped_ranked")
        (tables_dir / f"{prefix}_grouped_ranked.tex").write_text(grp, encoding="utf-8")

       
    # ── Robust comparison table (robust_comparison section only) ─────────────
    if robust_comparison_cfg is not None and grouped_df is not None:
        rc = robust_comparison_table(
            ranked_df            = ranked_df,
            grouped_df           = grouped_df,
            experiments_cfg      = experiments_cfg or {},
            baseline_rg          = robust_comparison_cfg["baseline_rg"],
            delta_f_min_improvement = robust_comparison_cfg["delta_f_min_improvement"],
            caption              = f"{caption_prefix} Lambda Selection Summary.",
            label                = f"tab:{prefix}_lambda_selection",
        )
        (tables_dir / f"{prefix}_lambda_selection.tex").write_text(
            rc, encoding="utf-8"
        )

    print(f"  Tables -> {tables_dir}/{prefix}_{{params,results,ranked,grouped_ranked}}.tex")