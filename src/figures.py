"""
src/figures.py
--------------
Publication-quality figures for the NBV analysis pipeline.

Figure outputs
--------------
  figures/internal/
    {prefix}_comparison_grid.png   5-panel view-by-view comparison
    {prefix}_time_comparison.png   Bar chart of total computation time
    {prefix}_ranking.png           Horizontal bar of totalrank per experiment

  figures/
    {prefix}_grouped_bar.png       Mean totalrank per group with std error bars
    {prefix}_grouped_heatmap.png   Heatmap of totalrank: rows=groups, cols=sub-experiments
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from pathlib import Path


# ── Visual style ──────────────────────────────────────────────────────────────
COLORS  = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
LINES   = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "P"]

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
    "tri_imaged_pct",
    "cum_travelled_m",
    "cum_energy",
    "tri_quality",
    "total_time",
]

GRID_SUBTITLES = [
    "(a) % Retrieved",
    "(b) Accumulated distance",
    "(c) Accumulated energy",
    "(d) Mean quality",
    "(e) Total time",
]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _style(i: int) -> dict:
    return {
        "color":      COLORS[i % len(COLORS)],
        "linestyle":  LINES[i % len(LINES)],
        "marker":     MARKERS[i % len(MARKERS)],
        "linewidth":  1.4,
        "markersize": 4,
    }


def _plot_metric(ax, experiments: dict, metric: str,
                 title: str = None, show_legend: bool = True,
                 marker_every: int = 10) -> None:
    ylabel, _ = METRIC_CFG.get(metric, (metric.replace("_", " "), True))
    for i, (label, (_, df)) in enumerate(experiments.items()):
        ax.plot(df["view"], df[metric], markevery=marker_every,
                label=label, **_style(i))
    ax.set_xlabel("View number")
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.4)
    if show_legend:
        ax.legend(framealpha=0.8)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Figure -> {path}")


# ── Figure builders (return Figure, do not save) ──────────────────────────────

def _build_comparison_grid(experiments: dict, scene_name: str = "") -> plt.Figure:
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    axes = axes.flatten()
    for idx, (metric, subtitle) in enumerate(zip(GRID_METRICS, GRID_SUBTITLES)):
        _plot_metric(axes[idx], experiments, metric,
                     title=subtitle, show_legend=(idx == 0))
    axes[5].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].get_legend().remove()
    fig.legend(handles, labels, loc="lower right",
               bbox_to_anchor=(0.95, 0.08), framealpha=0.9, fontsize=9)
    if scene_name:
        fig.suptitle(f"{scene_name} -- experiment graphs", fontsize=12, y=1.01)
    fig.tight_layout()
    return fig


def _build_time_comparison(experiments: dict, prefix: str) -> plt.Figure:
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


def _build_ranking_bar(ranked_df: pd.DataFrame, prefix: str) -> plt.Figure:
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

def save_comparison_grid(experiments: dict, output_dir: Path,
                         prefix: str, scene_name: str = "") -> None:
    if len(experiments) >= 2:
        _save(_build_comparison_grid(experiments, scene_name),
              output_dir / "figures" / f"{prefix}_comparison_grid.png")


def save_time_comparison(experiments: dict, output_dir: Path,
                         prefix: str, title: str = "") -> None:
    _save(_build_time_comparison(experiments, prefix),
          output_dir / "figures" / f"{prefix}_time_comparison.png")


def save_ranking_bar(ranked_df: pd.DataFrame, output_dir: Path,
                     prefix: str, title: str = "") -> None:
    _save(_build_ranking_bar(ranked_df, prefix),
          output_dir / "figures" / f"{prefix}_ranking.png")


# ── Grouped figures (paper-quality) ──────────────────────────────────────────

def save_grouped_bar(
    ranked_df: pd.DataFrame,
    grouped_df: pd.DataFrame,
    groups_cfg: dict,
    group_params_columns: list,
    output_dir: Path,
    prefix: str,
    title: str = "",
) -> None:
    """
    Bar chart of mean totalrank per group with std error bars.
    Best group highlighted in red, others in blue.
    """
    if grouped_df is None or groups_cfg is None:
        return

    param_key, param_header = group_params_columns[0]

    labels, means, stds = [], [], []
    for gid, gdata in groups_cfg.items():
        sub = ranked_df[ranked_df["group_id"] == gid]["totalrank"]
        if sub.empty:
            continue
        labels.append(str(gdata[param_key]))
        means.append(sub.mean())
        stds.append(sub.std(ddof=1) if len(sub) > 1 else 0.0)

    if not means:
        return

    best_idx = int(np.argmin(means))
    colors   = ["#d62728" if i == best_idx else "#1f77b4"
                for i in range(len(labels))]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(max(5, len(labels) * 0.9), 4))
    bars = ax.bar(x, means, yerr=stds, capsize=5,
                  color=colors, edgecolor="black", linewidth=0.6,
                  error_kw={"elinewidth": 1.2, "ecolor": "black"})

    ax.bar_label(bars, fmt="%.2f", padding=6, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel(param_header.replace("$", "").replace("\\", ""))
    ax.set_ylabel("Mean total rank (lower = better)")
    ax.set_title(title or f"{prefix} -- grouped ranking by {param_key}")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.3)

    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#d62728", label="Best group"),
        Patch(color="#1f77b4", label="Other groups"),
    ], fontsize=8)

    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_grouped_bar.png")


def save_grouped_heatmap(
    ranked_df: pd.DataFrame,
    groups_cfg: dict,
    group_params_columns: list,
    output_dir: Path,
    prefix: str,
    title: str = "",
) -> None:
    """
    Heatmap of totalrank: rows = groups (alpha), columns = sub-experiments.
    Green = low rank (good), Red = high rank (bad).
    """
    if groups_cfg is None or "group_id" not in ranked_df.columns:
        return

    param_key, param_header = group_params_columns[0]

    sub_labels_set = sorted(
        set(eid.rsplit(".", 1)[-1] for eid in ranked_df["experiment_id"]),
        key=lambda x: int(x),
    )

    group_ids    = list(groups_cfg.keys())
    param_labels = [str(groups_cfg[g][param_key]) for g in group_ids]

    matrix = np.full((len(group_ids), len(sub_labels_set)), np.nan)
    for i, gid in enumerate(group_ids):
        sub_df = ranked_df[ranked_df["group_id"] == gid]
        for j, slabel in enumerate(sub_labels_set):
            match = sub_df[sub_df["experiment_id"].str.endswith(f".{slabel}")]
            if not match.empty:
                matrix[i, j] = match["totalrank"].values[0]

    sub_display = [f"Sub {s}" for s in sub_labels_set]

    cell_w = max(5, len(sub_labels_set) * 1.5)
    cell_h = max(3, len(group_ids) * 0.55)
    fig, ax = plt.subplots(figsize=(cell_w, cell_h))

    im = ax.imshow(matrix, aspect="auto", cmap="viridis_r")

    v_min = np.nanmin(matrix)
    v_max = np.nanmax(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val  = matrix[i, j]
            text = f"{val:.1f}" if not np.isnan(val) else "--"
            norm_val = (val - v_min) / (v_max - v_min + 1e-9)
            text_color = "black" if norm_val < 0.6 else "white"
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=8, color=text_color)

    ax.set_xticks(range(len(sub_display)))
    ax.set_xticklabels(sub_display, fontsize=9)
    ax.set_yticks(range(len(param_labels)))
    ax.set_yticklabels(param_labels, fontsize=9)
    ax.set_xlabel("Sub-experiment", fontsize=10)
    ax.set_ylabel(param_header.replace("$", "").replace("\\", ""), fontsize=10)
    ax.set_title(title or f"{prefix} -- totalrank heatmap", fontsize=11)

    plt.colorbar(im, ax=ax, label="totalrank (lower = better)", shrink=0.8)
    fig.tight_layout()
    _save(fig, output_dir / "figures" / f"{prefix}_grouped_heatmap.png")


# ── Main entry point ──────────────────────────────────────────────────────────

def save_all_figures(
    experiments: dict,
    ranked_df: pd.DataFrame,
    output_dir: Path,
    prefix: str,
    scene_name: str = "",
    groups_cfg: dict = None,
    grouped_df: pd.DataFrame = None,
    group_params_columns: list = None,
) -> None:
    """
    Generate all figures for a section.

    Internal figures (for review only) -> output/figures/internal/
    Paper figures                       -> output/figures/
    """
    figures_dir  = output_dir / "figures"
    internal_dir = figures_dir / "internal"
    figures_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    # ── Internal: per-view comparison grid ───────────────────────────────────
    if len(experiments) >= 2:
        _save(
            _build_comparison_grid(experiments, scene_name),
            internal_dir / f"{prefix}_comparison_grid.png",
        )

    # ── Internal: time comparison and full ranking bar ────────────────────────
    _save(
        _build_time_comparison(experiments, prefix),
        internal_dir / f"{prefix}_time_comparison.png",
    )
    _save(
        _build_ranking_bar(ranked_df, prefix),
        internal_dir / f"{prefix}_ranking.png",
    )

    # ── Paper figures: grouped bar + heatmap ─────────────────────────────────
    if groups_cfg is not None and group_params_columns:
        save_grouped_bar(
            ranked_df, grouped_df, groups_cfg, group_params_columns,
            output_dir, prefix, scene_name,
        )
        save_grouped_heatmap(
            ranked_df, groups_cfg, group_params_columns,
            output_dir, prefix, scene_name,
        )