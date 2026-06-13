"""
run_section.py
--------------
Main entry point. Reads the config.py from a section folder, loads all
log files, computes rankings, and writes all outputs inside that section.

Usage
-----
  python run_section.py <section>
  python run_section.py area

  # Run all sections at once:
  python run_section.py --all

Options
-------
  --missing   Only report which log files are missing without running analysis.
              Useful to check the section is ready before processing.
"""

import argparse
import importlib.util
import sys
import pandas as pd
from pathlib import Path
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from parser  import parse_log
from ranking import rank_experiments, extract_summary, rank_groups
from tables  import save_tables
from figures import save_all_figures

SECTIONS = ["area", "distance_energy", "motion", 
            "quality", "final_obj_comparison", "k_sensitivity", "robust", "robust_comparison"]


# ── Config loader ─────────────────────────────────────────────────────────────

def load_config(section: str):
    config_path = ROOT / section / "config.py"
    if not config_path.exists():
        raise FileNotFoundError(
            f"No config.py found at {config_path}\n"
            f"Create one following the template in area/config.py"
        )
    spec   = importlib.util.spec_from_file_location(f"{section}.config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── Missing-files checker ─────────────────────────────────────────────────────

def check_missing(section: str, cfg) -> list[str]:
    logs_dir = ROOT / section / "logs"
    missing  = []
    for filename, exp_cfg in cfg.EXPERIMENTS.items():
        log_path = logs_dir / f"{filename}.log"
        if not log_path.exists():
            missing.append(f"  [{exp_cfg['id']}]  {filename}.log")
    return missing


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_section(section: str, verbose: bool = True) -> None:
    print(f"\n{'='*60}")
    print(f"  Section: {section}")
    print(f"{'='*60}")

    cfg      = load_config(section)
    meta     = cfg.SECTION_META
    logs_dir = ROOT / section / "logs"
    out_dir  = ROOT / section / "output"

    # ── 1. Check for missing files ────────────────────────────────────────────
    missing = check_missing(section, cfg)
    if missing:
        print(f"\n  WARNING: {len(missing)} log file(s) not found — skipping them:")
        for m in missing:
            print(m)

    # ── 2. Load available log files ───────────────────────────────────────────
    print(f"\n  Loading logs from {logs_dir}/")
    experiments = {}

    for filename, exp_cfg in cfg.EXPERIMENTS.items():
        log_path = logs_dir / f"{filename}.log"
        if not log_path.exists():
            continue
        try:
            log_meta, df = parse_log(log_path)
            exp_id = exp_cfg["id"]
            experiments[exp_id] = (log_meta, df)
            if verbose:
                pct = df.iloc[-1]["tri_imaged_pct"]
                print(f"    {exp_id:>9}  {filename:<28}  %retrieved={pct:.2f}")
        except Exception as e:
            print(f"    ERROR loading {filename}.log: {e}")

    if not experiments:
        print("\n  No log files found. Add .log files to the logs/ folder and re-run.")
        return

    # ── 3. Ranking ────────────────────────────────────────────────────────────
    print(f"\n  Computing ranks  (threshold={cfg.PCT_THRESHOLD}%) ...")
    ranked = rank_experiments(
        experiments,
        pct_threshold     = cfg.PCT_THRESHOLD,
        totalrank_formula = cfg.TOTALRANK_FORMULA,
        experiments_cfg   = cfg.EXPERIMENTS,
        metrics           = cfg.METRICS,
    )
    print(f"  Done.")

    # ── 4. Tables ─────────────────────────────────────────────────────────────
    print("\n  Exporting LaTeX tables ...")

    loaded_ids     = set(experiments.keys())
    loaded_exp_cfg = {
        fname: exp_cfg
        for fname, exp_cfg in cfg.EXPERIMENTS.items()
        if exp_cfg["id"] in loaded_ids
    }

    full_summary = extract_summary(experiments, experiments_cfg=cfg.EXPERIMENTS, metrics= cfg.METRICS)

    groups_cfg     = getattr(cfg, "GROUPS", None)
    grouped_ranked = None
    if groups_cfg and not full_summary.empty:
        grouped_ranked = rank_groups(ranked, groups_cfg, metrics= cfg.METRICS)


    robust_comparison_cfg = None
    if getattr(cfg, "ROBUST_COMPARISON", False):
        robust_comparison_cfg = {
            "baseline_rg":           cfg.ROBUST_BASELINE_RG,
            "delta_f_min_improvement": cfg.DELTA_F_MIN_IMPROVEMENT,
        }
    save_tables(
        ranked_df            = ranked,
        full_summary         = full_summary,
        grouped_df           = grouped_ranked,
        output_dir           = out_dir,
        prefix               = meta["prefix"],
        caption_prefix       = meta["caption_prefix"],
        experiments_cfg      = loaded_exp_cfg,
        params_columns       = getattr(cfg, "PARAMS_COLUMNS", None),
        groups_cfg           = groups_cfg,
        group_params_columns = getattr(cfg, "GROUP_PARAMS_COLUMNS", None),
        params_note          = getattr(cfg, "PARAMS_NOTE", None),
        include_method       = False,
        metrics              = cfg.METRICS,
        robust_comparison_cfg = robust_comparison_cfg,       
    )

    # ── 5. Excel export (Google Drive) ───────────────────────────────────────
    GOOGLE_DRIVE_PATH = Path(r"G:\Mi unidad\NBV")
    GOOGLE_DRIVE_PATH.mkdir(parents=True, exist_ok=True)
    xlsx_path = GOOGLE_DRIVE_PATH / f"{meta['prefix']}.xlsx"

    def sort_by_id(df):
        df = df.copy()
        df["_sort_key"] = df["experiment_id"].apply(
            lambda x: [int(p) if p.isdigit() else p
                       for p in str(x).replace("G", "").split(".")]
        )
        return df.sort_values("_sort_key").drop(columns="_sort_key").reset_index(drop=True)

    def write_sheet_as_table(writer, df, sheet_name, table_name):
        df.to_excel(writer, sheet_name=sheet_name, index=False, float_format="%.6f")
        ws      = writer.sheets[sheet_name]
        n_rows  = len(df) + 1
        n_cols  = len(df.columns)
        last_col = ws.cell(1, n_cols).column_letter
        tbl = Table(displayName=table_name, ref=f"A1:{last_col}{n_rows}")
        tbl.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False, showLastColumn=False,
            showRowStripes=True,   showColumnStripes=False,
        )
        ws.add_table(tbl)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:

        write_sheet_as_table(writer, sort_by_id(full_summary), "summary_results", "tbl_results")
        write_sheet_as_table(writer, sort_by_id(ranked),       "summary_ranked",  "tbl_ranked")

        if grouped_ranked is not None and groups_cfg is not None:
            group_params_columns = getattr(cfg, "GROUP_PARAMS_COLUMNS", [])
            combined_rows = []
            for gid, gdata in groups_cfg.items():
                match = grouped_ranked[grouped_ranked["experiment_id"] == gid]
                totalrank_val = match["totalrank"].values[0] if not match.empty else float("nan")
                combined_rows.append({
                    "experiment_id": gid,
                    **{k: gdata[k] for k, _ in group_params_columns},
                    "totalrank": totalrank_val,
                })
            combined_df = pd.DataFrame(combined_rows)
            combined_df["_sort_key"] = combined_df["experiment_id"].apply(
                lambda x: [int(p) if p.isdigit() else p
                           for p in str(x).replace("G", "").split(".")]
            )
            combined_df = combined_df.sort_values("_sort_key").drop(columns="_sort_key")
            write_sheet_as_table(writer, combined_df, "summary_grouped", "tbl_grouped")

        for exp_id, (_, df) in sorted(
            experiments.items(),
            key=lambda x: [int(p) for p in str(x[0]).split(".")]
        ):
            safe_id = exp_id.replace(".", "_")
            write_sheet_as_table(writer, df, safe_id, f"tbl_{safe_id}")

    print(f"  Excel  → {xlsx_path}  ({len(experiments)} experiments + 3 summary sheets)")

    # ── 6. Figures ────────────────────────────────────────────────────────────
    print("\n  Generating figures ...")
    save_all_figures(
        experiments          = experiments,
        ranked_df            = ranked,
        output_dir           = out_dir,
        prefix               = meta["prefix"],
        scene_name           = meta.get("caption_prefix", ""),
        groups_cfg           = groups_cfg,
        grouped_df           = grouped_ranked,
        group_params_columns = getattr(cfg, "GROUP_PARAMS_COLUMNS", None),
        experiments_cfg      = loaded_exp_cfg,
        metrics              = cfg.METRICS,
        robust_comparison_cfg = robust_comparison_cfg,
    )

    print(f"\n  Done. All outputs in {out_dir}/")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run analysis pipeline for one or all NBV experiment sections.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Examples:",
            "  python run_section.py area",
            "  python run_section.py --all",
            "  python run_section.py area --missing",
        ]),
    )
    parser.add_argument(
        "section", nargs="?",
        choices=SECTIONS,
        help=f"Section to run. One of: {', '.join(SECTIONS)}",
    )
    parser.add_argument("--all",     action="store_true", help="Run all sections.")
    parser.add_argument("--missing", action="store_true", help="Only report missing logs.")
    args = parser.parse_args()

    if not args.all and args.section is None:
        parser.print_help()
        sys.exit(1)

    targets = SECTIONS if args.all else [args.section]

    for section in targets:
        if args.missing:
            cfg     = load_config(section)
            missing = check_missing(section, cfg)
            print(f"\n--- {section} ({len(cfg.EXPERIMENTS)} experiments) ---")
            if missing:
                print(f"  Missing ({len(missing)}):")
                for m in missing:
                    print(m)
            else:
                print("  All log files present.")
        else:
            try:
                run_section(section)
            except Exception as e:
                print(f"\n  ERROR in section '{section}': {e}")
                if not args.all:
                    raise


if __name__ == "__main__":
    main()
