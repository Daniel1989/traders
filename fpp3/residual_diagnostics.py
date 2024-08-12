import pandas as pd
import numpy as np
import statsmodels

from statsforecast import StatsForecast
from statsforecast.models import __all__

import matplotlib.pyplot as plt
# Create a dataframe from a csv file:
google_stock = pd.read_csv("Assets/GOOGL.csv")

# Filter the year of interest:
google_mask = google_stock["Date"] <= "2015-12-31"
google_2015 = google_stock[google_mask]
fig, ax = plt.subplots(1, 1, figsize = (20, 8))
google_2015['Close'].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Google daily closing stock price in 2015', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Day[1]', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()


# Naive method:
from statsforecast.models import Naive

# Create arrays with Close values:
y_google_2015 = google_2015["Close"].values

# Define the model, fit and predict:
model = Naive()
model = model.fit(y=y_google_2015)
naive = model.predict(h=10)

def augment(model_name, time_var, obs_values):
    type_model_list = []
    for n in range(len(obs_values)):
        type_model_list.append(model_name)
        n += 1
    fitted_values = model.predict_in_sample()
    residuals = obs_values - fitted_values["fitted"]

    augment_df = pd.DataFrame({'model':type_model_list,
                        'time_var':time_var,
                        'obs_values':obs_values,
                        'fitted_values':fitted_values["fitted"],
                        'residuals':residuals})

    return(augment_df)

aug_df = augment("Naive", google_2015["Date"], google_2015["Close"])
print(aug_df)

fig, ax = plt.subplots(1, 1, figsize = (20, 8))
aug_df['residuals'].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Google daily closing stock price in 2015', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Day[1]', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()

fig, axs = plt.subplots(1, 1,
                        figsize=(20, 8),
                        tight_layout=True)

axs.hist(aug_df["residuals"], bins=20)

# Specify graph features:
axs.set_title('Histogram of residuals', fontsize=22)
axs.set_ylabel('count', fontsize=20)
axs.set_xlabel('residuals', fontsize=20)

# Show plot

import math

ticker_data = aug_df["residuals"]
ticker_data_acf = [ticker_data.autocorr(i) for i in range(1, 25)]

test_df = pd.DataFrame([ticker_data_acf]).T
test_df.columns = ['Autocorr']
test_df.index += 1
test_df.plot(kind='bar', width=0.05, figsize=(20, 4))

# Statisfical significance.
n = len(aug_df['residuals'])
plt.axhline(y=2 / math.sqrt(n), color='r', linestyle='dashed')
plt.axhline(y=-2 / math.sqrt(n), color='r', linestyle='dashed')

# Adding plot title.
plt.title("Residuals from the Naive method")

# Providing x-axis name.
plt.xlabel("lag[1]")

# Providing y-axis name.
plt.ylabel("ACF")

plt.show()

df_box_pierce = statsmodels.stats.diagnostic.acorr_ljungbox(test_df, lags=10, boxpierce=True, model_df=1)
df_box_pierce = df_box_pierce[["bp_stat","bp_pvalue"]]
print(df_box_pierce.tail(1))
ljung_box = statsmodels.stats.diagnostic.acorr_ljungbox(test_df, lags=10, model_df=1)
print(ljung_box.tail(1))

from statsforecast.models import RandomWalkWithDrift

# Define the model, fit and predict:
model = RandomWalkWithDrift()
model = model.fit(y=y_google_2015)
y_hat_dict = model.predict(h=10)

aug_df_drift = augment("Drift", google_2015["Date"], google_2015["Close"])

ticker_data = aug_df_drift["residuals"]
ticker_data_acf = [ticker_data.autocorr(i) for i in range(1,25)]
test_df = pd.DataFrame([ticker_data_acf]).T
test_df.columns = ['Autocorr']
test_df.index += 1

ljung_box = statsmodels.stats.diagnostic.acorr_ljungbox(test_df, lags=10, model_df=1)
ljung_box.tail(1)