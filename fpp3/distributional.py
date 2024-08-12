#Import the libraries that we are going to use for the analysis:
import pandas as pd
import numpy as np
import random
from itertools import product
from ipywidgets import interact

from statsforecast import StatsForecast
from statsforecast.models import __all__

import matplotlib.pyplot as plt

# Create a dataframe from a csv file:
google_stock = pd.read_csv("Assets/GOOGL.csv")

# Filter the year of interest:
google_mask = google_stock["Date"] <= "2015-12-31"
google_2015 = google_stock[google_mask]

# Filter the year of interest:
google_mask = google_stock["Date"] > "2015-12-31"
google_2016 = google_stock[google_mask]

# Define a new dataframe with daily close prices and dates:
google_train = google_2015[["Date", "Close"]]
google_test = google_2016[["Date", "Close"]]

# Rename columns:
google_train.columns = ["ds", "y"]
google_test.columns = ["ds", "y"]

# Create a new column in the dataframe, unique_id:
google_train["unique_id"] = "Close price"
google_test["unique_id"] = "Close price"

# Convert string Date time into Python Date time object:
google_train['ds'] = pd.to_datetime(google_train['ds'])
google_test['ds'] = pd.to_datetime(google_test['ds'])

# import the model that we are going to use for the analysis:
from statsforecast.models import AutoARIMA

# Since we are dealing with daily data, it would be benefitial to use 5 as seasonality.
models = [AutoARIMA(season_length=5, approximation=True)]

# Define the model, fit and predict:
fcst = StatsForecast(df=google_train,
                     models=models,
                     freq="D",
                     n_jobs=-1)

levels = [80]
forecasts = fcst.forecast(h=30, level=levels)
forecasts = forecasts.reset_index()
# Merge test dataframe with forecast predicted
df_plot_1 = google_test.merge(forecasts, left_on='ds', right_on='ds')

# Concatenate train dataframe with the previous dataframe
df_plot_2 = pd.concat([google_train, df_plot_1]).set_index('ds')

fig, ax = plt.subplots(1, 1, figsize = (20, 7))

plt.plot(df_plot_2['y'], 'k-', df_plot_2['AutoARIMA'], 'b-')

# Specify graph features:
ax.fill_between(df_plot_2.index,
                df_plot_2['AutoARIMA-lo-80'],
                df_plot_2['AutoARIMA-hi-80'],
                alpha=.35,
                color='blue',
                label='auto_arima_level_80')
ax.set_title('Google daily closing stock price', fontsize=20)
ax.set_ylabel('$US', fontsize=15)
ax.set_xlabel('Day', fontsize=15)
ax.legend(prop={'size': 15})
plt.show()

'''
quantile_score() function: Return quantile score.

* prob: Percentile analized.
* f: Int. number, interval value predicted.
* y: Int. number, value observed.'''

def quantile_score(prob, f, y):

    if y >= f:
        q_score = 2 * prob * (y-f)
    else:
        q_score = 2 * (1-prob) * (f-y)

    return q_score

quantile_score(0.1, df_plot_1['AutoARIMA-lo-80'][0], df_plot_1['y'][0])
'''
winkler_score() function: Return winkler score.

* a: Percentile analized.
* l: Int. number, low interval value predicted.
* u: Int. number, high interval value predicted.
* y: Int. number, value observed.'''

def winkler_score(a, l, u, y):

    if y < l:
        winkler_score = (u-l) + 2/a * (l-y)
    if l < y < u:
        winkler_score = (u-l)
    if y > u:
        winkler_score = (u-l) + 2/a * (y-u)

    return winkler_score

winkler_score(0.1, df_plot_1['AutoARIMA-lo-80'][0], df_plot_1['AutoARIMA-hi-80'][0], df_plot_1['y'][0])
def create_levels(train_dataframe, test_dataframe, season_length, freq, horizon):

    models = [AutoARIMA(season_length=season_length, approximation=True)]

    fcst = StatsForecast(df=train_dataframe,
                     models=models,
                     freq=freq,
                     n_jobs=-1)

    levels = [90, 80, 70, 60, 50, 40, 30, 20, 10]
    forecasts = fcst.forecast(h=horizon, level=levels)
    forecasts = forecasts.reset_index()
    df_fore = test_dataframe.merge(forecasts, left_on='ds', right_on='ds')

    return df_fore

df_fore = create_levels(google_train, google_test, 5, 'D', 30)
'''
crps() function: Return Continuous Ranked Probability Score.

* df: Dataframe with test values and forecast intervals values.
* model: Model analized name.
* levels_list: list, levels analized. '''


def crps(df, model, levels_list):
    import re

    obs_values = df.y
    q_scores = []

    lvl_lo, lvl_hi = model + '-lo-', model + '-hi-'
    lvl_low = [lvl_lo + str(i) for i in levels_list]
    lvl_high = [lvl_hi + str(i) for i in levels_list]
    lvl_list = lvl_low + lvl_high

    for level in lvl_list:
        s = -[float(s) for s in re.findall(r'-?\d+\.?\d*', level)][0]
        prob = (1 - s / 100) / 2
        res = obs_values - df[level]

        for e in res:

            if e > 0:
                q_score = 2 * prob * (obs_values - df[level])

            else:
                q_score = 2 * (1 - prob) * (df[level] - obs_values)

            q_scores.append(q_score)

    crps = np.average(q_scores)

    return crps

crps(df_fore, 'AutoARIMA', [90, 80, 70, 60])
