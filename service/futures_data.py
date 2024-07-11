import datetime
import time

from models import GoodsPriceInSecond, DailyTraderData, database, ForecastInterval, MinuteTradeData
from peewee import fn
from service.exchange import factory
from service.fpp3 import calc_interval
from util.notify import send_common_to_ding
from util.utils import is_trade_time


def get_goods_minute_data_by_code(code):
    try:
        code_no = code[:2]
        contract_num = code[2:]
        query = MinuteTradeData.select().where(MinuteTradeData.goods_code == code_no,
                                               MinuteTradeData.contract_number == contract_num).order_by(
            MinuteTradeData.data_time.desc()).limit(60)
        result = []
        for record in query:
            result.append([
                record.data_time,
                record.open_price,
                record.high_price,
                record.low_price,
                record.close_price,
                record.deal_vol
            ])
        result.reverse()
        return result
    except Exception as e:
        print(e)
        return []


def get_goods_minute_data(code):
    try:
        inner = GoodsPriceInSecond.select(
            GoodsPriceInSecond.uid,
            GoodsPriceInSecond.deal_vol,
            GoodsPriceInSecond.price_time,
            GoodsPriceInSecond.current_price.alias('current_price'),
            fn.DATE_FORMAT(GoodsPriceInSecond.price_time, '%Y-%m-%d %H:%i').alias('minute_start'),
        ).where(GoodsPriceInSecond.uid == code).order_by(GoodsPriceInSecond.price_time.desc()).limit(5000).alias(
            'inner')

        first = (GoodsPriceInSecond.select(
            fn.MIN(inner.c.price_time).alias('first_time'),
            inner.c.minute_start
        ).from_(inner).group_by(inner.c.minute_start))

        first_price = (GoodsPriceInSecond.select(
            first.c.first_time,
            first.c.minute_start,
            inner.c.current_price
        ).from_(first).join(inner, on=(first.c.first_time == inner.c.price_time)))

        last = (GoodsPriceInSecond.select(
            fn.MAX(inner.c.price_time).alias('last_time'),
            inner.c.minute_start
        ).from_(inner).group_by(inner.c.minute_start))

        last_price = (GoodsPriceInSecond.select(
            last.c.last_time,
            last.c.minute_start,
            inner.c.current_price
        ).from_(last).join(inner, on=(last.c.last_time == inner.c.price_time)))

        start_end = (GoodsPriceInSecond.select(
            first_price.c.first_time,
            first_price.c.current_price.alias('open_price'),
            last_price.c.last_time,
            last_price.c.current_price.alias('close_price'),
            first_price.c.minute_start,
        ).from_(last_price).join(first_price, on=(last_price.c.minute_start == first_price.c.minute_start))).limit(500)

        query = (GoodsPriceInSecond.select(
            inner.c.minute_start,
            start_end.c.first_time,
            start_end.c.last_time,
            start_end.c.open_price,
            start_end.c.close_price,
            fn.MAX(inner.c.current_price).alias('high_price'),
            fn.MIN(inner.c.current_price).alias('low_price'),
            (fn.MAX(inner.c.deal_vol) - fn.MIN(inner.c.deal_vol)).alias('volume')
        ).from_(inner)
                 .join(start_end, on=(inner.c.minute_start == start_end.c.minute_start))
                 .order_by(inner.c.price_time)
                 .group_by(inner.c.minute_start))

        # cur = database.cursor()
        # print(cur.mogrify(*query.sql()))
        # print(len(query))
        result = []
        for record in query:
            # print(
            #     f"Minute: {record.minute_start}, "
            #     f"Start: {record.first_time}, "
            #     f"End: {record.last_time}, "
            #     f"Open: {record.open_price}, "
            #     f"Close: {record.close_price}, "
            #     f"High: {record.high_price}, "
            #     f"Low: {record.low_price}, "
            #     f"Volume: {record.volume}")
            result.append([
                record.minute_start,
                record.open_price,
                record.high_price,
                record.low_price,
                record.close_price,
                record.volume
            ])
        return result
    except Exception as e:
        print(e)
        return []


def is_daily_data_synced(dateStr):
    result = DailyTraderData.select().where(DailyTraderData.date == dateStr).exists()
    return result


def sync_daily_data(dateStr):
    EXCHANGE_NAME = {
        'sh': '上海',
        'zz': '郑州',
        'dl': '大连',
        'gz': '广州'
    }
    error_exchange = []
    max_retry = 5
    retry = 0
    while True:
        target = ['sh', 'zz', 'dl', 'gz'] if len(error_exchange) == 0 else [item for item in error_exchange]
        error_exchange = []
        for item in target:
            try:
                exchange = factory.getExchange(item)
                exchange.handle4DailyRecord(dateStr)
                print("同步" + EXCHANGE_NAME[item] + "交易信息完成")
            except Exception as e:
                print("同步" + EXCHANGE_NAME[item] + "交易信息出错")
                error_exchange.append(item)
                print(e)

        if len(error_exchange) == 0:
            break
        else:
            retry += 1
            if retry > max_retry:
                send_common_to_ding("同步数据出错，出错交易所：" + ','.join(error_exchange))
                break
            time.sleep(60)
            continue


def get_main_code_no():
    latest_item = DailyTraderData.select().order_by(DailyTraderData.date.desc()).limit(1).get()
    sub_query = DailyTraderData.select(DailyTraderData.symbol,
                                       fn.MAX(DailyTraderData.deal_vol).alias('max_deal_vol')).where(
        DailyTraderData.date == latest_item.date).group_by(DailyTraderData.symbol)
    query = DailyTraderData.select().join(sub_query, on=((DailyTraderData.symbol == sub_query.c.symbol) & (
            DailyTraderData.deal_vol == sub_query.c.max_deal_vol))).where(DailyTraderData.date == latest_item.date)
    # cur = database.cursor()
    # print(cur.mogrify(*query.sql()))
    return [item for item in query]


def save_forecast_item(item: DailyTraderData):
    days = 365  # 用来预测的天数
    data_list = DailyTraderData.select().where(
        (DailyTraderData.code_no == item.code_no) & (DailyTraderData.symbol == item.symbol)).limit(days).order_by(
        DailyTraderData.date.desc()
    )
    forecast_day = (data_list[0].date + datetime.timedelta(
        days=1)).strftime("%Y-%m-%d")
    exist = ForecastInterval.select().where((ForecastInterval.goods_code == item.symbol)
                                            & (ForecastInterval.goods_num == item.code_no)
                                            & (ForecastInterval.forecast_date == forecast_day)).exists()
    if exist:
        return item.goods + str(item.code_no) + " 不同步，因为数据已同步"

    df = [[item.date.strftime("%Y-%m-%d"), item.open_price, item.highest_price, item.lowest_price, item.close_price,
           item.deal_vol] for item in data_list]
    df.reverse()
    forecast, _ = calc_interval(df, is_minute=False)
    data = forecast.iloc[0].to_list()
    ForecastInterval.create(
        forecast_date=forecast_day,
        goods_code=item.symbol,
        goods_num=item.code_no,
        origin_price=data[1],
        p95_low_price=data[2],
        p80_low_price=data[3],
        p80_high_price=data[4],
        p95_high_price=data[5]
    )
    return item.goods + str(item.code_no) + " 同步成功"


def sync_main_code_minute_data(target, alert_data=None):
    exchange = factory.getExchange(target)
    # 获取数据列表
    data = exchange.crawl_data()
    # 检查
    if len(data) > 500:
        print("数据量过大，批处理不一定成功")
    save_data = []
    batch = len(data)
    for item in data:
        save_data.append(MinuteTradeData(**item))
        key = item["goods_code"] + str(item["contract_number"])
        current_price = item["current_price"]
        content = ''
        if key in alert_data:
            if current_price <= alert_data[key]["p95_low_price"]:
                content += ",低于日线级别95%置性区间内的最低值" + str(alert_data[key]["p95_low_price"])
            elif current_price <= alert_data[key]["p80_low_price"]:
                content += ",低于日线级别80%置性区间内的最低值" + str(alert_data[key]["p80_low_price"])
            elif current_price >= alert_data[key]["p95_high_price"]:
                content += ",高于日线级别95%置性区间内的最大值" + str(alert_data[key]["p95_high_price"])
            elif current_price >= alert_data[key]["p80_high_price"]:
                content += ",高于日线级别80%置性区间内的最大值" + str(alert_data[key]["p80_high_price"])
            if content != '':
                content += ("\n区间信息：\nP80[" + str(alert_data[key]["p80_low_price"])
                            + "-" + str(alert_data[key]["p80_high_price"]) + "]\nP95["
                            + str(alert_data[key]["p95_low_price"]) + "-"
                            + str(alert_data[key]["p95_high_price"]) + "]\n")
                send_common_to_ding("来自日线检查，合约" + key + "当前价格" + str(current_price) + content)

    # 批量落库
    with database.atomic():
        MinuteTradeData.bulk_create(save_data, batch_size=batch)
