"""Part 5. Factor attribution for MSCI Value and the multi-factor mix.

    python part5.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from part1 import ann_stats, load_factors, load_msci, window

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "exhibits" / "part5"
NAMES = ["Intercept", "RF", "Mkt-RF", "HML", "SMB"]
COMPONENTS = ["Value", "Min vol", "Equal weight", "Momentum"]

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
BLUE, ORANGE, GREEN, RED = "#4C78A8", "#F58518", "#54A24B", "#E45756"


def save_fig(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name)
    plt.close(fig)


def ols(y, x):
    n, k = x.shape
    beta = np.linalg.solve(x.T @ x, x.T @ y)
    resid = y - x @ beta
    sigma2 = float(resid @ resid) / (n - k)
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(x.T @ x)))
    r2 = 1.0 - float(resid @ resid) / float(((y - y.mean()) @ (y - y.mean())))
    return beta, se, beta / se, r2


def sample():
    msci = window(load_msci(), "1995-01", "2023-07")
    factors = window(load_factors(), "1995-01", "2023-07")
    y = msci["value"].to_numpy()
    x = np.column_stack([
        np.ones(len(y)),
        factors["RF"].to_numpy(),
        factors["Mkt-RF"].to_numpy(),
        factors["HML"].to_numpy(),
        factors["SMB"].to_numpy(),
    ])
    return msci, factors, y, x


def write_regression(y, beta, se, tstat, r2):
    lines = [
        "Exhibit 5B — MSCI USA Value on the Fama-French factors",
        "Monthly gross total return, Jan 1995–Jul 2023. OLS with an intercept. t-stats are not Newey-West.",
        "Slopes are unitless (return on return). The intercept is a monthly decimal return.",
        "",
        f"n = {len(y)}    R² = {r2:.3f}",
        f"{'term':<12}{'coef':>10}{'t':>8}",
    ]
    for name, estimate, stat in zip(NAMES, beta, tstat):
        lines.append(f"{name:<12}{estimate:10.3f}{stat:8.2f}")
    lines += [
        "",
        "Exhibit 5C — the intercept is the monthly average MSCI Value return not explained by RF, Mkt-RF, HML, and SMB.",
        f"Monthly intercept: {100 * beta[0]:.3f}%",
        f"× 12: {100 * 12 * beta[0]:.2f}%",
    ]
    (OUT / "5b_regression.txt").write_text("\n".join(lines) + "\n")
    return se


def write_replication(msci, factors, y, beta):
    replica = (
        beta[1] * factors["RF"].to_numpy()
        + beta[2] * factors["Mkt-RF"].to_numpy()
        + beta[3] * factors["HML"].to_numpy()
        + beta[4] * factors["SMB"].to_numpy()
    )
    corr = float(np.corrcoef(y, replica)[0, 1])
    rf = factors["RF"]
    rows = {
        "MSCI Value": ann_stats(msci["value"], rf),
        "Replica": ann_stats(pd.Series(replica, index=factors.index), rf),
    }
    lines = [
        "Exhibit 5D — MSCI USA Value and the factor replica",
        "Jan 1995–Jul 2023. The replica uses the 5B slopes on RF, Mkt-RF, HML, and SMB, and drops the intercept.",
        "Annualized return is 12 × the arithmetic monthly mean. Sharpe matches Part 1.",
        "Returns are gross of fees and trading costs.",
        "",
        f"Correlation of the replica with MSCI Value: {corr:.3f}",
        "",
        f"{'strategy':<16}{'ann_return':>12}{'ann_vol':>10}{'sharpe':>8}",
    ]
    for name, (ret, vol, sharpe) in rows.items():
        lines.append(f"{name:<16}{100 * ret:12.2f}{100 * vol:10.2f}{sharpe:8.2f}")
    (OUT / "5d_replication.txt").write_text("\n".join(lines) + "\n")

    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    ax.scatter(100 * y, 100 * replica, s=22, c=BLUE, alpha=0.55, zorder=2)
    lo = min(100 * y.min(), 100 * replica.min())
    hi = max(100 * y.max(), 100 * replica.max())
    pad = 0.06 * (hi - lo)
    ax.plot([lo, hi], [lo, hi], color=ORANGE, lw=1.8, zorder=4, label="Same return")
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("MSCI Value (% per month)")
    ax.set_ylabel("Factor replica (% per month)")
    ax.set_title(f"Value index and its factor replica (corr {corr:.2f})", pad=8)
    ax.legend(frameon=False, loc="upper left")
    save_fig(fig, "5d_replication.png")
    return replica


def active_returns(msci):
    usa = msci["usa"]
    parts = {
        "Value": msci["value"] - usa,
        "Min vol": msci["minvol"] - usa,
        "Equal weight": msci["ew"] - usa,
        "Momentum": msci["mom"] - usa,
    }
    parts["Multi-factor"] = msci[["value", "minvol", "ew", "mom"]].mean(axis=1) - usa
    return parts


def active_stats(series):
    excess = 12 * float(series.mean())
    te = float(series.std(ddof=1)) * np.sqrt(12)
    return excess, te, excess / te


def write_active(msci):
    active = active_returns(msci)
    order = ["Multi-factor", *COMPONENTS]
    lines = [
        "Exhibit 5E — active return versus MSCI USA",
        "Jan 1995–Jul 2023. Active return is the index minus MSCI USA.",
        "The multi-factor index is the equal-weighted average of Value, Min vol, Equal weight, and Momentum.",
        "Annualized excess return is 12 × the arithmetic monthly mean. Tracking error is monthly std × sqrt(12).",
        "Information ratio is annualized excess return divided by tracking error.",
        "",
        f"{'index':<16}{'ann_excess':>12}{'te':>10}{'ir':>8}",
    ]
    for name in order:
        excess, te, ratio = active_stats(active[name])
        lines.append(f"{name:<16}{100 * excess:12.2f}{100 * te:10.2f}{ratio:8.2f}")
    (OUT / "5e_active.txt").write_text("\n".join(lines) + "\n")
    return active


def write_variance(active):
    mix = active["Multi-factor"].to_numpy()
    covs = np.array([
        float(np.cov(mix, active[name].to_numpy(), ddof=1)[0, 1]) for name in COMPONENTS
    ])
    variance = float(np.var(mix, ddof=1))
    shares = covs / covs.sum()
    lines = [
        "Exhibit 5F — what drives multi-factor tracking error",
        "Active returns versus MSCI USA, Jan 1995–Jul 2023.",
        "The variance of the multi-factor active return equals the average of its covariances with the four component active returns.",
        "Share is that covariance divided by the sum of the four covariances.",
        "",
        f"Variance of multi-factor active return: {variance:.6e}",
        f"Average of the four covariances:       {float(covs.mean()):.6e}",
        "",
        f"{'component':<16}{'covariance':>14}{'share':>10}",
    ]
    for name, cov, share in zip(COMPONENTS, covs, shares):
        lines.append(f"{name:<16}{cov:14.6e}{100 * share:9.1f}%")
    (OUT / "5f_variance.txt").write_text("\n".join(lines) + "\n")

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    colors = [BLUE, GREEN, ORANGE, RED]
    ax.bar(COMPONENTS, 100 * shares, color=colors, zorder=3)
    ax.xaxis.grid(False)
    ax.set_ylabel("Share of active variance (%)")
    ax.set_title("Drivers of multi-factor tracking error")
    save_fig(fig, "5f_variance.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    msci, factors, y, x = sample()
    beta, se, tstat, r2 = ols(y, x)
    write_regression(y, beta, se, tstat, r2)
    write_replication(msci, factors, y, beta)
    write_variance(write_active(msci))


if __name__ == "__main__":
    main()
