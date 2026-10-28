"""Part 4. NVDL versus NVDA: daily leverage, drag, and compounding.

    python part4.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.stats import linregress, t

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "data" / "nvdl.xlsx"
OUT = ROOT / "exhibits" / "part4"

plt.rcParams.update({
    "figure.dpi": 140,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "axes.titlecolor": "#1F4E79",
    "text.color": "#222222",
    "axes.grid": True,
    "grid.color": "#E6E6E6",
    "grid.linewidth": 0.7,
    "axes.axisbelow": True,
    "font.size": 10,
})
BLUE, ORANGE = "#4C78A8", "#F58518"


def save_fig(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name)
    plt.close(fig)


def load_returns():
    wb = load_workbook(SRC, data_only=True)
    rows = []
    for row in wb.active.iter_rows(min_row=6, values_only=True):
        if row[0] is None:
            continue
        rows.append((pd.Timestamp(row[0]), float(row[1]), float(row[2])))
    wb.close()
    df = pd.DataFrame(rows, columns=["date", "nvda", "nvdl"]).sort_values("date").reset_index(drop=True)
    if df["date"].min() != pd.Timestamp("2024-02-01") or df["date"].max() != pd.Timestamp("2024-08-30"):
        raise RuntimeError(f"unexpected dates {df['date'].min().date()}–{df['date'].max().date()}")
    if len(df) != 147:
        raise RuntimeError(f"expected 147 days, got {len(df)}")
    return df


def risk_row(name, series):
    q = float(np.quantile(series, 0.05))
    tail = series[series <= q]
    return {
        "name": name,
        "std": float(series.std(ddof=1)),
        "var": -q,
        "cvar": -float(tail.mean()),
        "n_tail": int(len(tail)),
    }


def write_risk(df):
    rows = [risk_row("NVDA", df["nvda"]), risk_row("NVDL", df["nvdl"])]
    lines = [
        "Exhibit 4A — daily risk of NVDA and NVDL",
        "Daily total returns, 1 Feb 2024–30 Aug 2024, 147 days. Not annualized.",
        "VaR 95% is minus the 5th percentile of daily returns, so it is a loss.",
        "CVaR 95% is minus the average return on days at or below that percentile.",
        "",
        f"{'':<8}{'std':>10}{'var_95':>10}{'cvar_95':>10}{'tail_n':>8}",
    ]
    for row in rows:
        lines.append(
            f"{row['name']:<8}{100 * row['std']:10.2f}{100 * row['var']:10.2f}"
            f"{100 * row['cvar']:10.2f}{row['n_tail']:8d}"
        )
    (OUT / "4a_risk.txt").write_text("\n".join(lines) + "\n")


def fit_regression(df):
    fit = linregress(df["nvda"], df["nvdl"])
    dfree = len(df) - 2
    critical = float(t.ppf(0.975, dfree))
    return fit, dfree, critical


def write_regression(df, fit, dfree, critical):
    bands = {
        "a": (fit.intercept, fit.intercept_stderr),
        "b": (fit.slope, fit.stderr),
    }
    lines = [
        "Exhibit 4B — daily NVDL on daily NVDA, with an intercept",
        "1 Feb 2024–30 Aug 2024. Returns are decimals in the regression; coefficients below are in daily-return units.",
        "95% confidence intervals use a t critical value with n − 2 degrees of freedom.",
        "The factsheet objective, before fees and expenses, is a slope of 2 and no intercept.",
        "",
        f"n = {len(df)}    df = {dfree}    R = {fit.rvalue:.4f}",
        f"{'coef':<8}{'estimate':>12}{'std_err':>12}{'ci_low':>12}{'ci_high':>12}",
    ]
    for name, (estimate, error) in bands.items():
        low = estimate - critical * error
        high = estimate + critical * error
        lines.append(f"{name:<8}{estimate:12.5f}{error:12.5f}{low:12.5f}{high:12.5f}")
    (OUT / "4b_regression.txt").write_text("\n".join(lines) + "\n")

    x = np.linspace(df["nvda"].min(), df["nvda"].max(), 40)
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2))
    axes[0].scatter(100 * df["nvda"], 100 * df["nvdl"], s=18, c=BLUE, alpha=0.75, zorder=2)
    axes[0].plot(100 * x, 200 * x, color=ORANGE, lw=1.6, zorder=3, label="2× NVDA")
    axes[0].axhline(0, color="0.55", lw=0.5, zorder=1)
    axes[0].axvline(0, color="0.55", lw=0.5, zorder=1)
    axes[0].set_xlabel("NVDA (% per day)")
    axes[0].set_ylabel("NVDL (% per day)")
    axes[0].set_title(f"Daily returns, slope {fit.slope:.2f}", pad=8)
    axes[0].legend(frameon=False, loc="upper left")
    gap = 100 * (df["nvdl"] - 2 * df["nvda"])
    axes[1].axhline(0, color="0.55", lw=0.6, zorder=1)
    axes[1].axhline(100 * fit.intercept, color=ORANGE, lw=1.6, zorder=2, label="Average gap")
    axes[1].scatter(100 * df["nvda"], gap, s=18, c=BLUE, alpha=0.75, zorder=3)
    axes[1].set_xlabel("NVDA (% per day)")
    axes[1].set_ylabel("NVDL − 2× NVDA (percentage points)")
    axes[1].set_title("Gap versus a pure 2× day", pad=8)
    axes[1].legend(frameon=False, loc="upper right")
    save_fig(fig, "4b_fit.png")


def write_drag(fit):
    annual = 252 * fit.intercept
    lines = [
        "Exhibit 4C — annualized regression intercept versus the net expense ratio",
        "The intercept is the daily NVDL return when NVDA’s return is zero. Annualized figure = intercept × 252.",
        "Net expense ratio is the factsheet’s fee after the waiver in force through 31 Dec 2024.",
        "Gross expense ratio on the same factsheet is 1.57%; management fee is 0.99%.",
        "",
        f"Daily intercept: {100 * fit.intercept:.4f}%",
        f"× 252: {100 * annual:.2f}%",
        "Net expense ratio: 1.15%",
    ]
    (OUT / "4c_drag.txt").write_text("\n".join(lines) + "\n")


def compound(series):
    return float(np.prod(1.0 + series.to_numpy()) - 1.0)


def write_paths(df):
    rows = []
    for month, group in df.groupby(df["date"].dt.to_period("M")):
        rows.append((str(month), compound(group["nvda"]), compound(group["nvdl"])))
    rows.append(("Feb–Aug", compound(df["nvda"]), compound(df["nvdl"])))
    lines = [
        "Exhibit 4D — compounded total return, NVDA and NVDL",
        "Each month compounds that month’s daily total returns. Feb–Aug compounds the full sample, 1 Feb 2024–30 Aug 2024.",
        "The 2× NVDA column is twice the stock’s compounded return, the figure a constant 2× multiple would produce.",
        "Figures in percent.",
        "",
        f"{'window':<12}{'nvda':>10}{'nvdl':>10}{'2x_nvda':>10}",
    ]
    for label, nvda, nvdl in rows:
        lines.append(f"{label:<12}{100 * nvda:10.2f}{100 * nvdl:10.2f}{100 * 2 * nvda:10.2f}")
    (OUT / "4d_returns.txt").write_text("\n".join(lines) + "\n")

    months, full = rows[:-1], rows[-1]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2), gridspec_kw={"width_ratios": [4.2, 1]})
    for ax, block in ((axes[0], months), (axes[1], [full])):
        x = np.arange(len(block))
        heights = [100 * v for row in block for v in (row[1], row[2])]
        ax.bar(x - 0.18, [100 * row[1] for row in block], width=0.36, color=BLUE, label="NVDA", zorder=3)
        ax.bar(x + 0.18, [100 * row[2] for row in block], width=0.36, color=ORANGE, label="NVDL", zorder=3)
        ax.axhline(0, color="black", lw=0.6, zorder=2)
        ax.xaxis.grid(False)
        lo, hi = min(heights), max(heights)
        span = max(hi - min(lo, 0), 1)
        ax.set_ylim(min(lo, 0) - 0.06 * span, hi + 0.08 * span)
        tick = [pd.Period(row[0], freq="M").strftime("%b") if row[0][:2] == "20" else row[0] for row in block]
        ax.set_xticks(x, tick)
    axes[0].set_ylabel("Compounded return (%)")
    axes[0].set_title("Each month", pad=8)
    axes[1].set_title("Full sample", pad=8)
    axes[0].legend(frameon=False, loc="upper right")
    fig.suptitle("NVDA and NVDL, compounded beyond one day", color="#1F4E79")
    save_fig(fig, "4d_returns.png")


def write_twoday():
    nvda = 1.10 * 0.91 - 1.0
    nvdl = 1.20 * 0.82 - 1.0
    lines = [
        "Exhibit 4E — two-day path, ignoring daily drag",
        "NVDA is +10% on day 1 and −9% on day 2. NVDL is assumed to deliver exactly 2× each day’s stock return.",
        "",
        f"{'':<16}{'day 1':>10}{'day 2':>10}{'two-day':>10}",
        f"{'NVDA':<16}{10:10.1f}{-9:10.1f}{100 * nvda:10.1f}",
        f"{'NVDL':<16}{20:10.1f}{-18:10.1f}{100 * nvdl:10.1f}",
    ]
    (OUT / "4e_twoday.txt").write_text("\n".join(lines) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_returns()
    fit, dfree, critical = fit_regression(df)
    write_risk(df)
    write_regression(df, fit, dfree, critical)
    write_drag(fit)
    write_paths(df)
    write_twoday()


if __name__ == "__main__":
    main()
