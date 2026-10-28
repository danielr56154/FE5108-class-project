# Part 4

`data/nvdl.xlsx` holds daily total returns of NVDA and of the GraniteShares 2x Long NVDA ETF (ticker NVDL). The returns are decimals. The file is newest-first; the script sorts it. The sample is 147 trading days, 1 February 2024–30 August 2024. The factsheet is `data/nvdl_factsheet.pdf`, dated as of 30 June 2024.

Before 22 January 2024 the fund targeted 1.5 times NVDA’s daily return. That date is before this sample, so the stated objective throughout these days is 2 times the daily move, before fees and expenses.

## 4A

`exhibits/part4/4a_risk.txt`

Not annualized. For each series, the standard deviation is the sample standard deviation of daily returns (divisor \(n-1\)).

The 95% VaR is minus the 5th percentile of daily returns, so the number is a loss. The 95% CVaR is minus the average return on the days at or below that percentile.

## 4B

`exhibits/part4/4b_regression.txt` and `exhibits/part4/4b_fit.png`

$$
r_{\text{NVDL},t} = a + b\, r_{\text{NVDA},t} + e_t
$$

Confidence intervals are 95%, using a \(t\) critical value with \(n-2\) degrees of freedom. The factsheet’s daily objective, before fees, is \(b = 2\) and \(a = 0\). The dashed line on the chart is \(y = 2x\).

## 4C

`exhibits/part4/4c_drag.txt`

Annualized intercept \(= 252a\). The factsheet’s net expense ratio, after the waiver in force through 31 December 2024, is 1.15% a year. The gross ratio on the same page is 1.57%, and the management fee is 0.99%.

The write-up should name two costs that can sit in the intercept besides that expense ratio. The fund borrows to maintain the leverage, and it trades NVDA each day to reset the exposure.

## 4D

`exhibits/part4/4d_returns.txt` and `exhibits/part4/4d_returns.png`

A month’s total return compounds that month’s daily returns. The full-sample row compounds 1 February through 30 August. The \(2\times\) column is twice the stock’s compounded return. It is there so the cumulative gap is visible. It is not a third investment.

## 4E

`exhibits/part4/4e_twoday.txt`

No data. NVDA is \(+10\%\) then \(-9\%\). NVDL is taken as exactly \(2\times\) each day, with no drag.

$$
1.10 \times 0.91 - 1 = +0.1\%, \qquad 1.20 \times 0.82 - 1 = -1.6\%
$$

## 4F

No exhibit. The write-up answers two investors. A one-day bullish trade is the use the factsheet describes. A one-year hold through volatile prices is where the daily reset, described under 4D and 4E, works against the holder.
