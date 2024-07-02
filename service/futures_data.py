from models import GoodsPriceInSecond, database
from peewee import fn, Select
from datetime import datetime


def get_goods_minute_data(code):
    try:
        inner = GoodsPriceInSecond.select(
            GoodsPriceInSecond.uid,
            GoodsPriceInSecond.deal_vol,
            GoodsPriceInSecond.price_time,
            GoodsPriceInSecond.current_price.alias('current_price'),
            fn.DATE_FORMAT(GoodsPriceInSecond.price_time, '%Y-%m-%d %H:%i').alias('minute_start'),
        ).where(GoodsPriceInSecond.uid == code).order_by(GoodsPriceInSecond.price_time.desc()).limit(5000).alias('inner')

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
        ).from_(last_price).join(first_price, on=(last_price.c.minute_start == first_price.c.minute_start)))

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
