import pandas as pd
import numpy as np
import glob
import re
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas.plotting import lag_plot, autocorrelation_plot
#
# data_files = glob.glob('./data/*.csv')
#
# master_df = pd.read_csv('./data/price_data.csv')
#
# master_df = master_df[['Date', 'Coin', 'Price (Close)', 'Price (High)', 'Price (Open)', 'Circulating Supply']]
# master_df['Date'] = master_df['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
master_df = pd.load_csv('price_supply_top_30_coins.csv', index=False)


def get_bitcoin_price(start, end):
    return master_df.loc[(master_df['Coin'] == 'bitcoin') &
                         (start <= master_df['Date']) &
                         (master_df['Date'] <= end)]


def date_english(dt):
    return f'{dt.day}-{dt.month}-{dt.year}'


def log_return(price_series):
    return np.diff(np.log(price_series))


def plot_double_axis_graph(df,
                           col_1,
                           col_1_label,
                           col_2,
                           col_2_label,
                           title,
                           output_dir):
    plt.figure(figsize=(12, 5))
    plt.title(title)
    ax1 = df[col_1].plot(color='green', grid=True, label=col_1_label)
    ax2 = df[col_2].plot(color='blue', grid=True, secondary_y=True, label=col_2_label)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1 + h2, l1 + l2, loc=2)
    ax1.legend(loc=2)
    ax2.legend(loc=1)
    plt.savefig(f'{output_dir}/{title}.png')
    plt.show()


if __name__ == "__main__":
    checklist = pd.read_excel('data_checklist.xlsx', sheet_name='Sheet1')
    checklist['Token'] = checklist['Token'].apply(lambda x: x.replace(' ', '-').lower())

    coins = ['neo', 'dogecoin', 'compound', 'polygon', 'tron', 'ontology', 'cosmos', 'avalanche']

    coin_jump_dates = {}
    for coin in coins:
        coin_row = checklist.loc[checklist.Token == coin]
        coin_date_pairs = []
        for col in coin_row:
            if col.startswith('jump'):
                if type(coin_row[col].iloc[0]) == pd._libs.tslibs.timestamps.Timestamp:
                    if 'start' in col:
                        jump_date_pair = [coin_row[col].iloc[0]]
                    elif 'end' in col:
                        jump_date_pair.append(coin_row[col].iloc[0])
                        coin_date_pairs.append(jump_date_pair)

        coin_jump_dates[coin] = coin_date_pairs

    filtered_data = {}
    for coin, dates in coin_jump_dates.items():
        coin_filtered = []
        for date_pair in dates:
            start_date = date_pair[0] - timedelta(days=30)
            end_date = date_pair[1] + timedelta(days=30)
            section = master_df.loc[(master_df['Coin'] == coin) &
                                    (start_date <= master_df['Date']) &
                                    (master_df['Date'] <= end_date)]

            if len(section):
                btc_for_period = get_bitcoin_price(start_date, end_date)
                section.set_index('Date', drop=True, inplace=True)
                btc_for_period.set_index('Date', drop=True, inplace=True)
                # df = section[['Price (Close)', 'Date']]
                # df.rename(columns={'Price (Close)': f'price_{coin}'}, inplace=True)

                joined_df = section.join(btc_for_period, lsuffix=f'_{coin}', rsuffix='_btc')
                joined_df = joined_df[[f'Price (Close)_{coin}', 'Price (Close)_btc', f'Circulating Supply_{coin}']]

                # Check output dir exists
                output_file_dir_price = f'./figures/price/{coin}'
                output_file_dir_log_return = f'./figures/log_return/{coin}'
                if not os.path.isdir(output_file_dir_price):
                    os.makedirs(output_file_dir_price, exist_ok = False)
                if not os.path.isdir(output_file_dir_log_return):
                    os.makedirs(output_file_dir_log_return, exist_ok = False)

                # Plot graphs
                plot_double_axis_graph(df=joined_df,
                                       col_1=f'Price (Close)_{coin}',
                                       col_1_label=f'{coin} Closing Price',
                                       col_2=f'Circulating Supply_{coin}',
                                       col_2_label='Supply',
                                       title=f'{coin} closing price vs supply between {date_english(start_date)} & {date_english(end_date)}',
                                       output_dir=output_file_dir_price)

                plot_double_axis_graph(df=joined_df,
                                       col_1='Price (Close)_btc',
                                       col_1_label=f'BTC Closing Price',
                                       col_2=f'Price (Close)_{coin}',
                                       col_2_label=f'{coin} Closing price',
                                       title=f'{coin} vs BTC closing price between {date_english(start_date)} & {date_english(end_date)}',
                                       output_dir=output_file_dir_price)

                # Log returns
                joined_df['log_btc_return'] = np.log(joined_df['Price (Close)_btc']) - np.log(
                    joined_df['Price (Close)_btc'].shift(1))

                joined_df[f'log_{coin}_return'] = np.log(joined_df[f'Price (Close)_{coin}']) - np.log(
                    joined_df[f'Price (Close)_{coin}'].shift(1))

                plot_double_axis_graph(df=joined_df,
                                       col_1=f'log_{coin}_return',
                                       col_1_label=f'{coin} log return',
                                       col_2=f'Circulating Supply_{coin}',
                                       col_2_label='Supply',
                                       title=f'{coin} closing price vs. supply between {date_english(start_date)}_{date_english(end_date)}',
                                       output_dir=output_file_dir_log_return)

                plot_double_axis_graph(df=joined_df,
                                       col_1='log_btc_return',
                                       col_1_label=f'BTC log return',
                                       col_2=f'log_{coin}_return',
                                       col_2_label=f'{coin} log return',
                                       title=f'{coin} vs. BTC log return between {date_english(start_date)}_{date_english(end_date)}',
                                       output_dir=output_file_dir_log_return)

                coin_filtered.append(joined_df)

        filtered_data[coin] = coin_filtered

    stats = []
    for df in filtered_data['avalanche']:
        # Get alpha
        df['excess_return'] = df['log_avalanche_return'] - df['log_btc_return']
        df['excess_return'].plot(color='blue')
        plt.show()

        # Test stationarity
        halfway_idx = int(len(df) / 2)
        before = df[f'excess_return'].iloc[:halfway_idx]
        after = df[f'excess_return'].iloc[halfway_idx:]
        mean1, mean2 = before.mean(), after.mean()
        var1, var2 = before.var(), after.var()
        stats.append({'before_mean': mean1, 'after_mean': mean2, 'before_var': var1, 'after_var': var2})

        # Check if data is random
        # Lag plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        lag_plot(df['excess_return'], ax=ax1)
        ax1.set_title('Excess Avalanche log return lag plot')
        # lag_plot(df['log_btc_return'], ax=ax2)
        # ax2.set_title('Bitcoin log return lag plot')
        plt.show()

        # ACF Plot
        fig2, ax3 = plt.subplots(figsize=(18, 5))
        autocorrelation_plot(df['excess_return'], ax=ax3)
        ax3.set_title('Avalanche excess log return ACF plot')
        plt.show()
