#Import the libraries that we are going to use for the analysis:
import pandas as pd
import numpy as np
import scipy
from statsforecast import StatsForecast
from statsforecast.models import HistoricAverage
from statsforecast.models import Naive
from statsforecast.models import SeasonalNaive
from statsforecast.models import RandomWalkWithDrift
import matplotlib.pyplot as plt
aus_production = pd.read_csv("Assets/aus-production.csv", sep=";")
# Filter the year of interest:
aus_production_mask = aus_production['Quarter']>="1995"
filtered_aus_production = aus_production[aus_production_mask]
# Filter the year of interest:
aus_production_mask = aus_production['Quarter']>="1995 Q1"
filtered_aus_production = aus_production[aus_production_mask]
last_20 = aus_production.iloc[-20:]
print(last_20)

# Filter the year of interest:
aus_production_mask = aus_production['Quarter']>="1992"
recent_production = aus_production[aus_production_mask]

aus_production_mask = recent_production['Quarter']<"2008"
beer_train = recent_production[aus_production_mask]

y_beer = beer_train["Beer"].values

# Mean method:
model = HistoricAverage()
model = model.fit(y=y_beer)
mean = model.predict(h=10)

# Naive method:
model = Naive()
model = model.fit(y=y_beer)
naive = model.predict(h=10)

# Seasonal Naive method:
model = SeasonalNaive(season_length=4)
model = model.fit(y=y_beer)
snaive = model.predict(h=10)

# Drift method:
model = RandomWalkWithDrift()
model = model.fit(y=y_beer)
drift = model.predict(h=10)

print("Mean method:",mean,"\n\nNaive method:",naive,"\n\nSeasonal naïve method:",snaive,"\n\nDrift method:",drift)

# Specify the quarters predicted:
qua_pred = ['2008 Q1', '2008 Q2', '2008 Q3', '2008 Q4', '2009 Q1', '2009 Q2', '2009 Q3', '2009 Q4', '2010 Q1', '2010 Q2']

# Create a dataframe with the quarters and values predicted:
beer_fc = pd.DataFrame({'Quarter':qua_pred,
                        'obs_values':recent_production['Beer'].values[-10:],
                        'mean_forecast':mean["mean"],
                        'naive_forecast':naive["mean"],
                        'snaive_forecast':snaive["mean"],
                        'drift_forecast':drift["mean"]})

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([recent_production, beer_fc]).set_index('Quarter')
plt.plot(plot_df['Beer'], 'k-', plot_df['mean_forecast'], 'b-', plot_df['naive_forecast'], 'g-', plot_df['snaive_forecast'], 'm-', plot_df['drift_forecast'], 'r-')

# Specify graph features:
ax.set_title('Forecast for quarterly beer production', fontsize=22)
ax.set_ylabel('Megalitres', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
x_ticks = np.arange(0, len(plot_df), 4)
ax.set_xticks(x_ticks)

ax.legend(['Beer', 'mean_forecast', 'naive_forecast', 'snaive_forecast', 'drift_forecast'], prop={'size': 15})

plt.show()

'''accuracy() function: Return a dataframe whith the measures RMSE, MAE, MAPE and MASE of the models evaluated.

* df_forecast: Dataframe with a columns that contain observed values called obs_values and columns that contains forecasts.
* y_train_serie: Numpy array that contain the values used to train the forecast models.
* seasonallity: Factor relative with the seasonallity of the time series forecasted. For non seasonallity time series the factor is 1,
for quarter seasonallity the the factor is 4, for monthly seasonallity the the factor is 12.'''

def accuracy(df_forecast, y_train_serie, seasonallity):

    method = df_forecast.columns[2:]
    rmse_results = []
    mae_results = []
    mape_results = []
    mase_results = []

    y = df_forecast.obs_values.values
    y_hat_naive = df_forecast.naive_forecast.values
    scale = np.abs(y_train_serie[:-seasonallity] - y_train_serie[seasonallity:])
    scale = np.average(scale)

    for i in method:

        y_hat = df_forecast[i].values
        d = y - y_hat
        mae_f = np.mean(abs(d))
        rmse_f = np.sqrt(np.mean(d**2))
        mape = np.mean(np.abs((y - y_hat)/y))*100
        mase = mae_f / scale
        mae_results.append(np.round(mae_f,2))
        rmse_results.append(np.round(rmse_f,2))
        mape_results.append(np.round(mape,2))
        mase_results.append(np.round(mase,2))

    accuracy_df = pd.DataFrame({'Method':method,
                    'RMSE':rmse_results,
                    'MAE':mae_results,
                    'MAPE':mape_results,
                    'MASE':mase_results})

    return accuracy_df
accuracy(beer_fc, beer_train["Beer"].values, 4)

# Create a dataframe from a csv file:
google_stock = pd.read_csv("Assets/GOOGL.csv")

# Filter the year of interest:
google_mask = google_stock["Date"] <= "2015-12-31"
google_2015 = google_stock[google_mask]

# Filter the year of interest:
google_mask = google_stock["Date"] > "2015-12-31"
google_2016 = google_stock[google_mask]

# Create arrays with Close values:
y_google_2015 = google_2015["Close"].values
y_google_2016 = google_2016["Close"].values

# Mean method:
model = HistoricAverage()
model = model.fit(y=y_google_2015)
mean = model.predict(h=len(y_google_2016))

# Naive method:
model = Naive()
model = model.fit(y=y_google_2015)
naive = model.predict(h=len(y_google_2016))

# Drift method:
model = RandomWalkWithDrift()
model = model.fit(y=y_google_2015)
drift = model.predict(h=len(y_google_2016))

print("Mean method:",mean,"\n\nNaive method:",naive,"\n\nDrift method:",drift)
date_pred = google_2016["Date"]

# Create a dataframe with the quarters and values predicted:
Y_pred_df = pd.DataFrame({'Date':date_pred,
                        'obs_values':y_google_2016,
                        'mean_forecast':mean["mean"],
                        'naive_forecast':naive["mean"],
                        'drift_forecast':drift["mean"]})

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([google_stock, Y_pred_df]).set_index('Date')
plt.plot(plot_df['Close'], 'k-', plot_df['mean_forecast'], 'b-', plot_df['naive_forecast'], 'g-', plot_df['drift_forecast'], 'r-')

# Specify graph features:
ax.set_title('Google daily closing stock price', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Day', fontsize=20)
x_ticks = np.arange(0, len(plot_df), 20)
ax.set_xticks(x_ticks)
ax.legend(['Close', 'mean_forecast', 'naive_forecast', 'drift_forecast'], prop={'size': 15})
plt.show()
accuracy(Y_pred_df, y_google_2015, 1)

