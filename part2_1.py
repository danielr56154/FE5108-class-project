"""Part 2 (revised). Cleaning, cap-weight proxy, three book-to-price portfolios, factor comparison.

    python part2_1.py

Differences from part2.py: two-sided 99% winsorization (0.5% in each tail) as the main case with
the other definitions shown side by side, value portfolios that exclude Pb = 0.50 rows (compared
with keeping them), a fuller 2B comparison with MSCI USA, holdings and max weight over the whole
sample, arithmetic and compounded returns, and a written 2D answer.
Writes to exhibits/part2_1 so the part2.py exhibits are left alone.
"""

from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
STOCKS = ROOT / "data" / "stocks.csv"
FF = ROOT / "data" / "ff_msci.xlsx"
OUT = ROOT / "exhibits" / "part2_1"
FORM_START = pd.Period("1998-12", freq="M")
FORM_END = pd.Period("2018-11", freq="M")
TAIL = 0.005
MAIN = "two"
MODES = {
    "two": "Two-sided 0.5% / 99.5%",
    "upper": "Upper 99% only",
    "none": "No winsorization",
}
KINDS = {
    "mkt": "Cap-weight proxy",
    "ew": "EW top 20% B/P",
    "score": "B/P score",
    "score_cap": "B/P score x cap",
}

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


def month_stamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return pd.Period(pd.Timestamp(value), freq="M")
    except (ValueError, TypeError):
        return None


def as_period(value):
    if value is None or isinstance(value, datetime):
        return None
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    if len(text) == 6 and text.isdigit():
        return pd.Period(year=int(text[:4]), month=int(text[4:]), freq="M")
    return None


def save_fig(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name)
    plt.close(fig)


def write(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_hml():
    wb = load_workbook(FF, read_only=True, data_only=True)
    rows = list(wb["FF - 3 factor returns"].iter_rows(values_only=True))
    wb.close()
    header = next(i for i, row in enumerate(rows) if row and str(row[1]).strip() == "Mkt-RF")
    hml_at = next(i for i, cell in enumerate(rows[header]) if cell is not None and str(cell).strip() == "HML")
    values = {}
    for row in rows[header + 1:]:
        period = as_period(row[0])
        if period is None:
            break
        values[period] = float(row[hml_at]) / 100.0
    return pd.Series(values).sort_index()


def load_usa():
    wb = load_workbook(FF, read_only=True, data_only=True)
    rows = list(wb["MSCI - factor totret index"].iter_rows(values_only=True))
    wb.close()
    header_at = next(i for i, row in enumerate(rows) if row and str(row[0]).strip() == "Date")
    usa_at = next(i for i, cell in enumerate(rows[header_at]) if cell and "USA" in str(cell).upper() and "VALUE" not in str(cell).upper())
    levels = {}
    for row in rows[header_at + 1:]:
        period = month_stamp(row[0] if row else None)
        if period is None:
            if levels:
                break
            continue
        levels[period] = float(str(row[usa_at]).replace(",", ""))
    return pd.Series(levels).sort_index().pct_change().dropna()


def load_stocks():
    df = pd.read_csv(STOCKS, parse_dates=["date"])
    df["form"] = df["date"].dt.to_period("M")
    df["bp"] = 1.0 - df["Pb"]
    grouped = df.groupby("form")["R1M_Usd"]
    df["lo"] = grouped.transform(lambda s: s.quantile(TAIL))
    df["hi"] = grouped.transform(lambda s: s.quantile(1.0 - TAIL))
    df["hi99"] = grouped.transform(lambda s: s.quantile(0.99))
    df["r_two"] = df["R1M_Usd"].clip(lower=df["lo"], upper=df["hi"])
    df["r_upper"] = df["R1M_Usd"].clip(upper=df["hi99"])
    df["r_none"] = df["R1M_Usd"]
    return df


def write_cleaning(df):
    counts = df.groupby("form").size()
    coverage = df.groupby("form")["R1M_Usd"].apply(lambda s: s.notna().mean())
    months = counts.index.to_timestamp("M")
    raw = df["R1M_Usd"]
    cut_lo = df.groupby("form")["lo"].first()
    cut_hi = df.groupby("form")["hi"].first()

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(months, counts.to_numpy(), color=BLUE, lw=1.4)
    ax.set_ylabel("Number of stocks")
    ax.set_title("Stocks in the file each month")
    save_fig(fig, "2a_counts.png")

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.hist(raw[(raw >= -1.0) & (raw <= 1.5)], bins=60, color=BLUE, edgecolor="white", linewidth=0.3)
    ax.axvline(cut_lo.median(), color=ORANGE, lw=1.4, zorder=3)
    ax.axvline(cut_hi.median(), color=ORANGE, lw=1.4, zorder=3)
    ax.set_xlim(-1.0, 1.5)
    ax.set_xlabel("Forward one-month return")
    ax.set_ylabel("Stock-months")
    n_above = int((raw > 1.5).sum())
    ax.set_title(f"Return distribution ({n_above} stock-months above 1.5; max {raw.max():.2f}, min {raw.min():.2f})")
    save_fig(fig, "2a_returns.png")

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(months, coverage.to_numpy(), color=BLUE, lw=1.4)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Share non-missing")
    ax.set_title("Return coverage each month")
    save_fig(fig, "2a_coverage.png")

    at_half = np.isclose(df["Pb"], 0.5)
    # Full histogram so the 0.50 spike is visible; the 0.50 bin is highlighted in orange.
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    _, edges, patches = ax.hist(df["Pb"], bins=np.arange(0.005, 1.015, 0.01), color=BLUE, edgecolor="white", linewidth=0.2)
    for patch, left in zip(patches, edges[:-1]):
        if left < 0.5 < left + 0.01:
            patch.set_facecolor(ORANGE)
    n_half = int(at_half.sum())
    ax.annotate(f"Pb = 0.50: {n_half:,} stock-months", xy=(0.5, n_half), xytext=(0.62, 0.92 * n_half),
                color=ORANGE, fontsize=9, arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.0))
    ax.set_xlabel("Price-to-book percentile (1 = highest P/B)")
    ax.set_ylabel("Stock-months")
    ax.set_title(f"Standardized price-to-book ({100 * at_half.mean():.1f}% of rows sit exactly at 0.50)")
    save_fig(fig, "2a_pb.png")

    # Pb against market-cap and book percentiles, month by month
    plain, within = [], []
    for _, g in df.groupby("form"):
        plain.append(g["Pb"].rank().corr((g["Mkt_Cap_3M_Usd"] - g["Bv"]).rank()))
        bucket = pd.qcut(g["Bv"].rank(method="first"), 5, labels=False)
        within.append(np.nanmean([
            g.loc[bucket == q, "Pb"].rank().corr(g.loc[bucket == q, "Mkt_Cap_3M_Usd"].rank())
            for q in range(5)
        ]))
    plain, within = pd.Series(plain), pd.Series(within)
    half_by_month = pd.Series(at_half, index=df.index).groupby(df["form"]).mean()
    write("2a_pb_check.txt", [
        "Exhibit 2A — does the price-to-book percentile behave like market value / book?",
        "Pb, Bv and Mkt_Cap_3M_Usd are percentile ranks, so they cannot be divided to rebuild P/B.",
        "The check is on ordering and sign, month by month. Negative book equity cannot be seen in a percentile.",
        f"Sample: {df['form'].min()} to {df['form'].max()}, {df['form'].nunique()} months, {df['stock_id'].nunique()} stocks.",
        "",
        "(1) Spearman of Pb with (market-cap percentile − book percentile). Positive is the expected sign.",
        f"    Median across months: {plain.median():.3f}    Share of months positive: {float((plain > 0).mean()):.3f}",
        "(2) Within book-percentile quintiles, Spearman of Pb with market-cap percentile. Positive is the expected sign.",
        f"    Median across months: {within.median():.3f}    Share of months positive: {float((within > 0).mean()):.3f}",
        "(3) Rows with Pb exactly 0.50, which is the mode of the histogram and may be a filled value.",
        f"    Share of all rows: {100 * at_half.mean():.1f}%    Range across months: {100 * half_by_month.min():.1f}% to {100 * half_by_month.max():.1f}%",
        f"    Rows with Pb at 0.50 and Bv at 0.50 too: {100 * (at_half & np.isclose(df['Bv'], 0.5)).mean():.1f}%",
    ])

    write("2a_winsor.txt", [
        "Exhibit 2A — winsorization of the forward one-month return",
        "Each month, returns are clipped at that month's percentiles. Missing returns are never filled with zero.",
        f"Missing returns: {int(raw.isna().sum())} of {len(raw)} rows (lowest monthly coverage {coverage.min():.3f}).",
        f"Raw min {raw.min():.3f}, raw max {raw.max():.3f}, raw median {raw.median():.4f}.",
        "",
        f"{'definition':<26}{'rows clipped low':>18}{'rows clipped high':>19}{'min after':>11}{'max after':>11}",
        f"{MODES['two']:<26}{int((raw < df['lo']).sum()):18d}{int((raw > df['hi']).sum()):19d}{df['r_two'].min():11.3f}{df['r_two'].max():11.3f}",
        f"{MODES['upper']:<26}{0:18d}{int((raw > df['hi99']).sum()):19d}{df['r_upper'].min():11.3f}{df['r_upper'].max():11.3f}",
        f"{MODES['none']:<26}{0:18d}{0:19d}{raw.min():11.3f}{raw.max():11.3f}",
    ])


def portfolio(g, kind, rcol, exclude):
    g = g.dropna(subset=[rcol, "bp", "Mkt_Cap_3M_Usd"])
    if exclude and kind != "mkt":
        g = g[~np.isclose(g["Pb"], 0.5)]
    n = len(g)
    if kind == "mkt":
        raw = g["Mkt_Cap_3M_Usd"].to_numpy()
    elif kind == "ew":
        k = max(1, int(np.floor(n * 0.2 + 0.5)))
        order = np.lexsort((g["stock_id"].to_numpy(), -g["bp"].to_numpy()))
        raw = np.zeros(n)
        raw[order[:k]] = 1.0
    elif kind == "score":
        raw = g["bp"].to_numpy()
    else:
        raw = (g["bp"] * g["Mkt_Cap_3M_Usd"]).to_numpy()
    weights = raw / raw.sum()
    return float(weights @ g[rcol].to_numpy()), int((weights > 0).sum()), float(weights.max())


def run_portfolios(df, mode, exclude=True):
    rcol = f"r_{mode}"
    use = df[df["form"].between(FORM_START, FORM_END)]
    ret = {name: {} for name in KINDS}
    held = {name: {} for name in KINDS}
    maxw = {name: {} for name in KINDS}
    for form, g in use.groupby("form"):
        for name in KINDS:
            r, k, w = portfolio(g, name, rcol, exclude)
            ret[name][form + 1] = r
            held[name][form + 1] = k
            maxw[name][form + 1] = w
    returns = pd.DataFrame(ret).sort_index()
    expect = (pd.Period("2018-12") - pd.Period("1999-01")).n + 1
    if len(returns) != expect or returns.index.min() != pd.Period("1999-01") or returns.index.max() != pd.Period("2018-12"):
        raise RuntimeError(f"portfolio window {returns.index.min()}–{returns.index.max()} n={len(returns)}")
    return returns, pd.DataFrame(held).sort_index(), pd.DataFrame(maxw).sort_index()


def ann_geo(series):
    return float(np.prod(1.0 + series.to_numpy()) ** (12.0 / len(series)) - 1.0)


def ann_arith(series):
    return float(12 * series.mean())


def ann_vol(series):
    return float(series.std(ddof=1) * np.sqrt(12))


def write_market(returns, usa):
    mkt = returns["mkt"]
    corr = float(mkt.corr(usa))
    te = ann_vol(mkt - usa)
    stats = {"Cap-weight proxy": mkt, "MSCI USA": usa}
    write("2b_market.txt", [
        "Exhibit 2B — cap-weight proxy versus MSCI USA",
        "Proxy weights are proportional to the standardized market-cap percentile, so this is an approximate cap-weight index.",
        "MSCI USA is the gross large+mid-cap total-return index. Both series are monthly returns, Jan 1999–Dec 2018.",
        f"Proxy returns use the {MODES[MAIN].lower()} winsorization. Compounded = geometric annualized; arithmetic = 12 × monthly mean.",
        "",
        f"{'':<20}{'compounded':>12}{'arithmetic':>12}{'ann_vol':>10}",
        *[f"{name:<20}{100 * ann_geo(s):12.2f}{100 * ann_arith(s):12.2f}{100 * ann_vol(s):10.2f}" for name, s in stats.items()],
        "",
        f"Months: {len(mkt)}",
        f"Correlation of monthly returns: {corr:.3f}",
        f"Tracking error of the proxy versus MSCI USA: {100 * te:.2f}%",
    ])

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]
    months = mkt.index.to_timestamp("M")
    ax.plot(months, (1 + usa).cumprod().to_numpy(), color=BLUE, lw=1.8, label="MSCI USA")
    ax.plot(months, (1 + mkt).cumprod().to_numpy(), color=ORANGE, lw=1.8, label="Cap-weight proxy")
    ax.set_ylabel("Growth of 1 at end of Dec 1998")
    ax.set_title("Cumulative return")
    ax.legend(frameon=False, loc="upper left")
    ax = axes[1]
    ax.scatter(100 * usa, 100 * mkt, s=20, c=BLUE, alpha=0.55, zorder=2)
    lo = min(100 * usa.min(), 100 * mkt.min())
    hi = max(100 * usa.max(), 100 * mkt.max())
    pad = 0.06 * (hi - lo)
    ax.plot([lo, hi], [lo, hi], color=ORANGE, lw=1.8, zorder=4, label="Same as MSCI USA")
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("MSCI USA (% per month)")
    ax.set_ylabel("Cap-weight proxy (% per month)")
    ax.set_title(f"Monthly returns (corr {corr:.2f})")
    ax.legend(frameon=False, loc="upper left")
    save_fig(fig, "2b_market.png")


def write_value(returns, held, maxw):
    lines = [
        "Exhibit 2C — book-to-price portfolios, formation Dec 1998–Nov 2018 (return months Jan 1999–Dec 2018, 240 months)",
        f"Long-only, fully invested. Book-to-price score = 1 − price-to-book percentile. Returns use {MODES[MAIN].lower()} winsorization.",
        "Value portfolios exclude rows with Pb exactly 0.50 (likely filled for negative book equity) and rescale weights; the cap-weight proxy keeps them.",
        "compounded = (prod(1+r))^(12/T) − 1. arithmetic = 12 × monthly mean. ann_vol and TE = monthly std × sqrt(12).",
        "TE is versus the cap-weight proxy. Returns, vol, TE and max_w are in percent. n_names counts positive weights.",
        "avg / max are over the 240 formation dates; last is the Nov 2018 formation.",
        "",
        f"{'strategy':<18}{'compounded':>11}{'arithmetic':>11}{'ann_vol':>9}{'te':>7}{'n_avg':>8}{'n_min':>7}{'n_last':>8}{'maxw_avg':>10}{'maxw_max':>10}{'maxw_last':>10}",
    ]
    for key, label in KINDS.items():
        excess = returns[key] - returns["mkt"]
        lines.append(
            f"{label:<18}{100 * ann_geo(returns[key]):11.2f}{100 * ann_arith(returns[key]):11.2f}"
            f"{100 * ann_vol(returns[key]):9.2f}{100 * ann_vol(excess):7.2f}"
            f"{held[key].mean():8.0f}{held[key].min():7d}{held[key].iloc[-1]:8d}"
            f"{100 * maxw[key].mean():10.2f}{100 * maxw[key].max():10.2f}{100 * maxw[key].iloc[-1]:10.2f}"
        )
    write("2c_value.txt", lines)

    months = returns.index.to_timestamp("M")
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    colors = {"mkt": "#333333", "ew": ORANGE, "score": BLUE, "score_cap": "#54A24B"}
    for key, label in KINDS.items():
        ax.plot(months, (1 + returns[key]).cumprod().to_numpy(), color=colors[key], lw=1.6, label=label)
    ax.set_yscale("log")
    ax.set_ylabel("Growth of 1 at end of Dec 1998 (log)")
    ax.set_title("Value portfolios versus the cap-weight proxy")
    ax.legend(frameon=False, loc="upper left")
    save_fig(fig, "2c_cumulative.png")


def write_sensitivity(results):
    lines = [
        "Exhibit 2C — sensitivity to the winsorization definition",
        "Same portfolios and window as 2C (Pb = 0.50 rows excluded from the value portfolios). Compounded return and tracking error in percent versus the proxy built under the same definition.",
        "",
        f"{'definition':<26}{'strategy':<18}{'compounded':>11}{'ann_vol':>9}{'te':>7}",
    ]
    for mode, returns in results.items():
        for key, label in KINDS.items():
            excess = returns[key] - returns["mkt"]
            lines.append(
                f"{MODES[mode]:<26}{label:<18}{100 * ann_geo(returns[key]):11.2f}"
                f"{100 * ann_vol(returns[key]):9.2f}{100 * ann_vol(excess):7.2f}"
            )
        lines.append("")
    write("2c_sensitivity.txt", lines)


def write_exclusion(excluded, kept, hml):
    """excluded: results with Pb = 0.50 rows dropped from the value portfolios (main case).
    kept: results with those rows kept. Each is (returns, held, maxw)."""
    lines = [
        "Exhibit 2C — excluding versus keeping rows with Pb exactly 0.50 in the value portfolios",
        f"Winsorization: {MODES[MAIN].lower()}. The cap-weight proxy is the same in both cases. Percent except counts and correlation.",
        "n_last and maxw_last are at the Nov 2018 formation. corr_hml is the excess-return correlation with HML.",
        "",
        f"{'treatment':<10}{'strategy':<18}{'compounded':>11}{'ann_vol':>9}{'te':>7}{'n_last':>8}{'maxw_last':>10}{'corr_hml':>10}",
    ]
    hml = hml.reindex(excluded[0].index)
    for label, (returns, held, maxw) in (("excluded", excluded), ("kept", kept)):
        for key in ("ew", "score", "score_cap"):
            excess = returns[key] - returns["mkt"]
            lines.append(
                f"{label:<10}{KINDS[key]:<18}{100 * ann_geo(returns[key]):11.2f}{100 * ann_vol(returns[key]):9.2f}"
                f"{100 * ann_vol(excess):7.2f}{held[key].iloc[-1]:8d}{100 * maxw[key].iloc[-1]:10.2f}{excess.corr(hml):10.2f}"
            )
        lines.append("")
    write("2c_exclusion.txt", lines)


def write_factor(returns, hml):
    hml = hml.reindex(returns.index)
    if hml.isna().any():
        raise RuntimeError("HML does not cover 1999–2018")
    excess = pd.DataFrame({
        "EW top 20%": returns["ew"] - returns["mkt"],
        "B/P score": returns["score"] - returns["mkt"],
        "Score x cap": returns["score_cap"] - returns["mkt"],
        "HML": hml,
    })
    c = excess.corr()
    closest = c.loc[["EW top 20%", "B/P score", "Score x cap"], "HML"].idxmax()
    lines = [
        "Exhibit 2D — tracking error and correlation of value-portfolio excess returns",
        "Excess return is the portfolio minus the cap-weight proxy. HML is the Ken French value spread, Jan 1999–Dec 2018.",
        "",
        f"{'':<14}" + "".join(f"{name:>14}" for name in c.columns),
    ]
    for name, row in c.iterrows():
        lines.append(f"{name:<14}" + "".join(f"{value:14.2f}" for value in row))
    lines += ["", "Annualized tracking error versus the proxy (percent):"]
    for key in ("ew", "score", "score_cap"):
        lines.append(f"  {KINDS[key]:<18}{100 * ann_vol(returns[key] - returns['mkt']):8.2f}")
    lines += [
        "",
        f"Closest to HML: {closest} (correlation {c.loc[closest, 'HML']:.2f}).",
        "HML is a long-short spread of value-weighted small and big portfolios sorted on book-to-market, reformed each June.",
        "The three portfolios here are long-only, reformed monthly, and tilt on a percentile rank rather than on a size-neutral sort.",
    ]
    write("2d_corr.txt", lines)

    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    image = ax.imshow(c.to_numpy(), cmap="Blues", vmin=0, vmax=1, aspect="equal")
    ax.set_xticks(range(c.shape[1]), c.columns, rotation=20, ha="right")
    ax.set_yticks(range(c.shape[0]), c.index)
    ax.grid(False)
    for i in range(c.shape[0]):
        for j in range(c.shape[1]):
            ax.text(j, i, f"{c.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9, color="#222222")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Excess-return correlations, Jan 1999–Dec 2018")
    save_fig(fig, "2d_corr.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_stocks()
    write_cleaning(df)
    results = {}
    for mode in MODES:
        returns, held, maxw = run_portfolios(df, mode)
        results[mode] = returns
        if mode == MAIN:
            main_held, main_maxw = held, maxw
    returns = results[MAIN]
    usa = load_usa().reindex(returns.index)
    if usa.isna().any():
        raise RuntimeError("MSCI USA does not cover 1999–2018")
    write_market(returns, usa)
    write_value(returns, main_held, main_maxw)
    write_sensitivity(results)
    hml = load_hml()
    write_exclusion((returns, main_held, main_maxw), run_portfolios(df, MAIN, exclude=False), hml)
    write_factor(returns, hml)


if __name__ == "__main__":
    main()
