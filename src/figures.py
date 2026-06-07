"""
src/figures.py
--------------
Publication-quality figures for the NBV analysis pipeline.
IEEE Access compliant: Times New Roman, axis labels with units,
subfigure labels centered below panels in 8 pt.

Figure outputs
--------------
  figures/
    {prefix}_grouped_bar.png
    {prefix}_grouped_heatmap.png
    comparison_grid/
      {prefix}_{group_id}_comparison_grid.png   one per group_id (scene+method)

Which panels appear in the comparison grid is driven by the METRICS list
from config.py.
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
    "axes.titlesize":       8,
    "axes.titleweight":     "normal",
    "axes.labelsize":       9,
    "xtick.labelsize":      8,
    "ytick.labelsize":      8,
    "legend.fontsize":      8,
    "legend.title_fontsize":9,
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
    experiments, group_id, experiments_cfg, scene_name="", metrics=None,
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
    axes[leg_idx].legend(
        handles=handles, loc="center",
        title="Parameter group", title_fontsize=9,
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
            experiments, gid, experiments_cfg, scene_name, metrics=metrics,
        )
        if fig is not None:
            safe_gid = gid.replace(".", "_")
            _save(fig, grid_dir / f"{prefix}_{safe_gid}_comparison_grid.png")


# ── Grouped bar ───────────────────────────────────────────────────────────────

def save_grouped_bar(
    ranked_df, grouped_df, groups_cfg, group_params_columns,
    output_dir, prefix, title="",
):
    if grouped_df is None or groups_cfg is None:
        return

    n_total = 4

    # Use group IDs (G1, G2...) as x-axis labels
    labels, means, stds, success_counts = [], [], [], []
    for gid, gdata in groups_cfg.items():
        match = grouped_df[grouped_df["experiment_id"] == gid]
        if match.empty:
            continue
        rank_col = "rank_group" if "rank_group" in ranked_df.columns else "group_id"
        sub = ranked_df[ranked_df[rank_col] == gid]["totalrank"]
        labels.append(gid)   # G1, G2... as label
        means.append(float(match["totalrank"].values[0]))
        stds.append(sub.std(ddof=1) if len(sub) > 1 else 0.0)
        success_counts.append(
            int(match["success_count"].values[0])
            if "success_count" in match.columns else n_total
        )

    if not means:
        return

    # Winner: lexicographic (most successes, then lowest mean)
    max_ns = max(success_counts) if success_counts else n_total
    if "success_count" in grouped_df.columns:
        sorted_winner = grouped_df.sort_values(
            ["success_count", "totalrank"], ascending=[False, True]
        )
        winner_id = sorted_winner.iloc[0]["experiment_id"] if not sorted_winner.empty else None
    else:
        winner_id = grouped_df.sort_values("totalrank").iloc[0]["experiment_id"] \
                    if not grouped_df.empty else None

    colors  = [COLOR_BEST if lb == winner_id else COLOR_DEFAULT for lb in labels]
    # Hatch only bars excluded from final comparison (ns < max observed ns)
    hatches = ["///" if sc < max_ns else "" for sc in success_counts]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(max(5, len(labels) * 0.9), 4.5))

    for i, (m, s, c, h) in enumerate(zip(means, stds, colors, hatches)):
        is_zero = np.isnan(m) or m == 0
        bar_height = 0.01 if is_zero else m
        bar_std = 0.0 if is_zero else s
        
        alpha_val = 0.0 if is_zero else 1.0
        edge_c = "none" if is_zero else "black"
        
        ax.bar(x[i], bar_height, yerr=bar_std, capsize=5 if not is_zero else 0,
               color=c, edgecolor=edge_c, linewidth=0.6, hatch=h, alpha=alpha_val,
               error_kw={"elinewidth": 1.2, "ecolor": "black"})


    max_mean_val = max(means) if any(~np.isnan(means)) else 10.0
    
    for i, (m, s, ns) in enumerate(zip(means, stds, success_counts)):
        mean_val = 0.0 if (np.isnan(m) or m == 0) else m
        std_val = 0.0 if np.isnan(s) else s
        
        txt = f"{mean_val:.2f}\n({ns}/{n_total})"
        
        if mean_val == 0:
            y_pos = max_mean_val * 0.02 
        else:
            y_pos = mean_val + std_val + max_mean_val * 0.02
            
        ax.text(x[i], y_pos, txt,
                ha="center", va="bottom", fontsize=7, 
                color="black" if mean_val > 0 else "darkred")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    # Build axis label from GROUP_PARAMS_COLUMNS header, stripping LaTeX for matplotlib
    # Use param header directly as matplotlib mathtext (keep $ signs)
    param_header = group_params_columns[0][1]
    ax.set_xlabel(f"Parameter group ({param_header})")
    ax.set_ylabel("Mean total rank (lower = better)")
    ax.set_title(title or f"{prefix} -- grouped ranking")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.35)

    legend_handles = [
        mpatches.Patch(color=COLOR_BEST,    label="Winner"),
        mpatches.Patch(color=COLOR_DEFAULT, label="Other groups"),
    ]
    if any(h for h in hatches):
        legend_handles.append(
            mpatches.Patch(facecolor="white", edgecolor="black",
                           hatch="///", label=f"$n_s < {max_ns}$ (excluded)")
        )
    ax.legend(handles=legend_handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.12), ncol=len(legend_handles),
              framealpha=0.9, fontsize=8)

    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_grouped_bar.png")


# ── Grouped heatmap ───────────────────────────────────────────────────────────

def save_grouped_heatmap(
    ranked_df, groups_cfg, group_params_columns,
    output_dir, prefix, title="",
):
    if groups_cfg is None:
        return

    rank_col = "rank_group" if "rank_group" in ranked_df.columns else "group_id"
    if rank_col not in ranked_df.columns:
        return

    # Rows = rank_groups (G1, G2...), Cols = group_ids (1.01, 1.02...)
    group_ids_present = sorted(
        ranked_df["group_id"].unique(),
        key=lambda x: [int(p) for p in str(x).split(".")],
    )
    rank_group_ids = list(groups_cfg.keys())

    matrix      = np.full((len(rank_group_ids), len(group_ids_present)), np.nan)
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

    cell_w = max(5, len(group_ids_present) * 1.6)
    cell_h = max(3, len(rank_group_ids) * 0.6)
    fig, ax = plt.subplots(figsize=(cell_w, cell_h))

    display_matrix = np.where(invalid_mask, np.nan, matrix)
    vmin = np.nanmin(matrix) if not np.all(np.isnan(display_matrix)) else 0
    vmax = np.nanmax(matrix) if not np.all(np.isnan(display_matrix)) else 1
    im = ax.imshow(display_matrix, aspect="auto", cmap="viridis_r", vmin=vmin, vmax=vmax)

    # Grey fill for invalid
    if invalid_mask.any():
        grey = np.where(invalid_mask, 1.0, np.nan)
        cmap_grey = matplotlib.colors.ListedColormap([COLOR_INVALID])
        ax.imshow(grey, aspect="auto", cmap=cmap_grey, vmin=0, vmax=1, alpha=0.6)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            if np.isnan(val):
                ax.text(j, i, "--", ha="center", va="center", fontsize=8)
            else:
                text     = f"({val:.1f})" if invalid_mask[i, j] else f"{val:.1f}"
                norm_val = (val - vmin) / (vmax - vmin + 1e-9)
                color    = "black" if (norm_val < 0.6 or invalid_mask[i, j]) else "white"
                ax.text(j, i, text, ha="center", va="center", fontsize=8, color=color)

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=8, rotation=30, ha="right")
    # Y axis: use group IDs (G1, G2...) not parameter values
    ax.set_yticks(range(len(rank_group_ids)))
    ax.set_yticklabels(rank_group_ids, fontsize=9)
    param_header  = group_params_columns[0][1]
    ax.set_xlabel("Ranking group (scene + method)", fontsize=10)
    ax.set_ylabel(f"Parameter group ({param_header})", fontsize=10)
    ax.set_title(title or f"{prefix} -- totalrank heatmap", fontsize=11)

    cbar = plt.colorbar(im, ax=ax, label="totalrank (lower = better)", shrink=0.8)

    legend_handles = [
        mpatches.Patch(facecolor=COLOR_INVALID, alpha=0.6,
                       label="Invalid — below threshold"),
    ]
    ax.legend(handles=legend_handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.18), ncol=1, framealpha=0.9, fontsize=8)

    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_grouped_heatmap.png")

# ── K stability figure (k_sensitivity section only) ───────────────────────────

def save_k_stability_figure(
    grouped_df, k_values_order, threshold,
    output_dir, prefix,
):
    """
    Line plot of mean totalrank vs k with a horizontal dashed line
    marking the stability threshold. Used only in the k_sensitivity section.

    grouped_df rows must be ordered to match k_values_order.
    """
    if grouped_df is None or grouped_df.empty:
        return

    # Extract totalrank values in k_values_order
    totalranks = []
    for i, k_val in enumerate(k_values_order):
        if i >= len(grouped_df):
            totalranks.append(float("nan"))
            continue
        tr = grouped_df.iloc[i]["totalrank"]
        totalranks.append(float(tr) if not pd.isna(tr) else float("nan"))

    # Compute percentage changes between consecutive k values
    pct_changes = []
    for i in range(len(totalranks) - 1):
        curr, nxt = totalranks[i], totalranks[i + 1]
        if np.isnan(curr) or np.isnan(nxt) or curr == 0:
            pct_changes.append(float("nan"))
        else:
            pct_changes.append(100.0 * abs(nxt - curr) / curr)

    # Find first stable k
    stable_k = None
    for i, pct in enumerate(pct_changes):
        if not np.isnan(pct) and pct < threshold:
            stable_k = k_values_order[i]
            break

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # ── Left panel: totalrank vs k ────────────────────────────────────────────
    ax = axes[0]
    ax.plot(
        k_values_order, totalranks,
        color=COLOR_DEFAULT, linestyle="-", marker="o",
        linewidth=1.4, markersize=5, label="Mean totalrank",
    )

    if stable_k is not None:
        stable_idx = k_values_order.index(stable_k)
        ax.axvline(
            x=stable_k, color=COLOR_BEST,
            linestyle="--", linewidth=1.2,
            label=f"Selected $k={stable_k}$",
        )
        ax.plot(
            stable_k, totalranks[stable_idx],
            marker="*", color=COLOR_BEST,
            markersize=10, zorder=5,
        )

    ax.set_xlabel("$k$ (neighborhood sample size)")
    ax.set_ylabel("Mean total rank (lower = better)")
    ax.set_xticks(k_values_order)
    ax.grid(True, linestyle="--", alpha=0.35, linewidth=0.6)
    ax.legend(fontsize=8, framealpha=0.9)
    ax.set_title("(a)", fontsize=8, pad=4, loc="center")

    # ── Right panel: percentage change between consecutive k ──────────────────
    ax = axes[1]
    x_mid = [
        f"$k={k_values_order[i]}\\to{k_values_order[i+1]}$"
        for i in range(len(k_values_order) - 1)
    ]
    x_pos = range(len(x_mid))

    bar_colors = [
        COLOR_BEST if (not np.isnan(p) and p < threshold) else COLOR_DEFAULT
        for p in pct_changes
    ]
    ax.bar(
        x_pos, pct_changes,
        color=bar_colors, edgecolor="black",
        linewidth=0.6, width=0.5,
    )
    ax.axhline(
        y=threshold, color=COLOR_BEST,
        linestyle="--", linewidth=1.2,
        label=f"Stability threshold ({threshold:.0f}\\%)",
    )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_mid, fontsize=8)
    ax.set_xlabel("Transition")
    ax.set_ylabel(r"$\Delta$ totalrank (\%)")
    ax.grid(axis="y", linestyle="--", alpha=0.35, linewidth=0.6)
    ax.legend(fontsize=8, framealpha=0.9)
    ax.set_title("(b)", fontsize=8, pad=4, loc="center")

    # Annotate bars with values
    max_pct = max((p for p in pct_changes if not np.isnan(p)), default=threshold)
    for i, pct in enumerate(pct_changes):
        if not np.isnan(pct):
            ax.text(
                i, pct + max_pct * 0.02,
                f"{pct:.2f}\\%",
                ha="center", va="bottom", fontsize=7,
            )

    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_k_stability.png")

# ── Main entry point ──────────────────────────────────────────────────────────

def save_all_figures(
    experiments, ranked_df, output_dir, prefix,
    scene_name="", groups_cfg=None, grouped_df=None,
    group_params_columns=None, experiments_cfg=None,
    metrics=None,
    k_stability_cfg=None,
):
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    if experiments_cfg:
        save_comparison_grids(
            experiments, ranked_df, experiments_cfg,
            output_dir, prefix, scene_name, metrics=metrics,
        )

    if groups_cfg is not None and group_params_columns:
        save_grouped_bar(ranked_df, grouped_df, groups_cfg, group_params_columns,
                         output_dir, prefix, scene_name)
        save_grouped_heatmap(ranked_df, groups_cfg, group_params_columns,
                             output_dir, prefix, scene_name)

    # ── K stability figure (k_sensitivity section only) ───────────────────────
    if k_stability_cfg is not None and grouped_df is not None:
        save_k_stability_figure(
            grouped_df      = grouped_df,
            k_values_order  = k_stability_cfg["k_values_order"],
            threshold       = k_stability_cfg["threshold"],
            output_dir      = output_dir,
            prefix          = prefix,
        )