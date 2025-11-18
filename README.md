# Bitcoin_Correlation_Study
Python script regarding the data analysis concerning Bitcoin with various assets and macros.

# Summary
Performs operations described in the attached paper.
Pulls data from Yahoo Finance and FRED and compares correlations indices from [-1, 1].

If the correlation index approaches -1, the stronger an inverse correlation.
If the correlation index approaches 1, the stronger a direct correlation.

# Installation

- Execute pip install -r requirements.txt
- Execute python btc_correlations.py

# Results (As of Nov 2025)

<img width="1200" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/21bb4c92-7cbb-4b82-b9fb-61cb9b09bfb1" />

<img width="1200" height="700" alt="Figure_2" src="https://github.com/user-attachments/assets/cd385f4a-5b99-4f3b-ab82-35dd54d7a78b" />

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
