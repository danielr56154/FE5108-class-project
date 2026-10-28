# Part 3

`data/industries.xlsx`, the value-weighted monthly total-return block only. 49 industries, January 1995–July 2023. French reports percent; the code divides by 100. A value of −99.99 or −999 would be missing. The count of missing cells in this window is written at the top of `exhibits/part3/3b_c_d.txt`. MSCI USA levels, used for the wealth chart, come from `data/ff_msci.xlsx`.

The December 2004 books use the covariance of January 1995–December 2004 (120 months). The December 2015 book uses January 2006–December 2015. Covariance is the sample covariance (divisor \(T-1\)).

## 3A

`exhibits/part3/3a_weights.xlsx` and `exhibits/part3/3a_weights.csv`

Three fully invested portfolios. The workbook colors the top 5 weights green and the bottom 5 red inside each column. The csv has the same weights and no color.

Minimum variance with shorts allowed:

$$
w = \frac{\Sigma^{-1} 1}{1'\Sigma^{-1} 1}
$$

Minimum variance, long only:

$$
\min_w \; w'\Sigma w \quad \text{subject to} \quad 1'w = 1,\; w \ge 0
$$

Solved with SLSQP in scipy. The objective is convex, so the constraint \(w \ge 0\) is the only thing that separates it from the closed form.

Inverse volatility, with \(\sigma_i\) the seed-window standard deviation of industry \(i\):

$$
w_i \propto 1/\sigma_i, \qquad \sum_i w_i = 1
$$

## 3B and 3C

`exhibits/part3/3b_c_d.txt`

Realized volatility is the standard deviation of the monthly portfolio return \(w'r_t\) over the stated window, times \(\sqrt{12}\), in percent. In-sample is January 1995–December 2004 with the December 2004 weights. Out-of-sample is January 2005–July 2023 with those same weights held fixed.

## 3D

Same file, last block. Both long-only minimum-variance books are evaluated on January 2016–July 2023. The December 2004 book is not judged on its full out-of-sample life in this comparison. The two windows match.

## 3E

`exhibits/part3/3e_wealth.png`

\$1 at 31 December 2004 in the December 2004 long-only book, then the monthly industry returns through July 2023. MSCI USA is the index level divided by its December 2004 level. The y-axis is log base 2. Shaded regions are September 2008–February 2009 and February–March 2020.

`exhibits/part3/3e_crises.txt`

For each shaded window, the ten industries with the highest compounded total return. The ranking is the industry’s own return, not the portfolio’s holding.
