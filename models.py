from peewee import *
import datetime
from dotenv import load_dotenv
import os
from playhouse.shortcuts import ReconnectMixin

load_dotenv()


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")

database = ReconnectMySQLDatabase('futures', user=db_user, password=db_password,
                                  host=db_host, port=3306)


def formatted_datetime_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def formatted_datetime_day():
    return datetime.datetime.now().strftime('%Y-%m-%d')


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Records(BaseModel):
    goods = TextField(null=True)
    origin_response = TextField(null=True)
    price = IntegerField(null=True)
    reasons = TextField(null=True)
    type = TextField(null=True)
    user_id = IntegerField(null=True)
    volume = IntegerField(null=True)
    create_time = DateTimeField(default=formatted_datetime_now)

    class Meta:
        table_name = 'records'


class Startup(BaseModel):
    uid = CharField()
    model_name = CharField()
    agent_name = CharField()

    class Meta:
        table_name = 'startup'


class Users(BaseModel):
    money = IntegerField(null=True)
    name = TextField(null=True, unique=True)
    status = TextField(null=True)

    class Meta:
        table_name = 'users'


class Userstatus(BaseModel):
    close = IntegerField(null=True)
    close_date = CharField(null=True)
    goods = CharField()
    is_clear = IntegerField(column_name='isClear')
    open_date = CharField(null=True)
    price = FloatField()
    profit = IntegerField(null=True)
    stop_loss = FloatField()
    take_profit = FloatField()
    type = CharField()
    user_id = CharField()
    volume = IntegerField()

    class Meta:
        table_name = 'userstatus'


class Goods(BaseModel):
    cn_name = CharField()
    name = CharField()

    class Meta:
        table_name = 'goods'


class GoodsPriceInSecond(BaseModel):
    uid = CharField()
    goods = CharField()
    current_price = FloatField()
    price_diff = FloatField()
    price_diff_percent = FloatField()
    open_price = FloatField()
    high_price = FloatField()
    low_price = FloatField()
    close_price = FloatField()
    have_vol = FloatField()
    deal_vol = FloatField()
    compute_price = FloatField()
    prev_compute_price = FloatField()
    buy_price_oncall = FloatField()
    sell_price_oncall = FloatField()
    buy_vol = FloatField()
    sell_vol = FloatField()
    price_time = DateTimeField()
    create_time = DateTimeField(default=formatted_datetime_now)

    class Meta:
        table_name = 'goodsPriceInSecond'


class Ip(BaseModel):
    ip = CharField()
    success_num = IntegerField(default=0)
    fail_num = IntegerField(default=0)
    status = CharField()
    cost_time = IntegerField(null=True)
    last_check_time = DateTimeField()
    create_time = DateTimeField(default=formatted_datetime_now)

    class Meta:
        table_name = 'ip'


class DailyAccount(BaseModel):
    account_name = CharField()
    value = FloatField()
    date = DateField(default=formatted_datetime_day)

    class Meta:
        table_name = 'daily_account'


class DailyTraderData(BaseModel):
    goods = CharField()
    code_no = IntegerField()
    date = DateField()
    open_price = FloatField()
    highest_price = FloatField()
    lowest_price = FloatField()
    close_price = FloatField()
    compute_price = FloatField()
    # 当日收盘价-前日结算
    diff1 = FloatField()
    # 当日结算-前日结算
    diff2 = FloatField()
    deal_vol = IntegerField()
    amount = FloatField()
    have_vol = IntegerField()
    # 涨幅为diff1/前日结算
    percent = FloatField(default=0)
    symbol = CharField()
    exchange = CharField()

    class Meta:
        table_name = 'daily_trade'
        indexes = (
            (("goods", "code_no", "date"), True),
        )


class ForecastInterval(BaseModel):
    goods_code = CharField()
    goods_num = IntegerField()
    forecast_date = DateField()
    create_time = DateTimeField(default=formatted_datetime_now)
    origin_price = FloatField()
    p95_low_price = FloatField()
    p80_low_price = FloatField()
    p80_high_price = FloatField()
    p95_high_price = FloatField()

    class Meta:
        table_name = 'forecast_interval'


class MinuteTradeData(BaseModel):
    goods_code = CharField()
    contract_number = CharField()
    open_price = FloatField()
    high_price = FloatField()
    low_price = FloatField()
    close_price = FloatField()
    deal_vol = FloatField()
    data_time = DateTimeField()
    create_time = DateTimeField(default=formatted_datetime_now)

    class Meta:
        table_name = 'minute_trade_data'

class Wenhua(BaseModel):
    name = TextField()
    new = FloatField()
    delta_price = FloatField()
    increase = FloatField()
    create_time = DateTimeField(default=formatted_datetime_now)
    class Meta:
        table_name = 'wenhua'

database.connect()
database.create_tables(
    [Wenhua, MinuteTradeData,ForecastInterval, DailyTraderData, DailyAccount, Startup, GoodsPriceInSecond, Records, Users, Userstatus, Goods, Ip])
