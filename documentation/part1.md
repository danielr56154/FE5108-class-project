# Part 1

Ken French and MSCI series in `data/ff_msci.xlsx`. French monthly blocks are in percent; the code divides by 100 before mixing them with MSCI returns. The annual blocks at the bottom of the French sheets are ignored. Values of −99.99 or −999 are treated as missing. MSCI columns are gross USD total-return index levels, stored as text with thousands separators. Returns are the month-to-month percent change. Dates are joined on year-month, because MSCI dates are the last business day, not always the calendar month-end. The first MSCI return is January 1995 and the last is July 2023.

On the beta sheet, Excel turned the middle decile labels into dates. The low-beta and high-beta columns are the ones still labeled `Lo 10` and `Hi 10`. The spread is value-weighted `Lo 10` minus `Hi 10`. The momentum spread is value-weighted `Hi PRIOR` minus `Lo PRIOR`. Equal-weighted French blocks are not used.

## 1A

`exhibits/1a_premia.txt`

Arithmetic mean of the monthly spread, in percent per month. A spread is not a funded portfolio, so the mean that the t-stat tests is the arithmetic mean.

$$
t = \frac{\bar r}{s / \sqrt{n}}
$$

No Newey-West adjustment. July–December 1926 is left out: the pre-publication window is January 1927–December 1992 (792 months). The post-publication window is January 1993–July 2023 (367 months). Factors are `Mkt-RF`, `SMB`, and `HML`.

## 1B — source notes, not the answer

Rewrite this in your own words for the report. Do not paste it.

Source: MSCI Momentum Indexes Methodology, December 2013, the PDF linked in the handout.

- Universe: the constituents of the parent index. For the series in this project that parent is MSCI USA Standard (large and mid cap).
- Signal: 12-month and 6-month local price return, skipping the most recent month, minus the local short rate (US: 3-month T-bill). Each leg is divided by the annualized standard deviation of three years of weekly local price returns. If the 12-month leg is missing, only the 6-month leg is used. If the 6-month leg is missing, the stock is not eligible.
- The two risk-adjusted legs are turned into z-scores, averaged 50/50, and that z-score is winsorized at ±3. The weight score is \(1+Z\) when \(Z>0\) and \(1/(1-Z)\) when \(Z<0\).
- Inclusion uses a fixed number of names with the highest positive raw (unwinsorized) momentum z-scores. Ties go to the larger parent-index weight. A buffer around that count keeps existing names so the index turns over less. The target count is checked each review so the index still covers enough of the parent’s market cap.
- Weight before the cap is parent market-cap weight times the momentum score, then rescaled to 100%. Market cap is in the weight, not only momentum. The report should give two reasons that helps and one reason it hurts.
- Scheduled rebalance: semi-annual, last business day of May and November.
- Extra rebalance: each month, if the change in the parent’s trailing 3-month annualized volatility is above the 95th percentile of historical volatility changes of MSCI World, the index is rebuilt using only 6-month momentum. The methodology’s reason is to limit drawdowns when volatility jumps.
- MSCI USA Momentum caps an issuer at 5%.

## 1C

`exhibits/1c_performance.txt` and `exhibits/1c_performance.png`

January 1995–July 2023. The multi-factor return in a month is the equal-weighted average of the value, minimum-volatility, equal-weighted, and momentum index returns. It does not include MSCI USA. The risk-free rate is Ken French `RF`.

Annualized average return is \(12\bar r\), the arithmetic mean, which is the average in the Sharpe definition below. It is not a compounded growth rate.

$$
\mathrm{Sharpe} = \frac{12\bar r - 12\bar r_f}{s\sqrt{12}}
$$

\(s\) is the standard deviation of the strategy’s own monthly returns. The chart is sorted by Sharpe. The multi-factor bar is orange.

## 1D

`exhibits/1d_corr.txt` and `exhibits/1d_corr.png`

Same months as 1C. Each MSCI spread is the smart-beta index minus MSCI USA. The four French spreads are `HML`, `SMB`, the value-weighted momentum decile spread, and the value-weighted low-minus-high beta spread.

## 1E

`exhibits/1e_momentum_vol.png` and `exhibits/1e_regimes.txt`

The volatility dated at month \(t\) is the annualized standard deviation of `Mkt-RF` over the 12 months ending in \(t\). The momentum month is paired with the volatility dated the previous month, so month \(t\)’s market return is not inside the signal. The paired sample is December 1995–July 2023.

High vol means lagged volatility at or above the sample median. The regression is ordinary least squares of the monthly momentum spread, in percent, on lagged annualized volatility, in percent. t-stats ignore autocorrelation.
