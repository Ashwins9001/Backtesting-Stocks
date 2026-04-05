# Overview
Using Airflow and Pandas to import some stock ticker data from various providers (such as Apple) and backtesting trading strategies on them.

# Strategies Implemented
For basic testing and set-up so far only one strategy has been implemented:
- Moving-Average Basis: If price falls below 20-day moving-average, then buy otherwise sell. This strategy is honestly a terrible one and it ended up just following the market which makes sense since it's based on just the given ticker price.