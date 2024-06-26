from peewee import *
import datetime

database = SqliteDatabase('traders.db')


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class LlmConfig(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'LLMConfig'


class Records(BaseModel):
    goods = TextField(null=True)
    origin_response = TextField(null=True)
    price = IntegerField(null=True)
    reasons = TextField(null=True)
    type = TextField(null=True)
    user_id = IntegerField(null=True)
    volume = IntegerField(null=True)

    class Meta:
        table_name = 'records'


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


class PriceRecord(BaseModel):
    goods = CharField()
    price = FloatField()
    date = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    type = CharField()
    timestamp = CharField(null=True)

    class Meta:
        table_name = 'priceRecord'


class Ip(BaseModel):
    ip = CharField()
    success_num = IntegerField(default=0)
    fail_num = IntegerField(default=0)
    status = CharField()
    cost_time = IntegerField(null=True)
    last_check_time = DateTimeField()
    create_time = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    class Meta:
        table_name = 'ip'


database.connect()
database.create_tables([Records, Users, Userstatus, LlmConfig, Goods, PriceRecord, Ip])
