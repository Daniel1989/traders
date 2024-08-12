#Import the libraries that we are going to use for the analysis:
import pandas as pd
import numpy as np
import scipy

from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
from statsforecast.models import RandomWalkWithDrift

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

# Create a dataframe from a csv file:
df_eggs = pd.read_csv("Assets/egg_prices.csv", sep=";")

# Rename columns:
df_eggs.columns = ["ds","egg_prices"]

# Create a new column in the dataframe, unique_id:
df_eggs["unique_id"] = "egg_prices"

# Return a serie with a log transformation (λ=0):
df_eggs["egg_prices"] = scipy.stats.boxcox(df_eggs["egg_prices"].values, lmbda=0, alpha=None, optimizer=None)
df_eggs["y"] = df_eggs["egg_prices"]

df_eggs['ds'] = pd.to_datetime(df_eggs['ds'], format='%Y')

models = [AutoARIMA(season_length=1, approximation=True), RandomWalkWithDrift()]
print(df_eggs.head())
fcst = StatsForecast(df=df_eggs,
                     models=models,
                     freq="Y",
                     n_jobs=-1)

levels = [80]
future_dates = pd.date_range(start='1983', periods=10, freq='Y')
time_list = []
for item in df_eggs['egg_prices'].values:
    time_list.append(item)
exog_data = {
    'ds': future_dates,
    'egg_prices': time_list[-10:],
    'unique_id': ['egg_prices'] * 10
}
exog_df = pd.DataFrame(exog_data)
exog_df.set_index('ds', inplace=True)
exog_df['ds'] = pd.to_datetime(exog_data['ds'], format='%Y')
forecasts = fcst.forecast(h=10, level=levels, X_df=exog_df)
forecasts['ds'] = forecasts['ds'].dt.year
# Calculate the exponential of the values forecasted and the intervals:
forecasts["AutoARIMA"] = np.exp(forecasts["AutoARIMA"])
forecasts["AutoARIMA-lo-80"] = np.exp(forecasts["AutoARIMA-lo-80"])
forecasts["AutoARIMA-hi-80"] = np.exp(forecasts["AutoARIMA-hi-80"])
forecasts["RWD"] = np.exp(forecasts["RWD"])
print(forecasts.head(5))

df_eggs = pd.read_csv("Assets/egg_prices.csv", sep=";")
df_eggs.columns = ["ds","egg_prices"]
df_eggs["unique_id"] = "egg_prices"

fig, ax = plt.subplots(1, 1, figsize = (20, 8))
print(df_eggs.tail())
print("aa")
print(forecasts)
# Concatenate the dataframe of predicted values with the dataframe of observed values:
df_plot = pd.concat([df_eggs, forecasts]).set_index('ds')
plt.plot(df_plot['egg_prices'], 'k-', df_plot['AutoARIMA'], 'b-', df_plot['RWD'], 'b--' )

# Specify graph features:
ax.fill_between(df_plot.index,
                df_plot['AutoARIMA-lo-80'],
                df_plot['AutoARIMA-hi-80'],
                color='blue',
                where=(df_plot['AutoARIMA-hi-80'] >= df_plot['AutoARIMA-lo-80']),
                interpolate=True,
                label='auto_arima_level_80')

ax.set_title('Annual eggs prices', fontsize=20)
ax.set_ylabel('$US (in cents ajusted by inflation', fontsize=15)
ax.set_xlabel('Year', fontsize=15)
ax.legend(['egg_prices', 'AutoARIMA model', 'RWD model'], prop={'size': 15})
ax.grid()
plt.show()