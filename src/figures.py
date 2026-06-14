"""
src/figures.py
--------------
Publication-quality figures for the NBV analysis pipeline.
IEEE Access compliant: Times New Roman, axis labels with units,
subfigure labels centered below panels in 8 pt.

Figure outputs
--------------
  figures/
    {prefix}_analysis.png       (Combined Heatmap + Bar chart)
    comparison_grid/
      {prefix}_{group_id}_comparison_grid.png   one per group_id (scene+method)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path


COLORS        = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
LINES         = ["-", "--", "-.", ":"]
MARKERS       = ["o", "s", "^", "D", "v", "P"]
COLOR_BEST    = "#d62728"
COLOR_DEFAULT = "#1f77b4"
COLOR_INVALID = "#aaaaaa"

plt.rcParams.update({
    "font.family":          "serif",
    "font.serif":           ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset":     "stix",
    "axes.titlesize":       7.5,
    "axes.titleweight":     "normal",
    "axes.labelsize":       8.0,
    "xtick.labelsize":      7.0,
    "ytick.labelsize":      7.0,
    "legend.fontsize":      7.0,
    "legend.title_fontsize":8.0,
    "figure.dpi":           150,
    "savefig.dpi":          300,
    "savefig.bbox":         "tight",
})

# metric_key → (df_column, y-axis label)
_METRIC_CFG = {
    "retrieved": ("tri_imaged_pct",  "Retrieved area (%)"),
    "distance":  ("cum_travelled_m", "Accumulated distance (m)"),
    "energy":    ("cum_energy",      "Accumulated energy (dimensionless)"),
    "quality":   ("tri_quality",     "Mean quality (dimensionless)"),
    "time":      ("total_time",      "Execution time (s)"),
    "delta_f":   ("cum_delta_f",     r"Accumulated $\Delta f$ (dimensionless)"),
}

# Default display order (used when building grids)
_METRIC_ORDER = ["retrieved", "distance", "energy", "quality", "time", "delta_f"]

# IEEE subfigure labels
_SUBFIG_LABELS = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]


def _style(i):
    return {
        "color":     COLORS[i % len(COLORS)],
        "linestyle": LINES[i % len(LINES)],
        "marker":    MARKERS[i % len(MARKERS)],
        "linewidth": 1.2,
        "markersize":3.5,
    }


def _plot_metric(ax, experiments, metric_key, subtitle=None, marker_every=10):
    df_col, ylabel = _METRIC_CFG[metric_key]
    for i, (label, (_, df)) in enumerate(experiments.items()):
        if df_col not in df.columns:
            continue
        ax.plot(df["view"], df[df_col], markevery=marker_every,
                label=label, **_style(i))
    ax.set_xlabel("View number")
    ax.set_ylabel(ylabel)
    if subtitle:
        ax.set_title(subtitle, fontsize=8, pad=4, loc="center")
    ax.grid(True, linestyle="--", alpha=0.35, linewidth=0.6)


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Figure -> {path}")


def _active_grid_metrics(metrics):
    """Return metric keys in display order, filtered to those in metrics list."""
    return [m for m in _METRIC_ORDER if m in metrics and m in _METRIC_CFG]


# ── Comparison grid (one per group_id) ───────────────────────────────────────

def _build_comparison_grid_for_group(
    experiments, group_id, experiments_cfg,
    scene_name="", metrics=None, group_params_columns=None,
):
    if metrics is None:
        metrics = list(_METRIC_CFG.keys())

    grid_metrics = _active_grid_metrics(metrics)
    n_metrics    = len(grid_metrics)
    if n_metrics == 0:
        return None

    group_exp_ids = {
        ecfg["id"]: ecfg
        for ecfg in experiments_cfg.values()
        if ecfg.get("group_id") == group_id
    }
    sub_experiments = {}
    for exp_id, ecfg in sorted(group_exp_ids.items(), key=lambda x: x[0]):
        if exp_id in experiments:
            rg = ecfg.get("rank_group", exp_id)
            sub_experiments[rg] = experiments[exp_id]

    if not sub_experiments:
        return None

    # Always use a 2-column grid; last cell = legend if n_metrics is odd or == 5
    n_cols  = 3
    n_rows  = (n_metrics + n_cols) // n_cols   # enough rows for metrics + legend cell
    n_cells = n_rows * n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(13, n_rows * 3.6))
    axes = axes.flatten()

    for idx, mkey in enumerate(grid_metrics):
        subtitle = _SUBFIG_LABELS[idx] if idx < len(_SUBFIG_LABELS) else f"({idx+1})"
        _plot_metric(axes[idx], sub_experiments, mkey, subtitle=subtitle)

    # Legend cell: next cell after last metric panel
    leg_idx = n_metrics
    axes[leg_idx].set_axis_off()
    handles = [
        plt.Line2D([0], [0], label=label, **_style(i))
        for i, label in enumerate(sub_experiments.keys())
    ]
    if experiments_cfg:
        sample_ecfg = next(
            (ecfg for ecfg in experiments_cfg.values()
             if ecfg.get("group_id") == group_id),
            {}
        )
        param_keys   = [k for k, _ in (metrics or [])] if False else []

    params_title = "Parameter group"

    if group_params_columns:
        params_str   = ", ".join(h for _, h in group_params_columns)
        legend_title = f"Parameter group ({params_str})"
    else:
        legend_title = "Parameter group"

    axes[leg_idx].legend(
        handles=handles, loc="center",
        title=legend_title, title_fontsize=9,
        fontsize=8, framealpha=0.9, borderaxespad=0, handlelength=2.5,
    )
    # Hide any remaining empty cells
    for idx in range(leg_idx + 1, n_cells):
        axes[idx].set_axis_off()

    if scene_name:
        fig.suptitle(f"{scene_name} \u2014 Group {group_id}", fontsize=10, y=1.01)

    fig.tight_layout(rect=[0, 0, 1, 0.98])
    return fig


def save_comparison_grids(
    experiments, ranked_df, experiments_cfg,
    output_dir, prefix, scene_name="", metrics=None,
    group_params_columns=None,
):
    if not experiments_cfg:
        return

    group_ids = sorted(
        set(ecfg.get("group_id", "") for ecfg in experiments_cfg.values()
            if ecfg.get("group_id")),
        key=lambda x: [int(p) for p in str(x).split(".")],
    )

    grid_dir = output_dir / "figures" / "comparison_grid"
    grid_dir.mkdir(parents=True, exist_ok=True)

    for gid in group_ids:
        fig = _build_comparison_grid_for_group(
            experiments, gid, experiments_cfg, scene_name,
            metrics=metrics, group_params_columns=group_params_columns,
        )
        if fig is not None:
            safe_gid = gid.replace(".", "_")
            _save(fig, grid_dir / f"{prefix}_{safe_gid}_comparison_grid.png")


# ── Combined Grouped Analysis (Heatmap + Bar Chart) ───────────────────────────

def save_combined_grouped_analysis(
    ranked_df, grouped_df, groups_cfg, group_params_columns,
    output_dir, prefix, title=""
):
    """
    Creates a single, full-width figure containing both the heatmap (a)
    and the grouped bar chart (b), adhering to IEEE formatting standards.
    """
    if groups_cfg is None or grouped_df is None:
        return

    rank_col = "rank_group" if "rank_group" in ranked_df.columns else "group_id"
    if rank_col not in ranked_df.columns:
        return

    # Full page width IEEE Access (two-column span) -> ~7.16 inches.
    fig = plt.figure(figsize=(7.16, 2.3))
    
    # GridSpec used to make the bar chart wider than the heatmap (ratios 1 to 2.0)
    gs = plt.GridSpec(1, 2, figure=fig, width_ratios=[1.0, 2.0])
    ax_heat = fig.add_subplot(gs[0, 0])
    ax_bar  = fig.add_subplot(gs[0, 1])
    
    # Common parameter string for axes
    params_str = ", ".join(h for _, h in group_params_columns)

    # ==========================================================
    # 1. Heatmap (Left Panel - ax_heat)
    # ==========================================================
    group_ids_present = sorted(
        ranked_df["group_id"].unique(),
        key=lambda x: [int(p) for p in str(x).split(".")],
    )
    rank_group_ids = list(groups_cfg.keys())

    matrix       = np.full((len(rank_group_ids), len(group_ids_present)), np.nan)
    invalid_mask = np.zeros_like(matrix, dtype=bool)

    for i, rg in enumerate(rank_group_ids):
        sub_df = ranked_df[ranked_df[rank_col] == rg]
        for j, gid in enumerate(group_ids_present):
            match = sub_df[sub_df["group_id"] == gid]
            if not match.empty:
                matrix[i, j]       = float(match["totalrank"].values[0])
                invalid_mask[i, j] = not bool(match["is_valid"].values[0]) \
                                     if "is_valid" in match.columns else False

    col_labels = [str(g) for g in group_ids_present]

    display_matrix = np.where(invalid_mask, np.nan, matrix)
    vmin = np.nanmin(matrix) if not np.all(np.isnan(display_matrix)) else 0
    vmax = np.nanmax(matrix) if not np.all(np.isnan(display_matrix)) else 1
    
    im = ax_heat.imshow(display_matrix, aspect="auto", cmap="viridis_r", vmin=vmin, vmax=vmax)

    if invalid_mask.any():
        grey = np.where(invalid_mask, 1.0, np.nan)
        cmap_grey = matplotlib.colors.ListedColormap([COLOR_INVALID])
        ax_heat.imshow(grey, aspect="auto", cmap=cmap_grey, vmin=0, vmax=1, alpha=0.6)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            if np.isnan(val):
                ax_heat.text(j, i, "--", ha="center", va="center", fontsize=6.5)
            else:
                text     = f"({val:.1f})" if invalid_mask[i, j] else f"{val:.1f}"
                norm_val = (val - vmin) / (vmax - vmin + 1e-9)
                color    = "black" if (norm_val < 0.6 or invalid_mask[i, j]) else "white"
                ax_heat.text(j, i, text, ha="center", va="center", fontsize=6.5, color=color)

    ax_heat.set_xticks(range(len(col_labels)))
    ax_heat.set_xticklabels(col_labels, fontsize=7, rotation=30, ha="right")
    ax_heat.set_yticks(range(len(rank_group_ids)))
    ax_heat.set_yticklabels(rank_group_ids, fontsize=7)
    
    # labelpad garantiza que el nombre del eje baje lo suficiente y no choque con los números rotados
    ax_heat.set_xlabel("Scene–method configurations", fontsize=8, labelpad=3)
    ax_heat.set_ylabel("Parametric variations", fontsize=8)

    # Colorbar attached to heatmap
    cbar = plt.colorbar(im, ax=ax_heat, shrink=0.8, pad=0.04)
    cbar.set_label(r"Total rank ($\text{total}_{\text{rank}}$)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    # RE-ALINEACIÓN INFERIOR (Left Panel): Leyenda bajada a -0.32 y subfigura a -0.52
    legend_handles_heat = [
        mpatches.Patch(facecolor=COLOR_INVALID, alpha=0.6, label="Invalid — below threshold"),
    ]
    ax_heat.legend(handles=legend_handles_heat, loc="upper center",
                   bbox_to_anchor=(0.5, -0.32), ncol=1, framealpha=0.9, fontsize=7)
    
    ax_heat.text(0.5, -0.52, "(a) Total rank distribution", transform=ax_heat.transAxes, 
                 ha="center", va="top", fontsize=8, weight="bold")


    # ==========================================================
    # 2. Bar Chart (Right Panel - ax_bar)
    # ==========================================================
    n_total = 4
    labels, means, stds, success_counts = [], [], [], []
    for gid, gdata in groups_cfg.items():
        match = grouped_df[grouped_df["experiment_id"] == gid]
        if match.empty:
            continue
        sub = ranked_df[ranked_df[rank_col] == gid]["totalrank"]
        labels.append(gid)
        means.append(float(match["totalrank"].values[0]))
        stds.append(sub.std(ddof=1) if len(sub) > 1 else 0.0)
        success_counts.append(
            int(match["success_count"].values[0]) if "success_count" in match.columns else n_total
        )

    if means:
        max_ns = max(success_counts) if success_counts else n_total
        if "success_count" in grouped_df.columns:
            sorted_winner = grouped_df.sort_values(["success_count", "totalrank"], ascending=[False, True])
            winner_id = sorted_winner.iloc[0]["experiment_id"] if not sorted_winner.empty else None
        else:
            winner_id = grouped_df.sort_values("totalrank").iloc[0]["experiment_id"] if not grouped_df.empty else None

        colors  = [COLOR_BEST if lb == winner_id else COLOR_DEFAULT for lb in labels]
        hatches = ["///" if sc < max_ns else "" for sc in success_counts]

        x = np.arange(len(labels))
        
        for i, (m, s, c, h) in enumerate(zip(means, stds, colors, hatches)):
            is_zero = np.isnan(m) or m == 0
            bar_height = 0.01 if is_zero else m
            bar_std = 0.0 if is_zero else s
            alpha_val = 0.0 if is_zero else 1.0
            edge_c = "none" if is_zero else "black"
            
            ax_bar.bar(x[i], bar_height, yerr=bar_std, capsize=4 if not is_zero else 0,
                       color=c, edgecolor=edge_c, linewidth=0.6, hatch=h, alpha=alpha_val,
                       error_kw={"elinewidth": 1.0, "ecolor": "black"})

        max_mean_val = max(means) if any(~np.isnan(means)) else 10.0
        
        for i, (m, s, ns) in enumerate(zip(means, stds, success_counts)):
            mean_val = 0.0 if (np.isnan(m) or m == 0) else m
            std_val = 0.0 if np.isnan(s) else s
            
            # SOLUCIÓN TEXTO ROJO: Modificado y_pos base para empujar los textos en cero 
            # un poco más arriba y evitar que pisen la línea negra del eje
            txt = f"{mean_val:.2f}\n({ns}/{n_total})"
            y_pos = max_mean_val * 0.06 if mean_val == 0 else mean_val + std_val + max_mean_val * 0.02
            ax_bar.text(x[i], y_pos, txt, ha="center", va="bottom", fontsize=6.5, 
                        color="black" if mean_val > 0 else "darkred")

        ax_bar.set_xticks(x)
        # El mapeo de rotación ahora coincide exactamente con el del Heatmap
        ax_bar.set_xticklabels(labels, fontsize=7, rotation=30, ha="right")
        
        # labelpad agregado para empujar de forma idéntica el título del eje X
        ax_bar.set_xlabel("Parametric variations", fontsize=8, labelpad=3)
        ax_bar.set_ylabel(r"Group rank ($\text{group}_{\text{rank}}$)", fontsize=8)
        ax_bar.grid(axis="y", linestyle="--", alpha=0.4)
        ax_bar.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.35)

        # RE-ALINEACIÓN INFERIOR (Right Panel): Sincronizado exactamente con el panel izquierdo
        legend_handles_bar = [
            mpatches.Patch(color=COLOR_BEST,    label="Winner"),
            mpatches.Patch(color=COLOR_DEFAULT, label="Other groups"),
        ]
        if any(h for h in hatches):
            legend_handles_bar.append(
                mpatches.Patch(facecolor="white", edgecolor="black", hatch="///", 
                               label=f"$n_s < {max_ns}$ (excluded)")
            )
        
        ax_bar.legend(handles=legend_handles_bar, loc="upper center",
                    bbox_to_anchor=(0.5, -0.32), ncol=len(legend_handles_bar),
                    framealpha=0.9, fontsize=7)

        ax_bar.text(0.5, -0.52, "(b) Mean performance comparison", transform=ax_bar.transAxes, 
                    ha="center", va="top", fontsize=8, weight="bold")

    # Modificado el espacio inferior relativo (bottom=0.30) para acomodar los nuevos márgenes sin recortes
    fig.subplots_adjust(bottom=0.30, wspace=0.35, top=0.94, left=0.08, right=0.96)
    
    # Save the combined figure
    _save(fig, output_dir / "figures" / f"{prefix}_analysis.png")


# ── Delta f comparison figure (robust_comparison section only) ────────────────

def save_delta_f_comparison_figure(
    ranked_df, experiments_cfg, groups_cfg,
    baseline_rg, delta_f_min_improvement,
    output_dir, prefix,
):
    if "acc_delta_f" not in ranked_df.columns:
        return

    rank_col = "rank_group" if "rank_group" in ranked_df.columns else "group_id"

    # One bar per mu, averaged across all group_ids
    mu_labels = []
    mu_means  = []
    mu_valid  = []   # True if n_s=4 for this rank_group

    n_total = len(set(ranked_df["group_id"].unique()))

    for rg, gdata in groups_cfg.items():
        sub      = ranked_df[ranked_df[rank_col] == rg]
        valid    = sub[sub["is_valid"] == True] if "is_valid" in sub.columns else sub
        mean_df  = valid["acc_delta_f"].mean() if "acc_delta_f" in valid.columns \
                   and not valid.empty else float("nan")
        ns       = len(valid)

        mu_labels.append(gdata.get("mu", rg))
        mu_means.append(mean_df)
        mu_valid.append(ns == n_total)

    # Baseline delta_f for improvement line
    baseline_idx = list(groups_cfg.keys()).index(baseline_rg) \
                   if baseline_rg in groups_cfg else 0
    baseline_val = mu_means[baseline_idx] \
                   if not pd.isna(mu_means[baseline_idx]) else None

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(mu_labels))

    bar_colors = []
    for i, (mean, valid) in enumerate(zip(mu_means, mu_valid)):
        if i == baseline_idx:
            bar_colors.append(COLOR_DEFAULT)
        elif not valid:
            bar_colors.append(COLOR_INVALID)
        else:
            if baseline_val and not np.isnan(mean):
                improvement = 100.0 * (baseline_val - mean) / abs(baseline_val)
                bar_colors.append(
                    COLOR_BEST if improvement >= delta_f_min_improvement
                    else COLOR_DEFAULT
                )
            else:
                bar_colors.append(COLOR_DEFAULT)

    bars = ax.bar(
        x, mu_means, color=bar_colors,
        edgecolor="black", linewidth=0.6, width=0.6,
    )

    # Annotate bars
    max_val = max((v for v in mu_means if not np.isnan(v)), default=1.0)
    for i, (bar, valid) in enumerate(zip(bars, mu_valid)):
        h = bar.get_height()
        if not np.isnan(h):
            suffix = "" if valid else " (N/A)"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max_val * 0.01,
                f"{h:.3f}{suffix}",
                ha="center", va="bottom", fontsize=7,
            )

    # Threshold line: baseline * (1 - improvement/100)
    if baseline_val is not None:
        threshold_val = baseline_val * (1.0 - delta_f_min_improvement / 100.0)
        ax.axhline(
            y=threshold_val, color=COLOR_BEST,
            linestyle="--", linewidth=1.2,
            label=f"Minimum improvement threshold ({delta_f_min_improvement:.0f}\\%)",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(mu_labels, fontsize=8)
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"Mean accumulated $\Delta f$ (lower = more robust)")
    ax.set_title(
        r"Neighborhood degradation across $\mu$ values",
        fontsize=9,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.35, linewidth=0.6)

    legend_handles = [
        mpatches.Patch(color=COLOR_DEFAULT, label="Baseline / below threshold"),
        mpatches.Patch(color=COLOR_BEST,    label="Above threshold (selected candidate)"),
        mpatches.Patch(color=COLOR_INVALID, label=r"$n_s < 4$ (excluded)"),
    ]
    ax.legend(
        handles=legend_handles, loc="upper center",
        bbox_to_anchor=(0.5, -0.14), ncol=3,
        framealpha=0.9, fontsize=8,
    )

    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_delta_f_comparison.png")

# ── Main entry point ──────────────────────────────────────────────────────────

def save_all_figures(
    experiments, ranked_df, output_dir, prefix,
    scene_name="", groups_cfg=None, grouped_df=None,
    group_params_columns=None, experiments_cfg=None,
    metrics=None,
    robust_comparison_cfg=None, 
    section_type="standard",
):
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)


    if section_type == "comparison":
        if experiments_cfg:
            save_comparison_grids(
                experiments, ranked_df, experiments_cfg,
                output_dir, prefix, scene_name, metrics=metrics,
                group_params_columns=group_params_columns,
            )
    elif section_type == "standard":
        if groups_cfg is not None and group_params_columns:
            # Generate the unified IEEE multipanel figure
            save_combined_grouped_analysis(
                ranked_df=ranked_df,
                grouped_df=grouped_df,
                groups_cfg=groups_cfg,
                group_params_columns=group_params_columns,
                output_dir=output_dir,
                prefix=prefix,
                title=scene_name
            )

        # ── Delta f comparison (robust_comparison section only) ───────────────────
        if robust_comparison_cfg is not None and experiments_cfg is not None:
            save_delta_f_comparison_figure(
                ranked_df               = ranked_df,
                experiments_cfg         = experiments_cfg,
                groups_cfg              = groups_cfg,
                baseline_rg             = robust_comparison_cfg["baseline_rg"],
                delta_f_min_improvement = robust_comparison_cfg["delta_f_min_improvement"],
                output_dir              = output_dir,
                prefix                  = prefix,
            )
    else:
        raise ValueError(f"Unknown section_type: {section_type!r}")