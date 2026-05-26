"""
src/figures.py
--------------
Publication-quality figures for the NBV analysis pipeline.

Figure outputs
--------------
  figures/internal/
    {prefix}_comparison_grid.png
    {prefix}_time_comparison.png
    {prefix}_ranking.png

  figures/
    {prefix}_grouped_bar.png
    {prefix}_grouped_heatmap.png
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
    "tri_imaged_pct":  (r"$\%retrieved$",           True),
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
    "(a) % Retrieved", "(b) Accumulated distance", "(c) Accumulated energy",
    "(d) Mean quality", "(e) Total time",
]


def _style(i):
    return {"color": COLORS[i % len(COLORS)], "linestyle": LINES[i % len(LINES)],
            "marker": MARKERS[i % len(MARKERS)], "linewidth": 1.4, "markersize": 4}


def _plot_metric(ax, experiments, metric, title=None, show_legend=True, marker_every=10):
    ylabel, _ = METRIC_CFG.get(metric, (metric.replace("_", " "), True))
    for i, (label, (_, df)) in enumerate(experiments.items()):
        ax.plot(df["view"], df[metric], markevery=marker_every, label=label, **_style(i))
    ax.set_xlabel("View number")
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.4)
    if show_legend:
        ax.legend(framealpha=0.8)


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Figure -> {path}")


# ── Figure builders ───────────────────────────────────────────────────────────

def _build_comparison_grid(experiments, scene_name=""):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    axes = axes.flatten()
    for idx, (metric, subtitle) in enumerate(zip(GRID_METRICS, GRID_SUBTITLES)):
        _plot_metric(axes[idx], experiments, metric, title=subtitle, show_legend=False)
    axes[5].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center",
               bbox_to_anchor=(0.5, -0.04), ncol=min(len(handles), 4),
               framealpha=0.9, fontsize=9)
    if scene_name:
        fig.suptitle(f"{scene_name} -- experiment graphs", fontsize=12, y=1.01)
    fig.tight_layout()
    return fig


def _build_time_comparison(experiments, prefix):
    labels = list(experiments.keys())
    times  = [df.iloc[-1]["total_time"] for (_, df) in experiments.values()]
    colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
    fig, ax = plt.subplots(figsize=(max(4, len(labels) * 1.4), 4))
    bars = ax.bar(labels, times, color=colors, edgecolor="black", linewidth=0.6)
    ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
    ax.set_ylabel("Total time (s)")
    ax.set_title(f"{prefix} -- computation time")
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(times) * 1.2)
    fig.tight_layout()
    return fig


def _build_ranking_bar(ranked_df, prefix):
    df     = ranked_df.sort_values("totalrank")
    labels = df["experiment_id"].tolist()
    ranks  = df["totalrank"].tolist()
    colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
    fig, ax = plt.subplots(figsize=(6, max(3, len(labels) * 0.7)))
    bars = ax.barh(labels, ranks, color=colors, edgecolor="black", linewidth=0.6)
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=9)
    ax.set_xlabel("Total rank (lower = better)")
    ax.set_title(f"{prefix} -- total rank comparison")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_xlim(0, max(ranks) * 1.2 if max(ranks) > 0 else 1)
    fig.tight_layout()
    return fig


# ── Public save wrappers ──────────────────────────────────────────────────────

def save_comparison_grid(experiments, output_dir, prefix, scene_name=""):
    if len(experiments) >= 2:
        _save(_build_comparison_grid(experiments, scene_name),
              output_dir / "figures" / f"{prefix}_comparison_grid.png")

def save_time_comparison(experiments, output_dir, prefix, title=""):
    _save(_build_time_comparison(experiments, prefix),
          output_dir / "figures" / f"{prefix}_time_comparison.png")

def save_ranking_bar(ranked_df, output_dir, prefix, title=""):
    _save(_build_ranking_bar(ranked_df, prefix),
          output_dir / "figures" / f"{prefix}_ranking.png")


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
    if "success_count" in grouped_df.columns:
        sorted_winner = grouped_df.sort_values(
            ["success_count", "totalrank"], ascending=[False, True]
        )
        winner_id = sorted_winner.iloc[0]["experiment_id"] if not sorted_winner.empty else None
    else:
        winner_id = grouped_df.sort_values("totalrank").iloc[0]["experiment_id"] \
                    if not grouped_df.empty else None

    colors  = [COLOR_BEST if lb == winner_id else COLOR_DEFAULT for lb in labels]
    hatches = ["///" if sc < n_total else "" for sc in success_counts]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(max(5, len(labels) * 0.9), 4.5))

    for i, (m, s, c, h) in enumerate(zip(means, stds, colors, hatches)):
        ax.bar(x[i], m, yerr=s, capsize=5,
               color=c, edgecolor="black", linewidth=0.6, hatch=h,
               error_kw={"elinewidth": 1.2, "ecolor": "black"})

    for i, (m, s, ns) in enumerate(zip(means, stds, success_counts)):
        txt = f"{m:.2f}" + (f"\n({ns}/{n_total})" if ns < n_total else "")
        ax.text(x[i], m + s + max(means) * 0.02, txt,
                ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Parameter group")
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
                           hatch="///", label=f"$n_s < {n_total}$")
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
    ax.set_xlabel("Ranking group (scene + method)", fontsize=10)
    ax.set_ylabel("Parameter group", fontsize=10)
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
    scene_name="", groups_cfg=None, grouped_df=None, group_params_columns=None,
):
    figures_dir  = output_dir / "figures"
    internal_dir = figures_dir / "internal"
    figures_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    if len(experiments) >= 2:
        _save(_build_comparison_grid(experiments, scene_name),
              internal_dir / f"{prefix}_comparison_grid.png")
    _save(_build_time_comparison(experiments, prefix),
          internal_dir / f"{prefix}_time_comparison.png")
    _save(_build_ranking_bar(ranked_df, prefix),
          internal_dir / f"{prefix}_ranking.png")

    if groups_cfg is not None and group_params_columns:
        save_grouped_bar(ranked_df, grouped_df, groups_cfg, group_params_columns,
                         output_dir, prefix, scene_name)
        save_grouped_heatmap(ranked_df, groups_cfg, group_params_columns,
                             output_dir, prefix, scene_name)
