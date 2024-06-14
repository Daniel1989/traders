from peewee import *

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
    goods = CharField()
    is_clear = IntegerField(column_name='isClear')
    price = FloatField()
    stop_loss = FloatField()
    take_profit = FloatField()
    type = CharField()
    user_id = CharField()
    volume = IntegerField()

    class Meta:
        table_name = 'userstatus'

