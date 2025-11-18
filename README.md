# Bitcoin_Correlation_Study
Python script regarding the data analysis concerning Bitcoin with various assets and macros.
# BTC Correlation Analyzer

This repository contains a Python script for analyzing how Bitcoin (BTC) relates to traditional asset classes and key macroeconomic variables over time.

The tool downloads historical market and macro data, aligns everything to a common time frame (2012-01-01 to today), and computes a variety of correlation measures (full-sample, rolling, regime-based, and different time resolutions).

> **Note**: `requirements.txt` already lists all necessary dependencies. This README describes what the script does and how to use it.

---

## 1. Overview

The main script (e.g., `btc_correlation_analysis.py`) performs the following:

1. **Market Data Download**
   - Uses **Yahoo Finance** (`yfinance`) to pull daily price history for:
     - Bitcoin: `BTC-USD`
     - U.S. Treasuries ETF: `GOVT` (or another ticker if configured)
     - Gold ETF: `GLD`
     - International equities: `VXUS`
     - U.S. equities: `SPY`
     - U.S. energy sector ETF: `VDE`
     - Global energy sector ETF: `IXC`
     - (Optionally) additional tickers like `IYE`

2. **Macro Data Download**
   - Uses **FRED** (via `pandas_datareader`) to pull:
     - CPI: `CPIAUCSL`
     - PPI: `PPIACO`
     - Effective Federal Funds Rate: `FEDFUNDS`
     - 10-Year Treasury Yield: `GS10`
   - Data are resampled to a **month-end (`"ME"`) frequency** for macro–asset comparisons.

3. **Return & Change Calculations**
   - For assets: daily, weekly, and monthly **log returns**.
   - For macro series: **monthly percentage changes** (e.g., ΔCPI, ΔPPI, ΔFedFunds, Δ10Y).

4. **Correlation Analysis**
   - Full-sample correlation matrix of daily asset returns.
   - BTC’s correlation with each asset (daily, weekly, monthly).
   - **Rolling correlations** (e.g., 252-day rolling correlations of BTC vs each asset).
   - **Regime / sub-period correlations**, e.g.:
     - Early adoption (2012–2015)
     - Pre-COVID (2016–2019)
     - QE / everything rally (2020–2021)
     - Tightening / post-2022 regime
   - Correlations between **monthly asset returns and monthly macro changes**.

5. **Visualization & Outputs**
   - Normalized price plots for all assets over time.
   - Rolling correlation plots for BTC vs each asset.
   - CSV exports for:
     - Full correlation matrices (assets only).
     - BTC-vs-asset correlation slices.
     - Per-regime correlation matrices.
     - Weekly and monthly correlation matrices.
     - Asset–macro correlation matrices.

---

## 2. Data Sources

- **Price Data (Market Assets)**
  - Source: Yahoo Finance via `yfinance`
  - Frequency: Daily adjusted close prices
  - Coverage: From 2012-01-01 to present (subject to ticker history)

- **Macro Data**
  - Source: FRED via `pandas_datareader`
  - Series:
    - `CPIAUCSL` – Consumer Price Index (All Items, Urban Consumers)
    - `PPIACO` – Producer Price Index (All Commodities)
    - `FEDFUNDS` – Effective Federal Funds Rate
    - `GS10` – 10-Year Treasury Constant Maturity Yield
  - Frequency: Typically monthly, resampled to **month-end** for alignment with asset data.

> Depending on your environment and `pandas_datareader` version, FRED may require setting an API key (e.g., `FRED_API_KEY`). If authentication errors occur, configure the key according to the library’s documentation.

---

## 3. Installation

- Execute pip install -r requirements.txt
- Execute python btc_correlations.py

# Results (As of Nov 2025)

<img width="1200" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/21bb4c92-7cbb-4b82-b9fb-61cb9b09bfb1" />

<img width="1200" height="700" alt="Figure_2" src="https://github.com/user-attachments/assets/cd385f4a-5b99-4f3b-ab82-35dd54d7a78b" />

```
=== Correlation Matrix (ME-resampled returns) ===
Ticker           BTC      Gold  USTreasury       IXC       IYE       SPY       VDE      VXUS
Ticker
BTC         1.000000  0.068374    0.016332  0.193167  0.193145  0.350477  0.190662  0.259130
Gold        0.068374  1.000000    0.340893  0.035890  0.001782  0.076971 -0.001842  0.237722
USTreasury  0.016332  0.340893    1.000000 -0.255457 -0.270406  0.085641 -0.282213  0.126759
IXC         0.193167  0.035890   -0.255457  1.000000  0.978938  0.611507  0.979174  0.671678
IYE         0.193145  0.001782   -0.270406  0.978938  1.000000  0.629114  0.998731  0.632836
SPY         0.350477  0.076971    0.085641  0.611507  0.629114  1.000000  0.620837  0.834283
VDE         0.190662 -0.001842   -0.282213  0.979174  0.998731  0.620837  1.000000  0.629049
VXUS        0.259130  0.237722    0.126759  0.671678  0.632836  0.834283  0.629049  1.000000

=== BTC Correlations vs Macro (Monthly) ===
CPI        -0.019877
PPI         0.038264
FedFunds   -0.110845
GS10        0.080606
```
