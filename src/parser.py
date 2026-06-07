"""
src/parser.py
-------------
Parses NBV experiment log files into structured pandas DataFrames.
Never edit this file to accommodate a specific experiment — use config.py instead.

Supports an optional trailing column "delta_f_accum" after "change".
Its presence is auto-detected per file by column count.
"""

import re
import pandas as pd
from pathlib import Path


DATA_COLUMNS_BASE = [
    "view", "iterations", "fitness",
    "vxl_occupied_m2", "occplane_m2", "vxl_quality",
    "tri_imaged_m2", "tri_imaged_pct", "tri_quality",
    "travelled_m", "energy", "total_time", "single_time",
    "backstep", "change",
]

DATA_COLUMNS_EXTENDED = DATA_COLUMNS_BASE + ["delta_f_accum"]

META_PATTERNS = {
    "scene":         r"#scene[.\s]+:\s*(.+)",
    "triangles":     r"#triangles[.\s]+:\s*(\d+)",
    "total_area_m2": r"#Total triangles' area[.\s]+:\s*([\d.]+)",
    "aperture":      r"#sensor aperture[.\s]+:\s*([\d.]+)\s*x\s*([\d.]+)",
    "range_image":   r"#range image size[.\s]+:\s*(\d+)\s*x\s*(\d+)",
    "blind_dist":    r"#sensor blind distances[.\s]+:\s*([\d.]+)\s*\.\.\s*([\d.]+)",
    "blind_angle":   r"#sensor blind angle[.\s]+:\s*([\d.]+)",
    "noise_std":     r"#sensor Gaussian noise std dev[.\s]+:\s*([\d.]+)",
    "views_number":  r"#views number[.\s]+:\s*(\d+)",
    "method":        r"#optimization method[.\s]+:\s*(.+)",
}

_N_BASE     = len(DATA_COLUMNS_BASE)
_N_EXTENDED = len(DATA_COLUMNS_EXTENDED)


def parse_log(filepath: str | Path) -> tuple[dict, pd.DataFrame]:
    """
    Parse a single NBV log file.

    Auto-detects whether the file has the optional delta_f_accum column
    (16 columns) or not (15 columns).

    Returns
    -------
    meta : dict
    df   : pd.DataFrame  with cumulative columns added:
             cum_travelled_m, cum_energy, and cum_delta_f (if present)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")

    meta, data_rows = {}, []
    has_delta_f = None   # determined from first valid data line

    with open(filepath) as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith("#"):
                for key, pattern in META_PATTERNS.items():
                    m = re.search(pattern, line)
                    if not m:
                        continue
                    if key == "aperture":
                        meta["aperture_h_deg"] = float(m.group(1))
                        meta["aperture_v_deg"]  = float(m.group(2))
                    elif key == "range_image":
                        meta["range_image_h"] = int(m.group(1))
                        meta["range_image_v"] = int(m.group(2))
                    elif key == "blind_dist":
                        meta["blind_dist_min_m"] = float(m.group(1))
                        meta["blind_dist_max_m"] = float(m.group(2))
                    elif key in ("triangles", "views_number"):
                        meta[key] = int(m.group(1))
                    elif key in ("total_area_m2", "blind_angle", "noise_std"):
                        meta[key] = float(m.group(1))
                    else:
                        meta[key] = m.group(1).strip()
                continue

            parts = line.split()
            n = len(parts)
            if n not in (_N_BASE, _N_EXTENDED):
                continue

            if has_delta_f is None:
                has_delta_f = (n == _N_EXTENDED)

            try:
                row = [
                    int(parts[0]), int(parts[1]), float(parts[2]),
                    float(parts[3]), float(parts[4]), float(parts[5]),
                    float(parts[6]), float(parts[7]), float(parts[8]),
                    float(parts[9]), float(parts[10]), float(parts[11]),
                    float(parts[12]), int(parts[13]), int(parts[14]),
                ]
                if has_delta_f:
                    row.append(float(parts[15]))
                data_rows.append(row)
            except ValueError:
                continue

    cols = DATA_COLUMNS_EXTENDED if has_delta_f else DATA_COLUMNS_BASE
    df = pd.DataFrame(data_rows, columns=cols)
    df["cum_travelled_m"] = df["travelled_m"].cumsum()
    df["cum_energy"]      = df["energy"].cumsum()
    if has_delta_f:
        df["cum_delta_f"] = df["delta_f_accum"].cumsum()

    return meta, df