```markdown
# NBV Experiment Analysis Pipeline

Automated processing pipeline for Next Best View (NBV) experiment log files.
Produces **LaTeX tables**, **publication-quality figures**, and **CSV exports**
directly from raw log files.

---

## Repository structure

```
NBV/
├── src/                        ← Master code — never edit these
│   ├── parser.py               ← Log file parser
│   ├── ranking.py              ← Ranking computations (thesis §6.5)
│   ├── tables.py               ← LaTeX table generator
│   └── figures.py              ← Matplotlib figure generator
│
├── run_section.py              ← Main entry point
│
├── area/                       ← One folder per thesis section
│   ├── config.py               ← The ONLY file you edit for this section
│   ├── logs/                   ← Drop your .log log files here
│   └── output/
│       ├── tables/             ← Generated .tex files
│       ├── figures/            ← Generated .png files (300 dpi)
│       └── csv/                ← Generated .csv files
│
├── motion/
│   ├── config.py
│   ├── logs/
│   └── output/
│
├── quality/        (same structure)
├── global_opt/     (same structure)
├── local_opt/      (same structure)
└── final/          (same structure)
```

---

## Setup

```bash
pip install pandas numpy matplotlib
```

---

## Daily workflow

```bash
# Check which log files are still missing before running
python run_section.py area --missing

# Run a single section
python run_section.py area

# Run all sections at once
python run_section.py --all
```

---

## Output files

For each section, the following files are generated inside `<section>/output/`:

| File | Description |
|------|-------------|
| `tables/<prefix>_params.tex`   | Variable parameters table (e.g. Table 6.7 in thesis) |
| `tables/<prefix>_results.tex`  | Results table — best value per column in **bold** |
| `tables/<prefix>_ranked.tex`   | Ranking scores table |
| `csv/<prefix>_summary.csv`     | All metrics + ranks in one file |
| `csv/<prefix>_<id>_per_view.csv` | Per-view data for each experiment |
| `figures/<prefix>_comparison_grid.png` | 5-panel view-by-view comparison (Figs 6.26/6.28/6.30 style) |
| `figures/<prefix>_time_comparison.png` | Bar chart of total computation time |
| `figures/<prefix>_ranking.png` | Horizontal bar chart of totalrank |

---

## Including tables in your LaTeX paper

```latex
\input{area/output/tables/area_params.tex}
\input{area/output/tables/area_results.tex}
\input{area/output/tables/area_ranked.tex}
```

---

## Configuring a section

Each section has one `config.py`. It has four parts:

### 1 — `SECTION_META`
Labels used in output filenames, LaTeX captions, and figure titles.
```python
SECTION_META = {
    "prefix":         "area",
    "caption_prefix": "Area factor",
}
```

### 2 — `EXPERIMENTS`
Maps each log filename (without `.log`) to its experiment ID and any extra
columns for the parameters table. The `id` key is mandatory and is the only
identifier shown in results and ranked tables.
```python
EXPERIMENTS = {
    "lab_anne_40": {"id": "1.02", "environment": "Laboratory",
                    "method": "SA", "alpha": 0.40},
    ...
}
```

### 3 — `PARAMS_COLUMNS`
Defines which extra keys from `EXPERIMENTS` appear in the parameters table,
in what order, and with what LaTeX header.
```python
PARAMS_COLUMNS = [
    ("environment", "Scene"),
    ("method",      "Method"),
    ("alpha",       r"$\alpha$"),
]
```

### 4 — `PCT_THRESHOLD` and ranking formulas
```python
PCT_THRESHOLD = 45.0   # set to None to include all experiments


TOTALRANK_FORMULA = lambda drank, erank, retrrank, qrank, timerank: (
    0.7 * (retrrank + drank + erank + qrank) + 0.3 * timerank
)

```
---

## Log file naming convention

The filename stem in `EXPERIMENTS` must match the `.log` file in `logs/`.
Recommended pattern:

```
{scene}_{method}_{variant}.log

Examples:
  lab_anne_40.log    → laboratory, simulated annealing, alpha=0.40
  lab_evol_34.log    → laboratory, (1+1)-ES, alpha=0.34
  stu_anne_L300.log  → study room, simulated annealing, L=300
```

---

## Ranking methodology

Implements thesis equations 6.2 – 6.5:

```
ranking_decr(v) = 100 × |v − v_min| / v_min     lower raw value = better (rank 0)
ranking_incr(v) = 100 × |v − v_max| / v_max     higher raw value = better (rank 0)

frank      = 0.5 × retrrank + 0.5 × (0.7 × drank + 0.3 × erank)   [default]
totalrank  = frank + timerank                                         [default]
```

Both formulas are overridable per section via `config.py`.
```