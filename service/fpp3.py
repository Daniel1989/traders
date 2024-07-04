import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
import matplotlib.pyplot as plt


def calc_interval(df, is_minute=False):
    season_length = 5
    freq = 'D'
    h = 10
    if is_minute:
        season_length = 60
        freq = 'T'
        h = 60

    data = pd.DataFrame(df, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data['Close'] = data['Close'].astype(float)

    data_train = data[["Date", "Close"]]

    data_train.columns = ["ds", "y"]

    data_train["unique_id"] = "Close price"

    data_train['ds'] = pd.to_datetime(data_train['ds'])

    models = [AutoARIMA(season_length=season_length, approximation=True)]
    fcst = StatsForecast(df=data_train,
                         models=models,
                         freq=freq,
                         n_jobs=-1)

    levels = [80, 95]
    forecasts = fcst.forecast(h=h, level=levels)
    return forecasts, data_train


def draw_interval(forecasts, origin_data):
    forecasts = forecasts.reset_index()
    fig, ax = plt.subplots(1, 1, figsize=(20, 7))

    # Concatenate the dataframe of predicted values with the dataframe of observed values:
    df_plot = pd.concat([origin_data, forecasts]).set_index('ds')
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
    ax.set_title('price trending', fontsize=20)
    ax.set_ylabel('Yuan', fontsize=15)
    ax.set_xlabel('Day', fontsize=15)
    ax.legend(prop={'size': 15})
    ax.grid()
    plt.savefig('fpp3.png')

