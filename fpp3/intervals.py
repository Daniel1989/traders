import pandas as pd
import numpy as np
import random
from itertools import product
from ipywidgets import interact

from statsforecast import StatsForecast
from statsforecast.models import __all__

import matplotlib.pyplot as plt

google_stock = pd.read_csv("Assets/GOOGL.csv")

# Filter the year of interest:
google_mask = google_stock["Date"] <= "2015-12-31"
google_2015 = google_stock[google_mask]

# Define a new dataframe with daily close prices and dates:
google_train = google_2015[["Date", "Close"]]

# Rename columns:
google_train.columns = ["ds", "y"]

# Create a new column in the dataframe, unique_id:
google_train["unique_id"] = "Close price"

# Convert string Date time into Python Date time object:
google_train['ds'] = pd.to_datetime(google_train['ds'])

from statsforecast.models import AutoARIMA

# Since we are dealing with daily data, it would be benefitial to use 5 as seasonality.
models = [AutoARIMA(season_length=5, approximation=True)]
fcst = StatsForecast(df=google_train,
                     models=models,
                     freq="D",
                     n_jobs=-1)

levels = [80, 95]
forecasts = fcst.forecast(h=10, level=levels)
forecasts = forecasts.reset_index()
fig, ax = plt.subplots(1, 1, figsize = (20, 7))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
df_plot = pd.concat([google_train, forecasts]).set_index('ds')
df_plot[['y', 'AutoARIMA']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.fill_between(df_plot.index,
                df_plot['AutoARIMA-lo-80'],
                df_plot['AutoARIMA-hi-80'],
                alpha=.35,
                color='blue',
                label='auto_arima_level_80')
ax.fill_between(df_plot.index,
                df_plot['AutoARIMA-lo-95'],
                df_plot['AutoARIMA-hi-95'],
                alpha=.2,
                color='blue',
                label='auto_arima_level_95')
ax.set_title('Google daily closing stock price', fontsize=20)
ax.set_ylabel('$US', fontsize=15)
ax.set_xlabel('Day', fontsize=15)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()