"""
src/figures.py
--------------
Publication-quality figures for the NBV analysis pipeline.

Figure outputs
--------------
  figures/
    {prefix}_grouped_bar.png
    {prefix}_grouped_heatmap.png
    comparison_grid/
      {prefix}_{group_id}_comparison_grid.png   one per group_id (scene+method)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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
    "font.family":      "serif",
    "axes.titlesize":   11,
    "axes.labelsize":   10,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "legend.fontsize":  9,
    "figure.dpi":       150,
    "savefig.dpi":      300,
    "savefig.bbox":     "tight",
})

METRIC_CFG = {
    "tri_imaged_pct":  ("Percentage retrieved (\%)",           True),
    "cum_travelled_m": ("Accumulated distance (m)",  False),
    "cum_energy":      ("Accumulated energy",         False),
    "tri_quality":     ("Mean quality",               True),
    "total_time":      ("Total time (s)",             False),
    "fitness":         ("Fitness",                    True),
}

GRID_METRICS = [
    "tri_imaged_pct", "cum_travelled_m", "cum_energy", "tri_quality", "total_time",
]
GRID_SUBTITLES = [
    "(a) Percentage retrieved", "(b) Accumulated distance", "(c) Accumulated energy",
    "(d) Mean quality", "(e) Total time",
]


def _style(i):
    return {"color": COLORS[i % len(COLORS)], "linestyle": LINES[i % len(LINES)],
            "marker": MARKERS[i % len(MARKERS)], "linewidth": 1.4, "markersize": 4}


def _plot_metric(ax, experiments, metric, title=None, marker_every=10):
    ylabel, _ = METRIC_CFG.get(metric, (metric.replace("_", " "), True))
    for i, (label, (_, df)) in enumerate(experiments.items()):
        ax.plot(df["view"], df[metric], markevery=marker_every, label=label, **_style(i))
    ax.set_xlabel("View number")
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.4)


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Figure -> {path}")


# ── Comparison grid (one per group_id) ───────────────────────────────────────

def _build_comparison_grid_for_group(
    experiments: dict,
    group_id: str,
    ranked_df: pd.DataFrame,
    experiments_cfg: dict,
    scene_name: str = "",
) -> plt.Figure:
    """
    Build a 2x3 grid for a single group_id.
    Rows/cols 0-4: the 5 metrics.
    Cell [1,2] (index 5): legend panel.
    Each line = one rank_group (parameter variant) within this group_id.
    """
    # Collect experiment IDs belonging to this group_id
    group_exp_ids = {
        ecfg["id"]: ecfg
        for ecfg in experiments_cfg.values()
        if ecfg.get("group_id") == group_id
    }

    # Build sub-experiments dict: {rank_group_label: (meta, df)}
    sub_experiments = {}
    for exp_id, ecfg in sorted(group_exp_ids.items(),
                                key=lambda x: x[0]):
        if exp_id in experiments:
            rg    = ecfg.get("rank_group", exp_id)
            sub_experiments[rg] = experiments[exp_id]

    if not sub_experiments:
        return None

    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    axes = axes.flatten()

    for idx, (metric, subtitle) in enumerate(zip(GRID_METRICS, GRID_SUBTITLES)):
        _plot_metric(axes[idx], sub_experiments, metric, title=subtitle)
        axes[idx].get_legend().remove() if axes[idx].get_legend() else None

    # ── Cell 5: legend panel ──────────────────────────────────────────────────
    ax_leg = axes[5]
    ax_leg.set_axis_off()

    handles = [
        plt.Line2D([0], [0], label=label, **_style(i))
        for i, label in enumerate(sub_experiments.keys())
    ]
    ax_leg.legend(
        handles=handles,
        loc="center",
        title="Parameter group",
        title_fontsize=10,
        fontsize=9,
        framealpha=0.9,
        borderaxespad=0,
    )

    # Subtitle showing group context
    group_label = f"Group {group_id}"
    if scene_name:
        group_label = f"{scene_name} — {group_label}"
    fig.suptitle(group_label, fontsize=12, y=1.01)
    fig.tight_layout()
    return fig


def save_comparison_grids(
    experiments: dict,
    ranked_df: pd.DataFrame,
    experiments_cfg: dict,
    output_dir: Path,
    prefix: str,
    scene_name: str = "",
) -> None:
    """
    Save one comparison grid per group_id into figures/comparison_grid/.
    """
    if not experiments_cfg:
        return

    # Collect unique group_ids in sorted order
    group_ids = sorted(
        set(ecfg.get("group_id", "") for ecfg in experiments_cfg.values()
            if ecfg.get("group_id")),
        key=lambda x: [int(p) for p in str(x).split(".")],
    )

    grid_dir = output_dir / "figures" / "comparison_grid"
    grid_dir.mkdir(parents=True, exist_ok=True)

    for gid in group_ids:
        fig = _build_comparison_grid_for_group(
            experiments, gid, ranked_df, experiments_cfg, scene_name
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
        ax.bar(x[i], m, yerr=s, capsize=5,
               color=c, edgecolor="black", linewidth=0.6, hatch=h,
               error_kw={"elinewidth": 1.2, "ecolor": "black"})

    for i, (m, s, ns) in enumerate(zip(means, stds, success_counts)):
        txt = f"{m:.2f}\n({ns}/{n_total})"
        ax.text(x[i], m + s + max(means) * 0.02, txt,
                ha="center", va="bottom", fontsize=7)

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


# ── Main entry point ──────────────────────────────────────────────────────────

def save_all_figures(
    experiments, ranked_df, output_dir, prefix,
    scene_name="", groups_cfg=None, grouped_df=None,
    group_params_columns=None, experiments_cfg=None,
):
    """
    Generate all figures for a section.

    figures/comparison_grid/   one grid per group_id (legend in 6th panel)
    figures/                   grouped_bar + grouped_heatmap
    """
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Per-group comparison grids
    if experiments_cfg:
        save_comparison_grids(
            experiments, ranked_df, experiments_cfg,
            output_dir, prefix, scene_name,
        )

    # Paper figures
    if groups_cfg is not None and group_params_columns:
        save_grouped_bar(ranked_df, grouped_df, groups_cfg, group_params_columns,
                         output_dir, prefix, scene_name)
        save_grouped_heatmap(ranked_df, groups_cfg, group_params_columns,
                             output_dir, prefix, scene_name)