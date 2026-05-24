"""
src/tables.py
-------------
LaTeX table generation matching the thesis style.
Produces two tables per section:
  1. _results.tex  — raw metrics
  2. _ranked.tex   — ranking scores
"""

from pathlib import Path
import pandas as pd


# ── Column definitions ────────────────────────────────────────────────────────
# (display_label, higher_is_better)
RESULTS_COLS = {
    "acc_dist_m":    (r"\thead{Acc.\\ dist. (m)}",  False),
    "acc_energy":    (r"\thead{Acc.\\ energy}",      False),
    "pct_retrieved": (r"\thead{\%ret.}",             True),
    "mean_quality":  (r"\thead{Mean\\ quality}",     True),
    "total_time_s":  (r"\thead{Time\\ (s)}",         False),
}

RANKED_COLS = {
    "drank":     (r"$d_{rank}$",      False),
    "erank":     (r"$e_{rank}$",      False),
    "retrrank":  (r"$retr_{rank}$",   False),
    "qrank":     (r"$q_{rank}$",      False),
    "timerank":  (r"$time_{rank}$",   False),
    "totalrank": (r"$total_{rank}$",  False),
}


# ── Formatting ────────────────────────────────────────────────────────────────

# Columns that need more decimal places
HIGH_PRECISION_COLS = {"mean_quality", "tri_quality"}

def _fmt(v, dec=2):
    if isinstance(v, int) or (isinstance(v, float) and v == int(v)):
        return str(int(v))
    return f"{float(v):.{dec}f}"


def _apply_bold(df: pd.DataFrame, col_cfg: dict) -> pd.DataFrame:
    out = df.copy().astype(object)
    for col, (_, hib) in col_cfg.items():
        if col not in df.columns:
            continue
        series   = df[col].astype(float)
        best_idx = series.idxmax() if hib else series.idxmin()
        dec      = 3 if col in HIGH_PRECISION_COLS else 2
        out[col] = series.map(lambda v, d=dec: _fmt(v, d))
        out.at[best_idx, col] = r"\textbf{" + out.at[best_idx, col] + "}"
    return out


# ── Core LaTeX builder ────────────────────────────────────────────────────────

def _to_latex(fmt_df, cols, headers, caption, label, include_method, two_col=False) -> str:
    display = ["experiment_id"]
    if include_method and "method" in fmt_df.columns:
        display.append("method")
    display += [c for c in cols if c in fmt_df.columns]

    hdr_map = {"experiment_id": "ID", "method": "Method"}
    hdr_map.update({k: v[0] for k, v in headers.items()})

    col_spec   = "l" + "r" * (len(display) - 1)
    header_row = " & ".join(hdr_map.get(c, c) for c in display) + r" \\"
    data_rows  = "\n    ".join(
        " & ".join(str(row[c]) for c in display) + r" \\"
        for _, row in fmt_df[display].iterrows()
    )

    table_env = "table*" if two_col else "table"

    return (
        rf"\begin{{{table_env}}}[ht]" "\n"
        r"\centering" "\n"
        r"\footnotesize" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{col_spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {data_rows}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        rf"\end{{{table_env}}}"
    )


# ── Public functions ──────────────────────────────────────────────────────────

def results_table(df, caption, label, include_method=True, two_col=False) -> str:
    fmt = _apply_bold(df, RESULTS_COLS)
    return _to_latex(fmt, list(RESULTS_COLS), RESULTS_COLS,
                     caption, label, include_method, two_col=two_col)

def ranked_table(df, caption, label, include_method=True, two_col=False) -> str:
    fmt = _apply_bold(df, RANKED_COLS)
    return _to_latex(fmt, list(RANKED_COLS), RANKED_COLS,
                     caption, label, include_method, two_col=two_col)
def grouped_table(df, caption, label, two_col=False) -> str:
    fmt = _apply_bold(df, RANKED_COLS)
    return _to_latex(fmt, list(RANKED_COLS), RANKED_COLS,
                     caption, label, include_method=False, two_col=two_col)

def _sort_by_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_sort_key"] = df["experiment_id"].apply(
        lambda x: [int(p) for p in str(x).split(".")]
    )
    df = df.sort_values("_sort_key").drop(columns="_sort_key")
    return df.reset_index(drop=True)

def params_table(
    experiments_cfg: dict,
    params_columns: list,
    caption: str,
    label: str,
    note: str = None,          # ← nuevo
) -> str:
    col_keys    = ["id"] + [k for k, _ in params_columns]
    col_headers = {"id": "ID", **{k: h for k, h in params_columns}}
    col_spec    = "l" + "l" * (len(col_keys) - 1)
    header_row  = " & ".join(col_headers[k] for k in col_keys) + r" \\"

    rows = []
    for cfg in experiments_cfg.values():
        row = " & ".join(str(cfg.get(k, "")) for k in col_keys) + r" \\"
        rows.append(row)
    body = "\n    ".join(rows)

    # Optional note below the table using \footnotesize
    note_tex = (
        f"\n\\vspace{{2pt}}\n\\raggedright\\footnotesize {note}"
        if note else ""
    )

    return (
        r"\begin{table}[ht]" "\n"
        r"\centering" "\n"
        rf"\caption{{{caption}}}" "\n"
        rf"\label{{{label}}}" "\n"
        rf"\begin{{tabular}}{{{col_spec}}}" "\n"
        r"\hline" "\n"
        f"    {header_row}\n"
        r"\hline" "\n"
        f"    {body}\n"
        r"\hline" "\n"
        r"\end{tabular}"
        f"{note_tex}\n"
        r"\end{table}"
    )


def save_tables(
    ranked_df: pd.DataFrame,
    output_dir: Path,
    prefix: str,
    caption_prefix: str,
    full_summary: pd.DataFrame = None,
    grouped_df: pd.DataFrame = None,        # ← nuevo
    experiments_cfg: dict = None,
    groups_cfg: dict = None,                # ← nuevo
    group_params_columns: list = None,      # ← nuevo
    params_columns: list = None,
    params_note: str = None, 
    include_method: bool = True,
) -> None:
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # Parameters table — individual experiments
    if experiments_cfg is not None and params_columns is not None:
        params = params_table(
            experiments_cfg,
            params_columns,
            caption=f"{caption_prefix} experiment variable parameters.",
            label=f"tab:{prefix}_params",
            note=params_note, 
        )
        (tables_dir / f"{prefix}_params.tex").write_text(params, encoding="utf-8")

    # Results table — all experiments, sorted by ID
    results_df = _sort_by_id(full_summary if full_summary is not None else ranked_df)
    res = results_table(
        results_df,
        caption=f"{caption_prefix} experiment results.",
        label=f"tab:{prefix}_results",
        include_method=include_method,
    )
    (tables_dir / f"{prefix}_results.tex").write_text(res, encoding="utf-8")

    # Ranked table — valid experiments only, sorted by ID
    if "is_valid" in ranked_df.columns:
        valid_ranked = ranked_df[ranked_df["is_valid"] == True].copy()
    else:
        valid_ranked = ranked_df.copy()
    ranked_sorted = _sort_by_id(valid_ranked)
    ranked = ranked_table(
        ranked_sorted,
        caption=f"{caption_prefix} experiment ranked results.",
        label=f"tab:{prefix}_ranked",
        include_method=include_method,
    )
    (tables_dir / f"{prefix}_ranked.tex").write_text(ranked, encoding="utf-8")


    # Grouped combined table (params + totalrank)
    if grouped_df is not None and groups_cfg is not None and group_params_columns is not None:
        groups_with_id = {k: {"id": k, **v} for k, v in groups_cfg.items()}

        # Build combined DataFrame: params columns + totalrank
        grp_sorted = _sort_by_id(grouped_df)

        # Params rows aligned to group order
        param_rows = []
        for gid, gdata in groups_with_id.items():
            match = grp_sorted[grp_sorted["experiment_id"] == gid]
            totalrank_val = match["totalrank"].values[0] if not match.empty else float("nan")
            param_rows.append({"id": gid, **{k: gdata[k] for k, _ in group_params_columns},
                                "totalrank": totalrank_val})
        combined_df = pd.DataFrame(param_rows)

        # Build LaTeX manually
        param_col_keys  = ["id"] + [k for k, _ in group_params_columns] + ["totalrank"]
        param_col_hdrs  = {"id": "ID", "totalrank": r"$total_{rank}$"}
        param_col_hdrs.update({k: h for k, h in group_params_columns})
        col_spec        = "l" * (len(param_col_keys))
        header_row      = " & ".join(param_col_hdrs[k] for k in param_col_keys) + r" \\"

        # Bold the best (lowest) totalrank
        best_idx = combined_df["totalrank"].idxmin()
        rows = []
        for i, row in combined_df.iterrows():
            tr_fmt = _fmt(row["totalrank"])
            if i == best_idx:
                tr_fmt = r"\textbf{" + tr_fmt + "}"
            cells = [str(row[k]) for k in param_col_keys[:-1]] + [tr_fmt]
            rows.append(" & ".join(cells) + r" \\")
        body = "\n    ".join(rows)

        grp_tex = (
            r"\begin{table}[ht]" "\n"
            r"\centering" "\n"
            r"\footnotesize" "\n"
            rf"\caption{{{caption_prefix} grouped ranked results.}}" "\n"
            rf"\label{{tab:{prefix}_grouped_ranked}}" "\n"
            rf"\begin{{tabular}}{{{col_spec}}}" "\n"
            r"\hline" "\n"
            f"    {header_row}\n"
            r"\hline" "\n"
            f"    {body}\n"
            r"\hline" "\n"
            r"\end{tabular}" "\n"
            r"\end{table}"
        )
        (tables_dir / f"{prefix}_grouped_ranked.tex").write_text(grp_tex, encoding="utf-8")

    print(f"  Tables → {tables_dir}/{prefix}_{{params,results,ranked,grouped_ranked}}.tex")