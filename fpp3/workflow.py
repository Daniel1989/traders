import pandas as pd
import numpy as np
import statsforecast
import matplotlib.pyplot as plt
from statsforecast import StatsForecast
from statsforecast.models import ETS

df = pd.read_csv("Assets/global_economy_data.csv", delimiter=";")

print(df.head())
fig = plt.figure(figsize=(20,8))
ax = plt.axes()

# Specify graph features
plt.title("GDP per capita for Sweden")
plt.xlabel("Year [1Y]")
plt.ylabel("$US")

ax.plot( df["Year"], df["Sweden_gdp_per_cap"])
# Create an array with the observed values in Sweden_gdp_per_cap:
y_sweden_gdp_per_cap = df["Sweden_gdp_per_cap"].values

# Create a dataframe with the observed values in Sweden_gdp_per_cap and date index:
Y_df = df[["Year","Sweden_gdp_per_cap"]]
Y_df.columns = ["ds","y"]

ets = ETS(model='ZMZ',
          season_length=4)
ets = ets.fit(y=y_sweden_gdp_per_cap)

y_hat_dict = ets.predict(h=3)
print(y_hat_dict)
years_pred = [2018,2019,2020]

# Create a dataframe with the years and values predicted
Y_pred_df = pd.DataFrame({'ds':years_pred ,
                        'ETS':y_hat_dict["mean"]})
print(Y_pred_df)

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values
plot_df = pd.concat([Y_df, Y_pred_df]).set_index('ds')
plot_df[['y', 'ETS']].plot(ax=ax, linewidth=2)

# Specify graph features
ax.set_title('GDP per capita for Sweden', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Year', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()