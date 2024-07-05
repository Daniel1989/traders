from dotenv import load_dotenv
from datetime import datetime
import requests
from service.fpp3 import calc_interval, draw_interval
from service.futures_data import get_goods_minute_data, sync_daily_data, get_main_code_no, save_forecast_item

load_dotenv()

# 统计每日账户资金
# client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3")
# response = client.chat.completions.create(
#     model="ep-20240615044418-lmzkv",
#     messages=[
#         {"role": "system", "content": 'You are a help assistant.'},
#         {"role": "user", "content": 'who you are'},
#     ],
# )
# print(response)
# draw_daily_account()

# forecast预测
# url = ("http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol"
#                 "=ag2408")
# daily_history = requests.get(url).json()
# result, _ = calc_interval(daily_history)
# data = get_goods_minute_data("AG2408")
# result_minute, origin_data = calc_interval(data, is_minute=True)
# p95_min = min(result_minute.iloc[:, 2].to_list())
# p95_max = max(result_minute.iloc[:, 5].to_list())
# p80_min = min(result_minute.iloc[:, 3].to_list())
# p80_max = max(result_minute.iloc[:, 4].to_list())
# s1 = ("基于近一年的每日收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对今日收盘价格进行预测，"
#      "得到80%的置性区间为：["+str(result.iloc[0][3])+", "+str(result.iloc[0][4])+"]。"
#      "95%的置性区间为：["+str(result.iloc[0][2])+", "+str(result.iloc[0][5])+"]。")
#
# s2 = ("基于最近6个小时内的每分钟收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对接下去的一小时内的每分钟收盘价格进行预测，"
#      "得到结果如下，有80%的可能价格在["+str(p80_min)+", "+str(p80_max)+"]的区间内变动,"
#      "95%的的可能价格在["+str(p95_min)+", "+str(p95_max)+"]的区间内变动。")
# draw_interval(result, origin_data)

# 同步每日数据
# dateStr = datetime.now().strftime('%Y%m%d')
date_list = [
    '20240704',
]
for item in date_list:
    sync_daily_data(item)

data = get_main_code_no()
for item in data:
    save_forecast_item(item)
    break

