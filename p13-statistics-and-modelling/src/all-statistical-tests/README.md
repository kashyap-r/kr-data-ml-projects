# Financial Services Statistical Testing Lab

An **offline, reproducible Python practice environment** using a **fictional wealth-management and brokerage firm**. No sensitive client information, live API, paid dataset, or login is required. Data are **synthetic**, generated with fixed seed `20261113`: values and observed relationships are deliberately simulated, **not** real-world estimates, investment results, or evidence of business impact.

## 1. Getting started (macOS / Linux / Windows)

```bash
# Unzip archive; cd into financial_statistics_lab
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_tests.py --family all
python run_tests.py --family means
jupyter notebook notebooks/financial_statistics_workbook.ipynb
```

`data/*.csv` is **already included** in the ZIP, so you do not need to run the generator. To reproduce them exactly, run `python generate_data.py`, which overwrites the CSVs using the fixed seed. The command `python run_tests.py --family all` creates `outputs/results.csv` plus PNG plots and `outputs/regression_summary.txt`. Changing the family allows you to isolate one topic. To modify the significance threshold, use `--alpha 0.01`.

## 2. Dataset dictionary and joins

| File | Grain / approximate rows | Main columns | Use cases |
|---|---|---|---|
| `data/clients.csv` | One row per client / 2,400 | `client_id`, `segment`, `risk_profile`, `digital_score`, `experiment_arm`, `wealth_usd`, `onboarded`, `advisory_adopted`, `complaint`, `monthly_revenue_usd`, `monthly_trades`, `latency_before_ms`, `latency_after_ms` | Mean/proportion tests, association, correlation, paired comparisons, regression |
| `data/orders.csv` | One row per order / 5,200 | `order_id`, `client_id`, `risk_profile`, `engine`, `order_notional_usd`, `execution_latency_ms`, `spread_bps`, `asset_class` | Distribution differences, execution performance, categorical composition |
| `data/strategies.csv` | One return observation per strategy/sample / 720 | `strategy`, `sample_id`, `monthly_return` | t-tests, ANOVA, variance, rank tests |
| `data/market_daily.csv` | One business day / 360 | `date`, `daily_return`, `price_index`, `trading_volume` | Normality, stationarity, autocorrelation |
| `data/rare_product_pilot.csv` | One pilot client / 44 | `pilot_id`, `product`, `complaint` | Fisher exact for small counts |

Join client + order records on `client_id` only if needed. **Important:** Multiple orders per client are correlated; tests on `orders.csv` that assume independent orders are **teaching demonstrations**, not fully defensible client-level inferences. For production work, use client-level aggregations, clustered inference, hierarchical models, or suitable repeated-measure methods. `strategies.csv` contains independent **synthetic draws** from each strategy distribution, not a properly aligned historical comparison; for actual strategies on identical market dates, compare **paired excess-return differences**, accounting for autocorrelation.

## 3. Test catalog: what to run, when, what chart

| Family | Tests included (Python functions) | Fictional wealth/brokerage decision | Charts saved |
|---|---|---|---|
| Means | one-sample t (`ttest_1samp`); Welch t (`ttest_ind`); paired t (`ttest_rel`); one-way ANOVA (`f_oneway`); educational known-sigma z | Are monthly returns above 0? Do strategy means differ? Did latency change? | strategy boxplot; paired latency histogram |
| Variance | classical F ratio; Levene median (`levene`); Bartlett (`bartlett`) | Do investment-strategy risk dispersions differ? | overlaid return histograms |
| Proportions | one- and two-proportion z (`proportions_ztest`); chi-square goodness-of-fit (`chisquare`) | Did onboarding conversion change? Does the asset-class mix differ from policy? | conversion bars |
| Association | chi-square independence (`chi2_contingency`); Fisher exact (`fisher_exact`) | Is risk category associated with advisory take-up? Is product linked to complaints in a tiny pilot? | stacked adoption bars |
| Correlation | Pearson (`pearsonr`); Spearman (`spearmanr`); Kendall (`kendalltau`) | Is digital engagement associated with trading activity? | scatterplot |
| Regression | coefficient t, model F (`statsmodels.formula.api.ols`) | Which predictors are conditionally associated with revenue? | residuals vs fitted; full summary text |
| Non-parametric | paired Wilcoxon (`wilcoxon`); Mann–Whitney U (`mannwhitneyu`); Kruskal–Wallis (`kruskal`) | How do skewed latency or strategy-return distributions compare? | engine boxplot |
| Distribution | corrected KS-type Lilliefors (`lilliefors`); Jarque–Bera (`jarque_bera`); Anderson–Darling (`anderson`); specified-distribution KS (`kstest`) | Is normality a reasonable working assumption for risk modeling? | histogram + normal fit; Q–Q plot |
| Time series | ADF (`adfuller`); KPSS (`kpss`); Ljung–Box (`acorr_ljungbox`) at 5/10/20 lags | Are prices/returns stationary? Do returns show serial dependence? | price/return series; autocorrelation |

**33 output rows** in `outputs/results.csv` because some families include multiple lag tests or multiple model coefficients. The Anderson–Darling normality test uses its 5% **critical value** rather than reporting a p-value.

## 4. Correct interpretation sequence for EACH test

1. **Business question**: e.g., *Did a randomized new onboarding experience improve the conversion rate?*
2. **Observation unit and design**: client-level randomized groups, one observation per client.
3. **Variable types**: binary `onboarded`, categorical `experiment_arm`.
4. **Hypotheses**: H0: p(control) = p(new); H1: they differ.
5. **Assumptions**: independent clients, assignment maintained, sufficient expected successes/failures, no metric peeking without correction.
6. **Check visualization**: group conversion rates with uncertainty; inspect sample sizes.
7. **Inferential results**: test statistic, p-value, alpha threshold, and ideally confidence interval.
8. **Effect magnitude**: absolute percentage-point lift and relative lift; commercial implications of a difference are distinct from statistical significance.
9. **Business recommendation**: consider guardrails such as complaint incidence and operational risk; do not infer improvement from a p-value alone.

### Inference cautions
- A **p-value is not** the probability that H0 is true.
- `p >= 0.05` does **not** prove no difference: the experiment may lack power.
- Statistical significance is **not** practical significance. Always estimate effect sizes and confidence intervals.
- Multiple comparisons increase false-positive risk; use pre-registration or adjustment (Holm, FDR) where appropriate.
- Independent sample tests break down with repeated orders, clustered clients, serially correlated returns, or selection bias; choose an appropriate design.
- Correlations, regressions, before/after comparisons, and association tests generally do **not** establish causality. Random assignment or defensible quasi-experimental design is needed.
- Mann–Whitney and Kruskal–Wallis are tests of relative ordering/distribution, **not automatically tests of medians**; median interpretation requires additional shape assumptions. Signed-rank tests assume symmetry of paired differences for common location interpretations.
- ADF non-rejection does not prove a unit root; KPSS non-rejection does not prove stationarity. Interpret together with plots, structure breaks, and sample size.
- KS with *estimated* mean and SD requires correction: this project supplies Lilliefors for fitted normality; the separate KS example uses a pre-specified normal distribution.
- Normality can fail even with economically acceptable forecasts, while *tail risk* can matter enormously in finance.

## 5. Suggested self-guided progression

**Day 1:** `means`, `variance`. Explore confidence intervals and why return volatility changes interpretations.

**Day 2:** `proportions`, `association`. Estimate absolute lift, odds ratio, and segment-level performance; question confounding and randomization.

**Day 3:** `correlation`, `regression`. Compare univariate relationships to covariate-adjusted estimates and examine residuals.

**Day 4:** `nonparametric`, `distribution`. Add extreme outliers to order latency; compare robust and parametric results.

**Day 5:** `timeseries`. Compare results for prices versus returns, then simulate an AR(1) process and inspect the ACF and Ljung–Box.

## 6. Two external, real (but historical) datasets for later

These are *supplements*, not substitutes for the integrated synthetic brokerage CSVs:

1. **Plotly example Apple OHLC stock price CSV** (historical, single security, compact). Direct URL: https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv
   ```python
   import pandas as pd
   apple = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
   apple['daily_return'] = apple['AAPL.Close'].pct_change()
   apple = apple.dropna(subset=['daily_return'])
   ```
   Use return distribution, Jarque–Bera, ADF, KPSS, Ljung–Box. Not designed for account conversion or client segmentation.
2. **Statsmodels macroeconomic CSV** (historical U.S. quarterly macroeconomic observations, compact). Direct URL: https://raw.githubusercontent.com/statsmodels/statsmodels/main/statsmodels/datasets/macrodata/macrodata.csv
   ```python
   import statsmodels.api as sm
   macro = sm.datasets.macrodata.load_pandas().data # bundled; no network needed
   ```
   Use macroeconomic time series and regression demos; not representative of brokerage transaction events.

Both online direct CSV URLs are public examples rather than market-data feeds. This package itself does not download either file automatically. For a production strategy backtest you must also address survivorship bias, corporate actions, benchmark alignment, market closures, overlapping observations, and transaction costs.

## 7. Exercises

- **Exercise 1 (means):** Compare mean `monthly_revenue_usd` across all three wealth segments; use ANOVA and a post-hoc test if needed.
- **Exercise 2 (proportions):** Calculate New App − Control conversion difference and a 95% confidence interval. Repeat separately for HNI.
- **Exercise 3 (association):** Compute a Cramér's V effect size for the risk-profile/advisory table.
- **Exercise 4 (regression):** Replace `monthly_revenue_usd` with `onboarded` and fit a logistic regression, interpreting odds ratios rather than OLS coefficients.
- **Exercise 5 (robustness):** Multiply 1% of `execution_latency_ms` observations by 30. Compare t-test, Mann–Whitney and trimmed means.
- **Exercise 6 (markets):** Create `daily_return_lag1`, then fit an autoregressive model and evaluate residual Ljung–Box.
- **Exercise 7 (design):** Explain why analyzing all 5,200 orders as independent can understate uncertainty when the same client submits many orders.

**License:** Generated synthetic datasets and authored learning code in this archive may be reused freely for learning and adaptation. Public external datasets have their own upstream provenance/licensing.
