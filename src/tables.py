from pathlib import Path
import pandas as pd


# ── Full column registry ──────────────────────────────────────────────────────
# metric_key → (results_col, results_header, results_hib,
#               rank_col,    rank_header,    rank_hib,    alignment)
_METRIC_REGISTRY = {
    "distance":  ("acc_dist_m",    r"\thead{Acc.\\ dist. (m)}", False,
                  "drank",         r"$d_{\text{rank}}$",        False, "r"),
    "energy":    ("acc_energy",    r"\thead{Acc.\\ energy}",    False,
                  "erank",         r"$e_{\text{rank}}$",        False, "r"),
    "retrieved": ("pct_retrieved", r"\thead{\%ret.}",           True,
                  "retrrank",      r"$retr_{\text{rank}}$",     False, "r"),
    "quality":   ("mean_quality",  r"\thead{Mean\\ quality}",   True,
                  "qrank",         r"$q_{\text{rank}}$",        False, "r"),
    "time":      ("total_time_s",  r"\thead{Time\\ (s)}",       False,
                  "timerank",      r"$time_{\text{rank}}$",     False, "r"),
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
    header_row = " & ".join(hdr_map.get(c, c) for c in display) + r" \\"
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
    header_row  = " & ".join(col_headers[k] for k in col_keys) + r" \\"

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
        "totalrank":     r"$\overline{total_{\text{rank}}}$",
        **{k: h for k, h in group_params_columns},
    }
    param_aligns = (["l"] * (1 + len(group_params_columns)) + ["c", "r"])
    spec         = "@{}" + "".join(param_aligns) + "@{}"
    header_row   = " & ".join(param_col_hdrs[k] for k in param_col_keys) + r" \\"

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

# ── K stability table ─────────────────────────────────────────────────────────

def k_stability_table(grouped_df, k_values_order, threshold,
                      caption, label):
    """
    Generates a LaTeX table showing the percentage change in totalrank
    between consecutive k values. Used only in the k_sensitivity section.

    grouped_df must have columns: experiment_id (matching rank_group keys),
    totalrank.
    """
    rows = []
    for i in range(len(k_values_order) - 1):
        k_curr = k_values_order[i]
        k_next = k_values_order[i + 1]

        # match by k value in grouped_df via experiment_id
        # grouped_df experiment_id values are like "6.Y.01", "6.Y.02"...
        # position in k_values_order corresponds to position in GROUPS
        idx_curr = i
        idx_next = i + 1

        if idx_curr >= len(grouped_df) or idx_next >= len(grouped_df):
            continue

        tr_curr = grouped_df.iloc[idx_curr]["totalrank"]
        tr_next = grouped_df.iloc[idx_next]["totalrank"]

        if pd.isna(tr_curr) or pd.isna(tr_next) or tr_curr == 0:
            pct_change = float("nan")
            stable     = "--"
        else:
            pct_change = 100.0 * abs(tr_next - tr_curr) / tr_curr
            stable     = r"\textbf{yes}" if pct_change < threshold else "no"

        transition = f"$k={k_curr} \\rightarrow k={k_next}$"
        tr_curr_fmt = _fmt(tr_curr, 3) if not pd.isna(tr_curr) else "--"
        tr_next_fmt = _fmt(tr_next, 3) if not pd.isna(tr_next) else "--"
        pct_fmt     = _fmt(pct_change, 2) if not pd.isna(pct_change) else "--"

        rows.append(
            f"    {transition} & {tr_curr_fmt} & {tr_next_fmt} & {pct_fmt} & {stable} \\\\"
        )

    spec       = "@{}lrrrr@{}"
    header_row = (r"Transition & "
                  r"$total_{\text{rank}}(k)$ & "
                  r"$total_{\text{rank}}(k{+}1)$ & "
                  r"$\Delta$ totalrank (\%) & "
                  r"Stable ($<$" + f"{threshold:.0f}" + r"\%)" + r" \\")
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
    k_stability_cfg=None,
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

    # ── K stability table (k_sensitivity section only) ────────────────────────
    if k_stability_cfg is not None and grouped_df is not None:
        k_stab = k_stability_table(
            grouped_df          = grouped_df,
            k_values_order      = k_stability_cfg["k_values_order"],
            threshold           = k_stability_cfg["threshold"],
            caption             = f"{caption_prefix} Totalrank Stability Between Consecutive $k$ Values.",
            label               = f"tab:{prefix}_k_stability",
        )
        (tables_dir / f"{prefix}_k_stability.tex").write_text(k_stab, encoding="utf-8")
    
    print(f"  Tables -> {tables_dir}/{prefix}_{{params,results,ranked,grouped_ranked}}.tex")