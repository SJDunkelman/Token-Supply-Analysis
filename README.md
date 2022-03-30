<h1 align="center">Token Supply Analysis</h1>

Exploratory analysis of price inefficiencies caused by significant increases in the circulating supply of a cryptocurrency token, with the objective of assessing whether this relationship can be used to form a trading strategy for the client.



// Img of graphs

<tools badges>

## Table of Contents

* Prequisites
* Installation
* Methodology/Usage
* Report Findings

### Prerequisites

The first stage of data collection in this project was compiling a list of all top 30 cryptocurrencies by marketcap over time as to not introduce survivorship bias from the current top 30. In the interest of modularity I've separated this into its own <a href="https://github.com/SJDunkelman/historical-cryptocurrency-leaders">repo which can be found here</a>.

Once this list was compiled, I manually gathered price and supply data over the 2019-2021 period from <a href="www.messari.io">Messari</a>, which at the time of this project did not have API coverage for all the necessary coins.

### Installation

1. Clone this repo

```bash
git clone https://github.com/SJDunkelman/token-supply-analysis
```

2. Create virtual environment requirements.txt

```
cd token-supply-analysis
virtualenv venv/
source venv/bin/activate
pip install -r requirements.txt
```

Note: This was developed and tested on an intel iMac. For M1 Macs you might have to use Conda due to better support of Statsmodels ARM wheels. 

### Methodology/Usage
#### Data processing
Price & Supply data from each currency/token was collated and standardised in <code>price_data.py</code>. The output of this can be found in <code>price_supply_top_30_coins.csv</code>

#### Benchmark
In order to calculate the excess return of a security, we must first derive the return of a market benchmark. As there is no obvious benchmark unlike equities (and single securities such as BTC are non-stationary in their market significance), we first create an index time-series from a selection of key currencies weighted by market cap. 

You can find an implementation of this in <code>benchmark.py</code> for BTC, ETH, XMR, DOGE, LTC & XRP.

#### Abnormal return OLS

To calculate abnormal returns we need to derive α (excess return of token) & β (sensitivity of return to market changes). This is done using an OLS regression of token log return against the log return of the benchmark derived previously. For this exploratory data analysis we focused on Avalanche (AVA) which is shown below in figure 1.

![An OLS regression of Avalanche against a market benchmark](/figures/avalanche_market_regression.png "OLS regression")
<p align="center"><i>Figure 1.</i></p>

#### Event study
Dates of significant circulating supply changes were then identified for the Avalanche token based on announced vesting/supply events. The cumulative abnormal return for a window of 21 days either side of the event, the plots of which you can see below in figure 2.

![Cumulative Abnormal Returns for the event windows](/figures/avalanche_cumulative_return.png "Cumulative Abnormal Returns")
<p align="center"><i>Figure 2.</i></p>

The code for the abnormal returns and CAR can be found in <code>analysis.py</code> 
The conclusions of the analysis can be found in the report PDF in the <code>report</code> folder of this repo.

#### Test the data
The event data was tested for stationarity, as well as ACF & Lag plots produced to examine the data for any seasonality or correlated behaviour between the token and the benchmark returns.

You can find the code for these plots in <code>test_plots.py</code>
