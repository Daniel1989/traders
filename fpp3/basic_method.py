#Import the libraries that we are going to use for the analysis:
import pandas as pd
import numpy as np

from statsforecast import StatsForecast
from statsforecast.models import __all__

import matplotlib.pyplot as plt

df = pd.read_csv("Assets/aus-production.csv", sep=";")
bricks = df[["Quarter","Bricks"]]
bricks.columns = ["ds","bricks_prod"]


bricks_mask=bricks['ds']>="1970 Q1" # 制作一个过滤条件
filtered_bricks = bricks[bricks_mask] # 通过过滤条件获取一个子集

#Superior limit:
df_mask=filtered_bricks['ds']<="2004 Q4"
bricks = filtered_bricks[df_mask]


from statsforecast.models import HistoricAverage

# Create an array with the observed values in Bricks:
y_bricks = bricks["bricks_prod"].values

# Define the model, fit and predict:
model = HistoricAverage()
model = model.fit(y=y_bricks)
y_hat_dict = model.predict(h=20)
qua_pred = ['2005 Q1', '2005 Q2', '2005 Q3', '2005 Q4', '2006 Q1', '2006 Q2', '2006 Q3', '2006 Q4', '2007 Q1', '2007 Q2', '2006 Q1', '2006 Q2', '2006 Q3', '2006 Q4', '2007 Q1', '2007 Q2', '2007 Q3', '2007 Q4', '2008 Q1', '2008 Q2' ]

# Create a dataframe with the quarters and values predicted:
Y_pred_df = pd.DataFrame({'ds':qua_pred ,
                        'mean_forecast':y_hat_dict["mean"]})

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([bricks, Y_pred_df]).set_index('ds')
plot_df[['bricks_prod', 'mean_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Clay bricks production in Australia', fontsize=22)
ax.set_ylabel('Bricks', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()

plt.show()


from statsforecast.models import Naive

# Define the model, fit and predict:
model = Naive()
model = model.fit(y=y_bricks)
y_hat_dict = model.predict(h=20)

Y_pred_df["naive_forecast"] = y_hat_dict["mean"]
fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([bricks, Y_pred_df]).set_index('ds')
plot_df[['bricks_prod', 'naive_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Clay bricks production in Australia', fontsize=22)
ax.set_ylabel('Bricks', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

# SeasonalNaive's usage example:
from statsforecast.models import SeasonalNaive

# Define the model, fit and predict:
model = SeasonalNaive(season_length=4)
model = model.fit(y=y_bricks)
y_hat_dict = model.predict(h=20)
Y_pred_df["seasonal_naive_forecast"] = y_hat_dict["mean"]
fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([bricks, Y_pred_df]).set_index('ds')
plot_df[['bricks_prod', 'seasonal_naive_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Clay bricks production in Australia', fontsize=22)
ax.set_ylabel('Bricks', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

from statsforecast.models import RandomWalkWithDrift

# Define the model, fit and predict:
model = RandomWalkWithDrift()
model = model.fit(y=y_bricks)
y_hat_dict = model.predict(h=20)

Y_pred_df["drift_forecast"] = y_hat_dict["mean"]
fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([bricks, Y_pred_df]).set_index('ds')
plot_df[['bricks_prod', 'drift_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Clay bricks production in Australia', fontsize=22)
ax.set_ylabel('Bricks', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

beer = df[["Quarter","Beer"]]

#Inferior limit:
beer_mask=beer['Quarter']>="1992 Q1"
filtered_beer = beer[beer_mask]

#Superior limit:
beer_mask=filtered_beer['Quarter']<="2006 Q4"
beer = filtered_beer[beer_mask]
print(beer.head(2),"\n",beer.tail(2))

# Create an array with the observed values:
y_beer = beer["Beer"].values

# Define column names:
beer.columns = ["ds","beer_prod"]

# Mean method:
model = HistoricAverage()
model = model.fit(y=y_beer)
mean = model.predict(h=14)

# Naive method:
model = Naive()
model = model.fit(y=y_beer)
naive = model.predict(h=14)

# Seasonal Naive method:
model = SeasonalNaive(season_length=4)
model = model.fit(y=y_beer)
snaive = model.predict(h=14)

print("Mean method:",mean,"\n\nNaive method:",naive,"\n\nSeasonal naïve method:",snaive)

qua_pred = ['2007 Q1', '2007 Q2', '2006 Q1', '2006 Q2', '2006 Q3', '2006 Q4', '2007 Q1', '2007 Q2', '2007 Q3', '2007 Q4', '2008 Q1', '2008 Q2', '2009 Q2', '2010 Q2']

# Create a dataframe with the quarters and values predicted:
Y_pred_df = pd.DataFrame({'ds':qua_pred,
                        'mean_forecast':mean["mean"],
                        'naive_forecast':naive["mean"],
                        'snaive_forecast':snaive["mean"]})

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([beer, Y_pred_df]).set_index('ds')
plot_df[['beer_prod', 'mean_forecast', 'naive_forecast', 'snaive_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Forecast for quarterly beer production', fontsize=22)
ax.set_ylabel('Megalitres', fontsize=20)
ax.set_xlabel('Quarter', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()
plt.show()

google_stock = pd.read_csv("Assets/GOOGL.csv")

google_stock.head()
google_mask = google_stock["Date"] <= "2015-12-31"
google_2015 = google_stock[google_mask]

google_2015.head()
google_mask = google_stock["Date"] > "2015-12-31"
google_2016 = google_stock[google_mask]

google_2016.head()
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
                        'mean_forecast':mean["mean"],
                        'naive_forecast':naive["mean"],
                        'drift_forecast':drift["mean"]})

fig, ax = plt.subplots(1, 1, figsize = (20, 8))

# Concatenate the dataframe of predicted values with the dataframe of observed values:
plot_df = pd.concat([google_2015, Y_pred_df]).set_index('Date')
plot_df[['Close', 'mean_forecast', 'naive_forecast', 'drift_forecast']].plot(ax=ax, linewidth=2)

# Specify graph features:
ax.set_title('Google daily closing stock price', fontsize=22)
ax.set_ylabel('$US', fontsize=20)
ax.set_xlabel('Day', fontsize=20)
ax.legend(prop={'size': 15})
ax.grid()