from price_data import price_data
from benchmark import benchmark_data
from statsmodels import regression
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.ticker as mtick

plt.style.use(['science'])


# Helper functions
def ols(x, y):
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y, x).fit()

    x = x[:, 1]
    return model.params[0], model.params[1]


def format_date(dt):
    return f'{dt.day}/{dt.month}/{dt.year}'


# Calculate coefficients
regression_data = price_data.loc[price_data['Coin'] == 'avalanche']
regression_data = regression_data.join(benchmark_data['benchmark_return']).dropna()

X = regression_data['benchmark_return']
Y = regression_data['daily_log_return']

alpha, beta = ols(X, Y)

X2 = np.linspace(X.min(), X.max(), 100)
Y_hat = X2 * beta + alpha

plt.figure(figsize=(10,7))
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.scatter(X, Y, alpha=0.3)
plt.grid(True)
plt.xlabel('Benchmark return, %')
plt.ylabel('Avalanche return, %')
plt.title('Avalanche Market Model')
plt.plot(X2, Y_hat, alpha=0.9)
plt.savefig('figures/avalanche_market_regression.png')
plt.show()

# Calculate abnormal returns
abnormal_returns = []
for idx, row in regression_data.iterrows():
    excess = row['daily_log_return'] - (alpha + beta*row['benchmark_return'])
    abnormal_returns.append(excess)

regression_data['abnormal_return'] = abnormal_returns

# Calculate cumulative abnormal return
supply_jump_dates = [datetime(2021, 9, 5), datetime(2021, 7, 7), datetime(2021, 3, 9), datetime(2020, 12, 9)]


def average_abnormal_return():
    pass


def cumulative_abnormal_return(abnormal_returns, window_start, window_end):
    return sum(abnormal_returns.loc[(abnormal_returns.date >= window_start) & (abnormal_returns.date >= window_end)])


regression_data['date'] = regression_data.index
regression_data['date'] = regression_data['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

cumulative_abnormal_returns = {}
car = {}
car_df = pd.DataFrame()
for t0 in supply_jump_dates:
    car_at_pt = []
    for date_window_idx in range(-21, 21):
        date = t0 + timedelta(days=date_window_idx)
        if date < t0:
            start = date
            end = t0
            abnormal_return_window = regression_data.loc[(regression_data.date >= start) & (regression_data.date <= end)]
        elif date > t0:
            start = t0
            end = date
            abnormal_return_window = regression_data.loc[(regression_data.date >= start) & (regression_data.date <= end)]
        else:
            abnormal_return_window = regression_data.loc[regression_data.date == t0]

        cumulative_return = sum(abnormal_return_window['abnormal_return'])

        # car_at_pt.append({date_window_idx: cumulative_return})
        car_df = car_df.append({'date': t0,
                                'window_idx': date_window_idx,
                                'cum_abnormal_return': cumulative_return * 100}, ignore_index=True)


# Plot Cumulative Abnormal Returns
fig, axs = plt.subplots(2, 2, figsize=(10,7))
fig.tight_layout(pad=4, h_pad=3, w_pad=3)
axs[0, 0].plot(car_df['window_idx'].loc[car_df['date'] == supply_jump_dates[0]],
               car_df['cum_abnormal_return'].loc[car_df['date'] == supply_jump_dates[0]])
axs[0, 0].set_title(f'CAR for {format_date(supply_jump_dates[0])}')
axs[0, 1].plot(car_df['window_idx'].loc[car_df['date'] == supply_jump_dates[1]],
               car_df['cum_abnormal_return'].loc[car_df['date'] == supply_jump_dates[1]],
               'tab:orange')
axs[0, 1].set_title(f'CAR for {format_date(supply_jump_dates[1])}')
axs[1, 0].plot(car_df['window_idx'].loc[car_df['date'] == supply_jump_dates[2]],
               car_df['cum_abnormal_return'].loc[car_df['date'] == supply_jump_dates[2]], 'tab:green')
axs[1, 0].set_title(f'CAR for {format_date(supply_jump_dates[2])}')
axs[1, 1].plot(car_df['window_idx'].loc[car_df['date'] == supply_jump_dates[3]],
               car_df['cum_abnormal_return'].loc[car_df['date'] == supply_jump_dates[3]], 'tab:red')
axs[1, 1].set_title(f'CAR for {format_date(supply_jump_dates[3])}')

for ax in axs.flat:
    ax.set(xlabel='Window Length', ylabel=r'CAR')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

# Hide x labels and tick labels for top plots and y ticks for right plots.
for ax in axs.flat:
    ax.label_outer()

plt.savefig('figures/avalanche_cumulative_return.png')
plt.show()


