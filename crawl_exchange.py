import datetime
import time
from concurrent.futures import ProcessPoolExecutor
from models import ForecastInterval
from service.futures_data import sync_main_code_minute_data
from util.utils import is_trade_time

if __name__ == "__main__":
    while True:
        today = datetime.date.today()
        if today.weekday() == 5 or today.weekday() == 6:
            time.sleep(60)
            continue
        if not is_trade_time():
            time.sleep(60)
            continue
        exchange_list = ['sh', 'gz', 'dl', 'zz']
        forecast_date = ForecastInterval.select().order_by(ForecastInterval.forecast_date.desc()).get()
        forecast_data = ForecastInterval.select().where(ForecastInterval.forecast_date == forecast_date.forecast_date)
        data = {}
        for item in forecast_data:
            data[item.goods_code + str(item.goods_num)] = {
                "forecast_date": item.forecast_date,
                "goods_code": item.goods_code,
                "goods_num": item.goods_num,
                "p95_low_price": item.p95_low_price,
                "p80_low_price": item.p80_low_price,
                "p80_high_price": item.p80_high_price,
                "p95_high_price": item.p95_high_price
            }
        for item in exchange_list:
            sync_main_code_minute_data(item, data)
        time.sleep(60)
