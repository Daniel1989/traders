#Import the libraries that we are going to use for the analysis:
import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import RandomWalkWithDrift
import statsmodels.api as sm
import matplotlib.pyplot as plt

def mstl(x, period, blambda=None, s_window=7 + 4 * np.arange(1, 7)):
    origx = x
    n = len(x)
    msts = period
    # iterate = 1
    if x.ndim == 2:
        x = x[:, 0]
    if np.isnan(x).any():
        ...  # na.interp
    if blambda is not None:
        ...  # boxcox
    # tt = np.arange(n)
    if msts > 1:
        fit = sm.tsa.STL(x, period=msts, seasonal=s_window[0]).fit()
        seas = fit.seasonal
        deseas = x - seas
        trend = fit.trend
    else:
        try:
            from supersmoother import SuperSmoother
        except ImportError as e:
            print("supersmoother is required for mstl with period=1")
            raise e
        msts = None
        deseas = x
        t = 1 + np.arange(n)
        trend = SuperSmoother().fit(t, x).predict(t)
    deseas[np.isnan(origx)] = np.nan
    remainder = deseas - trend
    output = {"data": origx, "trend": trend}
    if msts is not None:
        output["seasonal"] = seas
    output["remainder"] = remainder
    return pd.DataFrame(output)

# Create a dataframe from a csv file:
df_employment  = pd.read_csv("Assets/us_retail_employment.csv")

# Rename columns:
df_employment.columns = ["ds","us_retail_employment"]

# Convert string Date time into Python Date time:
df_employment['ds'] = pd.to_datetime(df_employment['ds'])

# Create a new column in the dataframe, unique_id:
df_employment["unique_id"] = "us_retail_employment"

# Decompose a time series:
# 分解
mstl_df = mstl(df_employment['us_retail_employment'].values, 12, blambda=None, s_window=7 + 4 * np.arange(1, 7))

trend_employ_df = pd.DataFrame()
trend_employ_df['ds']  = df_employment['ds']
trend_employ_df['y'] = mstl_df['trend']
trend_employ_df['seasonally_adjusted_comp'] = mstl_df['trend']
trend_employ_df["unique_id"] = "seasonally_adjusted_comp"

from statsforecast.models import AutoARIMA
models = [AutoARIMA(season_length=12, approximation=True)]
fcst = StatsForecast(df=trend_employ_df,
                     models=models,
                     freq="M",
                     n_jobs=-1)

levels = [80, 95]
X_df = pd.DataFrame({
    'seasonally_adjusted_comp': trend_employ_df['seasonally_adjusted_comp'][-20:],
    'ds': trend_employ_df['ds'][-20:],
    'unique_id': trend_employ_df['unique_id'][-20:],

})
forecasts = fcst.forecast(h=20, level=levels, X_df=X_df)

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
trend_fore_df = pd.concat([df_employment, forecasts]).set_index('ds')
plt.plot(trend_fore_df['us_retail_employment'], 'k-', trend_fore_df['AutoARIMA'], 'b-')

# Specify graph features:
ax.fill_between(trend_fore_df.index,
                trend_fore_df['AutoARIMA-lo-80'],
                trend_fore_df['AutoARIMA-hi-80'],
                alpha=.35,
                color='blue',
                label='auto_arima_level_80')
ax.fill_between(trend_fore_df.index,
                trend_fore_df['AutoARIMA-lo-95'],
                trend_fore_df['AutoARIMA-hi-95'],
                alpha=.2,
                color='blue',
                label='auto_arima_level_95')
ax.set_title('US retail employment', fontsize=20)
ax.set_ylabel('Number of people', fontsize=15)
ax.set_xlabel('Month', fontsize=15)
ax.legend(prop={'size': 15})
ax.legend(['US retail employment', 'AutoARIMA model seasonally adjusted'], prop={'size': 15})
ax.grid()

seasonal_employ_df = pd.DataFrame()
seasonal_employ_df['ds']  = df_employment['ds']
seasonal_employ_df['y'] = mstl_df['seasonal']
seasonal_employ_df['seasonal_comp'] = mstl_df['seasonal']
seasonal_employ_df['unique_id'] = 'seasonal_comp'

from statsforecast.models import SeasonalNaive
models = [SeasonalNaive(season_length=12)]
fcst = StatsForecast(df=seasonal_employ_df,
                     models=models,
                     freq="M",
                     n_jobs=-1)
x_df = pd.DataFrame({
    'seasonal_comp': seasonal_employ_df['seasonal_comp'][-20:],
    'ds': seasonal_employ_df['ds'][-20:],
    'unique_id': seasonal_employ_df['unique_id'][-20:],
})
forecasts = fcst.forecast(h=20, level=levels, X_df=x_df)

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
seasonal_fore_df = pd.concat([seasonal_employ_df, forecasts]).set_index('ds')
seasonal_fore_df[['seasonal_comp', 'SeasonalNaive']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('US retail employment', fontsize=22)
ax.set_ylabel('Number of people', fontsize=20)
ax.set_xlabel('Month', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

trend_fore_df.reset_index(inplace=True)
# Create a dataframe with trend and seasonal forecasts values:
total_fore_df = pd.DataFrame({'ds':np.append(df_employment['ds'], trend_fore_df['ds']),
                    'us_retail_employment':df_employment['us_retail_employment'],
                    'AutoARIMA':(trend_fore_df['AutoARIMA'].values + seasonal_fore_df['SeasonalNaive']),
                    'AutoARIMA-lo-95':(trend_fore_df['AutoARIMA-lo-95'].values + seasonal_fore_df['SeasonalNaive']),
                    'AutoARIMA-lo-80':(trend_fore_df['AutoARIMA-lo-80'].values + seasonal_fore_df['SeasonalNaive']),
                    'AutoARIMA-hi-95':(trend_fore_df['AutoARIMA-hi-95'].values + seasonal_fore_df['SeasonalNaive']),
                    'AutoARIMA-hi-80':(trend_fore_df['AutoARIMA-hi-95'].values + seasonal_fore_df['SeasonalNaive'])})

total_fore_df.set_index('ds', inplace=True)
print(total_fore_df)

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

plt.plot(total_fore_df['us_retail_employment'], 'k-', total_fore_df['AutoARIMA'], 'b-')

# Specify graph features:
ax.fill_between(total_fore_df.index,
                total_fore_df['AutoARIMA-lo-80'],
                total_fore_df['AutoARIMA-hi-80'],
                alpha=.35,
                color='blue',
                label='auto_arima_level_80')
ax.fill_between(total_fore_df.index,
                total_fore_df['AutoARIMA-lo-95'],
                total_fore_df['AutoARIMA-hi-95'],
                alpha=.2,
                color='blue',
                label='auto_arima_level_95')
ax.set_title('US retail employment', fontsize=20)
ax.set_ylabel('Number of people', fontsize=15)
ax.set_xlabel('Month', fontsize=15)
ax.legend(prop={'size': 15})
ax.legend(['US retail employment', 'AutoARIMA model seasonally adjusted'], prop={'size': 15})

ax.grid()
plt.show()

type_model_list = []
y_values = df_employment['us_retail_employment'].values
for n in range(len(df_employment)):
    type_model_list.append('AutoARIMA')
    n += 1
fitted_values = AutoARIMA(season_length=12, approximation=True).fit(df_employment['us_retail_employment'].values).predict_in_sample()
residuals = df_employment['us_retail_employment'].values - fitted_values["fitted"]

augment_df = pd.DataFrame({'model':type_model_list,
                    'time_var':df_employment['ds'],
                    'obs_values':df_employment['us_retail_employment'].values,
                    'fitted_values':fitted_values["fitted"],
                    'residuals':residuals})

print(augment_df.head())

fig, ax = plt.subplots(1, 1, figsize = (20, 8))
augment_df['residuals'].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Residuals', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Month', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

fig, axs = plt.subplots(1, 1,
                        figsize=(20, 8),
                        tight_layout=True)

axs.hist(augment_df["residuals"], bins=20)

# Specify graph features:
axs.set_title('Histogram of residuals', fontsize=22)
axs.set_ylabel('count', fontsize=20)
axs.set_xlabel('residuals', fontsize=20)

# Show plot
plt.show()

import math

ticker_data = augment_df["residuals"]
ticker_data_acf = [ticker_data.autocorr(i) for i in range(1, 25)]

test_df = pd.DataFrame([ticker_data_acf]).T
test_df.columns = ['Autocorr']
test_df.index += 1
test_df.plot(kind='bar', width=0.05, figsize=(20, 4))

# Statisfical significance.
n = len(augment_df['residuals'])
plt.axhline(y=2 / math.sqrt(n), color='r', linestyle='dashed')
plt.axhline(y=-2 / math.sqrt(n), color='r', linestyle='dashed')

# Adding plot title.
plt.title("Residuals from the Naive method")

# Providing x-axis name.
plt.xlabel("lag[1]")

# Providing y-axis name.
plt.ylabel("ACF")

plt.show()