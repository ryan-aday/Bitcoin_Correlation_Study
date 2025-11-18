"""
btc_correlations_vde_ixc.py

Compare BTC vs U.S. Treasuries, gold, VXUS, SPY, VDE, and IXC
from 2012-01-01 to today, and compute correlation coefficients
between BTC and each of these assets.

Assets (default):
- Bitcoin: BTC-USD
- U.S. Treasuries: GOVT
- Gold: GLD
- International stocks (ex-US): VXUS
- U.S. equities: SPY
- U.S. energy (ETF): VDE
- Global energy (ETF): IXC

Outputs:
- Summary of data coverage per asset
- Correlation matrix of daily log returns
- BTC-to-asset correlations (daily log returns)
- Optional rolling correlation plots and price plots

Requirements:
    pip install yfinance pandas numpy matplotlib
"""

import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

def download_price_data(asset_tickers, start_date="2012-01-01", end_date=None):
    """
    Download adjusted close prices for the given assets using yfinance.

    Parameters
    ----------
    asset_tickers : dict
        Mapping of asset name -> ticker string.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str or None
        End date in 'YYYY-MM-DD' format. If None, uses today's date.

    Returns
    -------
    prices : pd.DataFrame
        DataFrame of adjusted close prices with columns as asset names.
    """
    if end_date is None:
        end_date = dt.date.today().strftime("%Y-%m-%d")

    tickers = list(asset_tickers.values())
    print(f"Downloading data from {start_date} to {end_date} for tickers: {tickers}")

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        progress=False,
    )

    # yfinance returns a multi-index column with ("Adj Close", ticker) when multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            prices = data["Adj Close"].copy()
        else:
            # Fallback: try Close
            prices = data["Close"].copy()
        prices.columns = prices.columns.get_level_values(0)
    else:
        # Single-ticker case
        if "Adj Close" in data.columns:
            prices = data["Adj Close"].copy()
        else:
            prices = data["Close"].copy()

    # Rename columns from tickers to human-readable names
    inv_map = {v: k for k, v in asset_tickers.items()}
    prices = prices.rename(columns=inv_map)

    prices = prices.sort_index()

    return prices


def compute_log_returns(prices):
    """
    Compute daily log returns for a price DataFrame.

    Parameters
    ----------
    prices : pd.DataFrame
        Price data.

    Returns
    -------
    returns : pd.DataFrame
        Daily log returns.
    """
    returns = np.log(prices / prices.shift(1))
    returns = returns.dropna(how="all")
    return returns


def summarize_data_coverage(prices):
    """
    Print basic data coverage per asset.

    Parameters
    ----------
    prices : pd.DataFrame
        Price data.
    """
    print("\n=== Data Coverage Summary ===")
    for col in prices.columns:
        series = prices[col].dropna()
        if series.empty:
            print(f"{col}: NO DATA")
        else:
            print(
                f"{col}: {series.index[0].date()} -> {series.index[-1].date()}, "
                f"{len(series)} data points"
            )


def compute_correlations(returns):
    """
    Compute correlation matrix of daily returns.

    Parameters
    ----------
    returns : pd.DataFrame
        Daily log returns.

    Returns
    -------
    corr_matrix : pd.DataFrame
        Correlation matrix.
    """
    corr_matrix = returns.corr()
    return corr_matrix


def extract_btc_correlations(corr_matrix, btc_name="BTC"):
    """
    Extract BTC's correlations with all other assets.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix of assets.
    btc_name : str
        Name of BTC's column in the matrix.

    Returns
    -------
    btc_corrs : pd.Series
        Correlation coefficients for BTC vs each asset.
    """
    if btc_name not in corr_matrix.index:
        raise ValueError(f"BTC column '{btc_name}' not found in correlation matrix.")
    btc_corrs = corr_matrix.loc[btc_name].drop(btc_name)
    return btc_corrs


def plot_prices(prices, title="Asset Prices (normalized)", normalize=True):
    """
    Plot normalized price series for comparison.

    Parameters
    ----------
    prices : pd.DataFrame
        Price data.
    title : str
        Plot title.
    normalize : bool
        If True, normalize all series to 1.0 at their first non-NaN value.
    """
    plt.figure(figsize=(12, 6))

    if normalize:
        norm_prices = prices.copy()
        for col in norm_prices.columns:
            first_valid = norm_prices[col].dropna()
            if first_valid.empty:
                continue
            base = first_valid.iloc[0]
            norm_prices[col] = norm_prices[col] / base
        norm_prices.plot(ax=plt.gca())
    else:
        prices.plot(ax=plt.gca())

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Normalized Price" if normalize else "Price")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_btc_rolling_correlations(returns, btc_name="BTC", window=252):
    """
    Plot rolling correlation of BTC vs each other asset.

    Parameters
    ----------
    returns : pd.DataFrame
        Daily log returns.
    btc_name : str
        Column name for BTC in returns.
    window : int
        Rolling window size in trading days (252 ~ 1 trading year).
    """
    if btc_name not in returns.columns:
        raise ValueError(f"BTC column '{btc_name}' not found in returns DataFrame.")

    other_assets = [col for col in returns.columns if col != btc_name]
    plt.figure(figsize=(12, 7))

    for asset in other_assets:
        rolling_corr = (
            returns[btc_name]
            .rolling(window=window, min_periods=int(window * 0.5))
            .corr(returns[asset])
        )
        rolling_corr.plot(label=f"{btc_name} vs {asset}")

    plt.title(f"Rolling {window}-day Correlations with {btc_name}")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.axhline(0, linestyle="--")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def compute_regime_correlations(returns, regimes, btc_name="BTC"):
    """
    Compute correlation matrices and BTC-vs-others correlations
    for each specified sub-period (regime).

    Parameters
    ----------
    returns : pd.DataFrame
        Daily log returns for all assets.
    regimes : dict
        Mapping of regime name -> (start_date, end_date) as 'YYYY-MM-DD' strings.
    btc_name : str
        Column name used for Bitcoin in `returns`.

    Returns
    -------
    regime_results : dict
        {regime_name: {"corr_matrix": DataFrame, "btc_corrs": Series}}
    """
    regime_results = {}

    print("\n=== Regime / Sub-period Correlations ===")
    for regime_name, (start, end) in regimes.items():
        mask = (returns.index >= start) & (returns.index <= end)
        sub = returns.loc[mask]

        # Skip regimes with too little data
        if sub.shape[0] < 30:
            print(f"{regime_name}: not enough data ({sub.shape[0]} rows), skipping.")
            continue

        corr_mat = sub.corr()
        btc_corrs = extract_btc_correlations(corr_mat, btc_name=btc_name)

        print(f"\n--- {regime_name} ({start} to {end}) ---")
        print("BTC correlations:")
        print(btc_corrs)

        # Optionally: you can print corr_mat here too if you like
        # print("\nFull correlation matrix:")
        # print(corr_mat)

        regime_results[regime_name] = {
            "corr_matrix": corr_mat,
            "btc_corrs": btc_corrs,
        }

    return regime_results


def resample_and_compute_correlations(prices, freq="W", btc_name="BTC"):
    """
    Resample prices (weekly/monthly), compute log returns and correlations.

    Parameters
    ----------
    prices : pd.DataFrame
        Price data for all assets.
    freq : str
        Resampling frequency, e.g. "W" (weekly), "M" (month-end).
    btc_name : str
        Column name used for Bitcoin.

    Returns
    -------
    corr_matrix : pd.DataFrame
        Correlation matrix of resampled returns.
    btc_corrs : pd.Series
        BTC correlations vs other assets.
    """
    # Resample to end-of-period prices, then compute log returns
    prices_resampled = prices.resample(freq).last()
    returns_resampled = compute_log_returns(prices_resampled)

    # Ensure we only use periods where BTC has data
    if btc_name not in returns_resampled.columns:
        raise ValueError(f"`{btc_name}` not found in resampled returns.")

    returns_resampled = returns_resampled.dropna(subset=[btc_name])
    corr_matrix = returns_resampled.corr()
    btc_corrs = extract_btc_correlations(corr_matrix, btc_name=btc_name)

    print(f"\n=== Correlation Matrix ({freq}-resampled returns) ===")
    print(corr_matrix)

    print(f"\n=== BTC Correlations with Other Assets ({freq}-resampled returns) ===")
    print(btc_corrs)

    return corr_matrix, btc_corrs

def fetch_macro_data(start_date, end_date):
    """
    Fetch CPI, PPI, Fed funds rate, and 10Y Treasury yield from FRED.

    Parameters
    ----------
    start_date, end_date : str 'YYYY-MM-DD'

    Returns
    -------
    macro : pd.DataFrame
        Columns: CPI, PPI, FedFunds, GS10
        Frequency: as returned by FRED (mostly monthly)
    """
    fred_series = {
        "CPI": "CPIAUCSL",    # CPI, all urban consumers, all items
        "PPI": "PPIACO",      # PPI, all commodities
        "FedFunds": "FEDFUNDS",  # Effective federal funds rate
        "GS10": "GS10",       # 10Y Treasury constant maturity yield
    }

    macro_list = []
    for name, code in fred_series.items():
        s = pdr.DataReader(code, "fred", start_date, end_date)
        s = s.rename(columns={code: name})
        macro_list.append(s)

    macro = pd.concat(macro_list, axis=1)
    macro = macro.sort_index()
    return macro


def correlate_assets_with_macro_monthly(prices, macro, btc_name="BTC", freq="ME"):
    """
    Put assets and macro data on the same monthly frequency, compute
    correlations between monthly asset returns and macro changes.

    Parameters
    ----------
    prices : pd.DataFrame
        Daily asset prices (BTC, SPY, VDE, etc.).
    macro : pd.DataFrame
        CPI, PPI, FedFunds, GS10 (as from fetch_macro_data).
    btc_name : str
        Name of BTC column in `prices`.
    freq : str
        Resample frequency, e.g. 'ME' for month-end.

    Returns
    -------
    corr_macro : pd.DataFrame
        Correlation matrix of monthly returns/changes.
    btc_vs_macro : pd.Series
        BTC correlations vs macro variables.
    """
    # 1) Resample both to month-end
    prices_m = prices.resample(freq).last()
    macro_m = macro.resample(freq).last()

    # 2) Compute monthly log returns for assets
    asset_rets_m = compute_log_returns(prices_m)

    # 3) Compute monthly percentage changes for macro series
    #    (you could also do year-over-year with .pct_change(12))
    macro_chg_m = macro_m.pct_change()

    # 4) Combine and drop rows with any missing values
    combined = pd.concat([asset_rets_m, macro_chg_m], axis=1).dropna()

    # 5) Correlation matrix
    corr_macro = combined.corr()

    # 6) BTC vs macro slice
    macro_names = [c for c in ["CPI", "PPI", "FedFunds", "GS10"] if c in corr_macro.columns]
    btc_vs_macro = corr_macro.loc[btc_name, macro_names]

    print("\n=== Correlations: Monthly Asset Returns vs Monthly Macro Changes ===")
    print(corr_macro)

    print("\n=== BTC Correlations vs Macro (Monthly) ===")
    print(btc_vs_macro)

    return corr_macro, btc_vs_macro


def main():
    # ---------------------------------------------------------------------
    # 1. Define asset universe and tickers
    # ---------------------------------------------------------------------
    asset_tickers = {
        "BTC": "BTC-USD",     # Bitcoin in USD
        "USTreasury": "GOVT", # U.S. Treasury bond ETF
        "Gold": "GLD",        # Gold ETF
        "VXUS": "VXUS",       # Vanguard Total International Stock ETF
        "SPY": "SPY",         # S&P 500 ETF
        "VDE": "VDE",         # Vanguard Energy ETF
        "IXC": "IXC",         # iShares Global Energy ETF
        "IYE": "IYE",         # iShares U.S. Energy ETF
        
    }

    start_date = "2012-01-01"
    end_date = None  # defaults to today

    # ---------------------------------------------------------------------
    # 2. Download price data
    # ---------------------------------------------------------------------
    prices = download_price_data(asset_tickers, start_date=start_date, end_date=end_date)

    # Forward-fill and back-fill to handle missing days (esp. BTC vs ETFs)
    prices = prices.ffill().bfill()

    summarize_data_coverage(prices)

    # ---------------------------------------------------------------------
    # 3. Compute log returns
    # ---------------------------------------------------------------------
    returns = compute_log_returns(prices)

    # Restrict to dates where BTC has data
    if "BTC" in returns.columns:
        returns_with_btc = returns.dropna(subset=["BTC"])
    else:
        raise ValueError("BTC column ('BTC') not found in returns DataFrame.")

    # ---------------------------------------------------------------------
    # 4. Correlation analysis
    # ---------------------------------------------------------------------
    corr_matrix = compute_correlations(returns_with_btc)
    print("\n=== Correlation Matrix of Daily Log Returns ===")
    print(corr_matrix)

    btc_corrs = extract_btc_correlations(corr_matrix, btc_name="BTC")
    print("\n=== BTC Correlations with Other Assets (Daily Log Returns) ===")
    print(btc_corrs)

    # Save to CSV for further analysis
    corr_matrix.to_csv("correlation_matrix_full_period.csv")
    btc_corrs.to_csv("btc_correlations_full_period.csv")

    # ---------------------------------------------------------------------
    # 4b. Regime (sub-period) correlations
    # ---------------------------------------------------------------------
    regimes = {
        "Early_Adoption_2012_2015": ("2012-01-01", "2015-12-31"),
        "Pre_COVID_2016_2019":      ("2016-01-01", "2019-12-31"),
        "QE_Everything_2020_2021":  ("2020-01-01", "2021-12-31"),
        "Tightening_2022_onward":   ("2022-01-01", dt.date.today().strftime("%Y-%m-%d")),
    }

    regime_results = compute_regime_correlations(
        returns_with_btc,
        regimes=regimes,
        btc_name="BTC",
    )

    # Optionally save each regime's BTC correlations to CSV
    for name, res in regime_results.items():
        res["btc_corrs"].to_csv(f"btc_correlations_{name}.csv")
        res["corr_matrix"].to_csv(f"correlation_matrix_{name}.csv")

    # ---------------------------------------------------------------------
    # 4c. Weekly and monthly correlations
    # ---------------------------------------------------------------------
    weekly_corr, weekly_btc_corrs = resample_and_compute_correlations(
        prices,
        freq="W",     # weekly
        btc_name="BTC",
    )
    weekly_btc_corrs.to_csv("btc_correlations_weekly.csv")
    weekly_corr.to_csv("correlation_matrix_weekly.csv")

    monthly_corr, monthly_btc_corrs = resample_and_compute_correlations(
        prices,
        freq="ME",     # month-end
        btc_name="BTC",
    )
    monthly_btc_corrs.to_csv("btc_correlations_monthly.csv")
    monthly_corr.to_csv("correlation_matrix_monthly.csv")

    # ---------------------------------------------------------------------
    # 5. Plots (optional; comment out if not needed)
    # ---------------------------------------------------------------------
    plot_prices(
        prices,
        title="Normalized Asset Prices (BTC, USTreasury, Gold, VXUS, SPY, VDE, IXC)"
    )

    # Rolling correlations (1-year window)
    plot_btc_rolling_correlations(returns_with_btc, btc_name="BTC", window=252)

    # ---------------------------------------------------------------------
    # 6. Macro data: CPI, PPI, Fed funds, 10Y Treasury (FRED)
    # ---------------------------------------------------------------------
    macro = fetch_macro_data(start_date, end_date if end_date is not None else dt.date.today().strftime("%Y-%m-%d"))

    # Monthly correlations: BTC & other assets vs macro variables
    corr_macro, btc_vs_macro = correlate_assets_with_macro_monthly(
        prices,
        macro,
        btc_name="BTC",
        freq="ME",  # month-end; matches your change
    )

    # Optionally save to CSV
    corr_macro.to_csv("correlation_matrix_monthly_with_macro.csv")
    btc_vs_macro.to_csv("btc_vs_macro_monthly.csv")


if __name__ == "__main__":
    main()
