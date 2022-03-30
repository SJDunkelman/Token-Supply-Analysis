import glob
import re
import pandas as pd
from datetime import datetime
import numpy as np

data_files = glob.glob('./data/coins/*.csv')

price_data = pd.DataFrame()
for csv_file in data_files:
    df = pd.read_csv(csv_file)
    df['Coin'] = re.search(r'(?<=data_)(.+)(?=_\d+)', csv_file).group()
    price_data = price_data.append(df)

price_data = price_data[['Date', 'Coin', 'Price (Close)', 'Price (High)', 'Price (Open)', 'Circulating Supply']]
price_data['Date'] = price_data['Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
price_data.to_csv('price_supply_top_30_coins.csv', index=False)

daily_returns = []
for idx, row in price_data.iterrows():
    log_return = np.log(row['Price (Close)']) - np.log(row['Price (Open)'])
    daily_returns.append(log_return)


price_data['daily_log_return'] = daily_returns
price_data.set_index('Date', drop=True, inplace=True)
price_data.to_csv('./data/price_data.csv')
