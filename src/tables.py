"""
src/tables.py
-------------
LaTeX table generation matching the thesis style.

Tables per section:
  1. _params.tex         — variable parameters (grouped by group_id)
  2. _results.tex        — raw metrics (all shown; invalid in italic; best-of-valid per group bolded)
  3. _ranked.tex         — ranking scores (valid only; best per group_id bolded)
  4. _grouped_ranked.tex — params + n_s + mean totalrank; winner row fully bolded
"""

from pathlib import Path
import pandas as pd


# ── Column definitions ────────────────────────────────────────────────────────
# (display_label, higher_is_better, alignment)
# alignment: "l" = left, "c" = center, "r" = right
RESULTS_COLS = {
    "acc_dist_m":    (r"\thead{Acc.\\ dist. (m)}",  False, "r"),
    "acc_energy":    (r"\thead{Acc.\\ energy}",      False, "r"),
    "pct_retrieved": (r"\thead{\%ret.}",             True,  "r"),
    "mean_quality":  (r"\thead{Mean\\ quality}",     True,  "r"),
    "total_time_s":  (r"\thead{Time\\ (s)}",         False, "r"),
}

RANKED_COLS = {
    "drank":     (r"$d_{rank}$",      False, "r"),
    "erank":     (r"$e_{rank}$",      False, "r"),
    "retrrank":  (r"$retr_{rank}$",   False, "r"),
    "qrank":     (r"$q_{rank}$",      False, "r"),
    "timerank":  (r"$time_{rank}$",   False, "r"),
    "totalrank": (r"$total_{rank}$",  False, "r"),
}

HIGH_PRECISION_COLS = {"mean_quality", "tri_quality"}

# Default alignments for fixed columns
COL_ALIGN = {
    "experiment_id": "l",
    "method":        "l",
    "id":            "l",
    "environment":   "l",
    "success_count": "c",
    "totalrank":     "r",
}


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fmt(v, dec=2):
    if isinstance(v, int) or (isinstance(v, float) and v == int(v)):
        return str(int(v))
    return f"{float(v):.{dec}f}"


def _italic(s: str) -> str:
    return r"\textit{" + s + "}"


def _bold(s: str) -> str:
    return r"\textbf{" + s + "}"


def _parse_id(x: str) -> list:
    parts = str(x).split(".")
    result = []
    for p in parts:
        clean = p.lstrip("Gg")
        try:
            result.append(int(clean))
        except ValueError:
            result.append(p)
    return result


def _sort_by_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_sort_key"] = df["experiment_id"].apply(_parse_id)
    df = df.sort_values("_sort_key").drop(columns="_sort_key")
    return df.reset_index(drop=True)


def _col_spec(display: list, col_defs: dict) -> str:
    """
    Build column spec with @{} on both ends.
    First column always left-aligned (ID), rest from col_defs or COL_ALIGN.
    """
    aligns = []
    for i, c in enumerate(display):
        if c in COL_ALIGN:
            aligns.append(COL_ALIGN[c])
        elif c in col_defs:
            aligns.append(col_defs[c][2])
        else:
            aligns.append("l" if i == 0 else "r")
    return "@{}" + "".join(aligns) + "@{}"


# ── Core LaTeX builder ────────────────────────────────────────────────────────

def _to_latex(
    fmt_df: pd.DataFrame,
    cols: list,
    col_defs: dict,
    headers: dict,
    caption: str,
    label: str,
    include_method: bool,
    two_col: bool = False,
    group_col: str = None,
    group_separator: str = r"\noalign{\smallskip}",
) -> str:
    display = ["experiment_id"]
    if include_method and "method" in fmt_df.columns:
        display.append("method")
    display += [c for c in cols if c in fmt_df.columns]

    hdr_map = {"experiment_id": "ID", "method": "Method"}
    hdr_map.update({k: v[0] for k, v in headers.items()})

    spec       = _col_spec(display, col_defs)
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


# ── Results table formatting ──────────────────────────────────────────────────

def _format_results(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().astype(object)
    has_valid = "is_valid" in df.columns

    for col, (_, hib, _align) in RESULTS_COLS.items():
        if col not in df.columns:
            continue
        series = df[col].astype(float)
        dec    = 3 if col in HIGH_PRECISION_COLS else 2

        out[col] = series.map(lambda v, d=dec: _fmt(v, d))

        if has_valid:
            for idx in df[df["is_valid"] == False].index:
                out.at[idx, col] = _italic(out.at[idx, col])

        if "group_id" in df.columns:
            for _, grp in df.groupby("group_id"):
                valid_grp = grp[grp["is_valid"] == True] if has_valid else grp
                if valid_grp.empty:
                    continue
                grp_series = series[valid_grp.index]
                best_idx   = grp_series.idxmax() if hib else grp_series.idxmin()
                out.at[best_idx, col] = _bold(out.at[best_idx, col])
        else:
            valid_series = series[df["is_valid"] == True] if has_valid else series
            best_idx = valid_series.idxmax() if hib else valid_series.idxmin()
            out.at[best_idx, col] = _bold(out.at[best_idx, col])

    return out


# ── Ranked table formatting ───────────────────────────────────────────────────

def _format_ranked(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().astype(object)
    for col, (_, hib, _align) in RANKED_COLS.items():
        if col not in df.columns:
            continue
        series = df[col].astype(float)
        dec    = 3 if col in HIGH_PRECISION_COLS else 2
        out[col] = series.map(lambda v, d=dec: _fmt(v, d))

        if "group_id" in df.columns:
            for _, grp in df.groupby("group_id"):
                grp_series = series[grp.index]
                best_idx   = grp_series.idxmax() if hib else grp_series.idxmin()
                out.at[best_idx, col] = _bold(out.at[best_idx, col])
        else:
            best_idx = series.idxmax() if hib else series.idxmin()
            out.at[best_idx, col] = _bold(out.at[best_idx, col])
    return out


# ── Public table builders ─────────────────────────────────────────────────────

def results_table(df: pd.DataFrame, caption: str, label: str,
                  include_method: bool = True, two_col: bool = False) -> str:
    fmt = _format_results(df)
    if "group_id" in df.columns:
        fmt["group_id"] = df["group_id"].values
    return _to_latex(fmt, list(RESULTS_COLS), RESULTS_COLS, RESULTS_COLS,
                     caption, label, include_method, two_col,
                     group_col="group_id" if "group_id" in df.columns else None)


def ranked_table(df: pd.DataFrame, caption: str, label: str,
                 include_method: bool = True, two_col: bool = False) -> str:
    fmt = _format_ranked(df)
    if "group_id" in df.columns:
        fmt["group_id"] = df["group_id"].values
    return _to_latex(fmt, list(RANKED_COLS), RANKED_COLS, RANKED_COLS,
                     caption, label, include_method, two_col,
                     group_col="group_id" if "group_id" in df.columns else None)


def params_table(experiments_cfg: dict, params_columns: list,
                 caption: str, label: str, note: str = None) -> str:
    col_keys    = ["id"] + [k for k, _ in params_columns]
    col_headers = {"id": "ID", **{k: h for k, h in params_columns}}

    # All params columns are left-aligned (text content)
    aligns = ["l"] * len(col_keys)
    spec   = "@{}" + "".join(aligns) + "@{}"

    header_row = " & ".join(col_headers[k] for k in col_keys) + r" \\"

    rows       = []
    prev_group = None
    for cfg in experiments_cfg.values():
        current_group = cfg.get("group_id")
        if prev_group is not None and current_group != prev_group:
            rows.append(r"\noalign{\smallskip}")
        rows.append(" & ".join(str(cfg.get(k, "")) for k in col_keys) + r" \\")
        prev_group = current_group

    body = "\n    ".join(rows)

    note_tex = (
        f"\n\\vspace{{2pt}}\n\\raggedright\\footnotesize {note}"
        if note else ""
    )

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


def grouped_ranked_table(
    groups_cfg: dict,
    grouped_df: pd.DataFrame,
    group_params_columns: list,
    caption: str,
    label: str,
) -> str:
    """
    Grouped ranked table: params + n_s/N_s + mean totalrank.
    Winner row: ALL cells bolded.
    Winning criterion cell: additionally marked (already bold, no xcolor needed).
    Winner is determined by lexicographic sort (success_count desc, totalrank asc).
    """
    grp_sorted     = _sort_by_id(grouped_df)
    groups_with_id = {k: {"id": k, **v} for k, v in groups_cfg.items()}
    n_total        = 4

    param_col_keys = (
        ["id"]
        + [k for k, _ in group_params_columns]
        + ["success_count", "totalrank"]
    )
    param_col_hdrs = {
        "id":            "ID",
        "success_count": rf"$n_s/{n_total}$",
        "totalrank":     r"$\overline{total_{rank}}$",
    }
    param_col_hdrs.update({k: h for k, h in group_params_columns})

    # All param cols left, success_count center, totalrank right
    param_aligns = (
        ["l"] * (1 + len(group_params_columns))
        + ["c", "r"]
    )
    spec       = "@{}" + "".join(param_aligns) + "@{}"
    header_row = " & ".join(param_col_hdrs[k] for k in param_col_keys) + r" \\"

    # ── Identify winner lexicographically ─────────────────────────────────────
    # Sort by success_count desc, then totalrank asc to find true winner
    if not grouped_df.empty and "success_count" in grouped_df.columns:
        sorted_for_winner = grouped_df.sort_values(
            ["success_count", "totalrank"],
            ascending=[False, True],
        )
        winner_id  = sorted_for_winner.iloc[0]["experiment_id"]
        winning_by = sorted_for_winner.iloc[0].get("winning_criterion", "")
        # If winning_criterion not set, determine it
        if not winning_by and len(sorted_for_winner) > 1:
            w_ns  = sorted_for_winner.iloc[0]["success_count"]
            r_ns  = sorted_for_winner.iloc[1]["success_count"]
            winning_by = "success_count" if w_ns > r_ns else "totalrank"
    else:
        winner_id  = grp_sorted.iloc[0]["experiment_id"] if not grp_sorted.empty else None
        winning_by = ""

    rows = []
    for gid, gdata in groups_with_id.items():
        match = grp_sorted[grp_sorted["experiment_id"] == gid]
        if match.empty:
            # Group not yet available — show placeholder
            cells = [str(gdata.get(k, "")) for k in ["id"] + [k for k, _ in group_params_columns]]
            cells += ["--", "--"]
            rows.append(" & ".join(cells) + r" \\")
            continue

        tr        = match["totalrank"].values[0]
        ns        = int(match["success_count"].values[0]) if "success_count" in match.columns else 0
        is_winner = (gid == winner_id)
        
        # Si es NaN, le ponemos un guion para LaTeX, si no, usamos tu formateador original
        tr_fmt = "--" if pd.isna(tr) else _fmt(tr)
        ns_fmt = str(ns)

        if is_winner:
            # Bold all cells in winner row
            param_cells = [_bold(str(gdata.get(k, "")))
                           for k in ["id"] + [k for k, _ in group_params_columns]]
            # Extra emphasis on deciding criterion with \underline inside bold
            if winning_by == "success_count":
                ns_fmt = _bold(r"\underline{" + ns_fmt + "}")
                tr_fmt = _bold(tr_fmt)
            else:
                ns_fmt = _bold(ns_fmt)
                # Solo subrayamos si no es un guion por NaN
                if not pd.isna(tr):
                    tr_fmt = _bold(r"\underline{" + tr_fmt + "}")
                else:
                    tr_fmt = _bold(tr_fmt)
            cells = param_cells + [ns_fmt, tr_fmt]
        else:
            cells = (
                [str(gdata.get(k, "")) for k in ["id"] + [k for k, _ in group_params_columns]]
                + [ns_fmt, tr_fmt]
            )

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


# ── Save all tables ───────────────────────────────────────────────────────────

def save_tables(
    ranked_df: pd.DataFrame,
    output_dir: Path,
    prefix: str,
    caption_prefix: str,
    full_summary: pd.DataFrame = None,
    grouped_df: pd.DataFrame = None,
    experiments_cfg: dict = None,
    groups_cfg: dict = None,
    group_params_columns: list = None,
    params_columns: list = None,
    params_note: str = None,
    include_method: bool = True,
) -> None:
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # ── Parameters table ──────────────────────────────────────────────────────
    if experiments_cfg is not None and params_columns is not None:
        p = params_table(
            experiments_cfg,
            params_columns,
            caption=f"{caption_prefix} experiment variable parameters.",
            label=f"tab:{prefix}_params",
            note=params_note,
        )
        (tables_dir / f"{prefix}_params.tex").write_text(p, encoding="utf-8")

    # ── Results table ─────────────────────────────────────────────────────────
    base_df = full_summary if full_summary is not None else ranked_df
    if "is_valid" not in base_df.columns and "is_valid" in ranked_df.columns:
        valid_col = ranked_df[["experiment_id", "is_valid"]].drop_duplicates()
        base_df   = base_df.merge(valid_col, on="experiment_id", how="left")
        base_df["is_valid"] = base_df["is_valid"].fillna(True)

    results_df = _sort_by_id(base_df)
    res = results_table(
        results_df,
        caption=f"{caption_prefix} experiment results.",
        label=f"tab:{prefix}_results",
        include_method=include_method,
    )
    (tables_dir / f"{prefix}_results.tex").write_text(res, encoding="utf-8")

    # ── Ranked table ──────────────────────────────────────────────────────────
    valid_ranked  = ranked_df[ranked_df["is_valid"] == True].copy() \
                    if "is_valid" in ranked_df.columns else ranked_df.copy()
    ranked_sorted = _sort_by_id(valid_ranked)
    rnk = ranked_table(
        ranked_sorted,
        caption=f"{caption_prefix} experiment ranked results.",
        label=f"tab:{prefix}_ranked",
        include_method=include_method,
    )
    (tables_dir / f"{prefix}_ranked.tex").write_text(rnk, encoding="utf-8")

    # ── Grouped ranked table ──────────────────────────────────────────────────
    if grouped_df is not None and groups_cfg is not None and group_params_columns is not None:
        grp = grouped_ranked_table(
            groups_cfg,
            grouped_df,
            group_params_columns,
            caption=f"{caption_prefix} grouped ranked results.",
            label=f"tab:{prefix}_grouped_ranked",
        )
        (tables_dir / f"{prefix}_grouped_ranked.tex").write_text(grp, encoding="utf-8")

    print(f"  Tables -> {tables_dir}/{prefix}_{{params,results,ranked,grouped_ranked}}.tex")
