# Part 2

Stock file: `data/stocks.csv`. Anonymized US names, November 1998–March 2019. `R1M_Usd` is a decimal (0.01 means 1%) and it is the return over the following month: the 31 December 1998 row is the January 1999 return. `Pb`, `Bv`, and `Mkt_Cap_3M_Usd` are percentiles on a 0.01–1.00 grid, where 1 is the highest value. `Pb` is price-to-book, not book-to-price. `Vol3Y_Usd` is unused.

Charts in 2A use the full file, so the thin months at the end are visible. Portfolio results use formation dates December 1998–November 2018. Those rows are the return months January 1999–December 2018 (240 months).

## 2A

- `exhibits/part2/2a_counts.png` — names per month. The count is about 880 at the start, about 1,190 for most of the file, then falls to about 550 in February and March 2019. Those two months are outside the performance window.
- `exhibits/part2/2a_returns.png` — pooled raw returns. The red line is the median, across months, of that month’s 99th percentile. The axis stops at 1.5 so the shape is visible; the title gives the maximum.
- Cleaning: inside each month, any return above that month’s 99th percentile is set to the 99th percentile. The left tail is left as reported. The handout names the 99% level, and a loss near −90% can be a real crash.
- `exhibits/part2/2a_coverage.png` — share of non-missing `R1M_Usd`. It is 1 in every month. A missing return would be dropped from that month’s portfolio before weights are scaled to 1. Filling it with zero would invent a flat month.
- `exhibits/part2/2a_pb.png` — `Pb` histogram. The 0.50 bin is the mode in every month. A percentile cannot show negative book equity, which Fama-French drop from HML.
- `exhibits/part2/2a_pb_check.txt` — within each month, Spearman correlation of `Pb` with (market-cap percentile − book percentile). The two percentiles are not divided. The median of those correlations is the sanity check that `Pb` behaves like a price-to-book ranking.

Book-to-price score used below:

$$
\mathrm{B/P} = 1 - \mathrm{Pb}
$$

A high score is a cheap stock.

## 2B

`exhibits/part2/2b_market.png` and `exhibits/part2/2b_market.txt`

Each formation month, weights are proportional to `Mkt_Cap_3M_Usd` and sum to 1. The portfolio return is the weighted average of the winsorized forward return. It is compared with the MSCI USA gross total return in the same return month. The proxy is a percentile, not a true capitalization weight, and the universe is not MSCI’s large and mid cap list. The correlation is the check that the file still tracks the US market.

## 2C

`exhibits/part2/2c_value.txt`

Three long-only, fully invested portfolios. More weight goes to higher book-to-price.

1. Equal-weight the top 20% by book-to-price. The count is \(\mathrm{round}(0.2N)\). Ties are broken by `stock_id`.
2. Weight every stock by its book-to-price score.
3. Weight every stock by book-to-price score times the market-cap percentile.

The return in the table is the compounded annualized return,

$$
\left(\prod_t (1+r_t)\right)^{12/T} - 1
$$

Volatility is the standard deviation of monthly returns times \(\sqrt{12}\). That standard deviation is around the arithmetic mean, not around the compounded return. Tracking error is the same formula applied to the portfolio minus the cap-weight proxy.

`n_names` and `max_w` are from the November 2018 formation. `n_names` counts positive weights. Use those two columns for the question about which book holds the fewest names and which has the largest single-stock weight.

## 2D

`exhibits/part2/2d_corr.txt`

Excess return is the portfolio minus the cap-weight proxy, over January 1999–December 2018. The fourth series is Ken French `HML` in those same months. HML is a value-weighted high-minus-low book-to-market spread, reformed each June, with negative book equity excluded. These three books are long-only monthly percentile tilts. The table is the comparison of how close each excess return is to HML.
