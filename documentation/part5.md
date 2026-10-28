# Part 5

Same Ken French factors and MSCI gross total-return indexes as Part 1, in `data/ff_msci.xlsx`. The window for every calculation is January 1995–July 2023. No new data file.

## 5A

No exhibit. Paraphrase the February 2021 MSCI Global Investable Market Value and Growth methodology. Do not paste it.

For the Standard index (large and mid cap, which is the USA Value series in this project), value uses three variables: book value to price, 12-month forward earnings to price, and dividend yield. Growth is a separate score, not “the rest of the market.” It uses long-term and short-term forward earnings-per-share growth, the current internal growth rate, long-term historical earnings-per-share growth, and long-term historical sales-per-share growth.

The list is not identical for every stock. Long-term forward earnings growth is left out of the small-cap style indexes. Long-term historical sales growth is not calculated for banks and diversified financials, aside from multi-sector holdings and financial exchanges. A stock can be partly in the value index and partly in the growth index. The two indexes together cover the parent, each targeting half of its free-float market cap.

HML, from Part 1, is one ratio: book equity to market equity. It is a value-weighted high-minus-low spread, reformed each June on NYSE breakpoints, and it drops negative book equity.

## 5B and 5C

`exhibits/part5/5b_regression.txt`

Monthly MSCI USA Value total return on an intercept, French RF, Mkt-RF, HML, and SMB. t-stats ignore autocorrelation.

$$
r_{\text{Value},t} = a + b_{\text{RF}}\text{RF}_t + b_{\text{M}}(\text{Mkt}-\text{RF})_t + b_{\text{HML}}\text{HML}_t + b_{\text{SMB}}\text{SMB}_t + e_t
$$

Question 5C is the intercept. The file also shows \(12a\). A positive intercept is monthly return the Fama–French mix does not explain.

## 5D

`exhibits/part5/5d_replication.txt` and `exhibits/part5/5d_replication.png`

The replica drops the intercept and keeps the four slopes as weights. Those weights are not rescaled to sum to 1.

$$
r_{\text{rep},t} = \hat b_{\text{RF}}\text{RF}_t + \hat b_{\text{M}}(\text{Mkt}-\text{RF})_t + \hat b_{\text{HML}}\text{HML}_t + \hat b_{\text{SMB}}\text{SMB}_t
$$

Annualized return, volatility, and Sharpe use the Part 1 definitions. Both series are gross of fees and trading costs. The write-up should give one to three reasons that comparison is not enough to choose between them. The factor portfolios are not a traded fund, the index fund has a fee, and the spreads can be costly to implement.

## 5E

`exhibits/part5/5e_active.txt`

Active return is the index minus MSCI USA, for the multi-factor index and for each of the four components. The multi-factor return is the equal-weighted average from Part 1.

Annualized excess return is \(12\) times the arithmetic monthly mean of that active return. Tracking error is the monthly standard deviation times \(\sqrt{12}\). The information ratio is the first divided by the second.

## 5F

`exhibits/part5/5f_variance.txt` and `exhibits/part5/5f_variance.png`

\(a_{\text{mf}}\) is the average of the four component active returns, so

$$
\mathrm{Var}(a_{\text{mf}}) = \frac{1}{4}\sum_i \mathrm{Cov}(a_{\text{mf}}, a_i).
$$

The file checks that identity. The share of component \(i\) is its covariance divided by the sum of the four covariances. The bar chart is those shares.

The write-up takes the largest share and says whether that factor is better held on its own or only inside the benchmark-relative mix, using limits to arbitrage.
