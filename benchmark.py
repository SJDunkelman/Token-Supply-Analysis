import pandas as pd
from price_data import price_data
from datetime import datetime
import numpy as np

benchmark_coins = ['bitcoin', 'ethereum', 'monero', 'dogecoin', 'litecoin', 'xrp']
benchmark_data = price_data.loc[price_data['Coin'].isin(benchmark_coins)].copy()
benchmark_data['circulating_marketcap'] = benchmark_data['Circulating Supply'] * benchmark_data['Price (Close)']

weight_columns = benchmark_coins + ['date']
dates = pd.date_range(start=datetime(2018, 1, 1), end=max(price_data.index))
benchmark = []
for day in dates:
    daily_prices = benchmark_data.loc[benchmark_data.index == day].copy()
    total_market_cap = sum(daily_prices['circulating_marketcap'])
    daily_prices['market_weight'] = daily_prices['circulating_marketcap'] / total_market_cap
    # if any(daily_prices.isna()):
    #     continue
    daily_weights = {'date': day}
    benchmark_value, benchmark_return = 0, 0
    for idx, row in daily_prices.iterrows():
        daily_weights[row['Coin']] = row['market_weight']
        benchmark_value += row['market_weight'] * row['Price (Close)']
        benchmark_return += row['market_weight'] * (np.log(row['Price (Close)']) - np.log(row['Price (Open)']))

    daily_weights['benchmark_value'] = benchmark_value
    daily_weights['benchmark_return'] = benchmark_return
    benchmark.append(daily_weights)

benchmark_data = pd.DataFrame(benchmark)
benchmark_data.set_index('date', drop=True, inplace=True)
benchmark_data.dropna(inplace=True)
benchmark_data.to_csv('./data/benchmark_data.csv')
