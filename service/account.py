import datetime

from models import Users, Userstatus, database, GoodsPriceInSecond, Goods, DailyAccount


def query_goods_current_price(goods_name):
    goods = Goods.select().where(Goods.cn_name == goods_name).get()
    data = GoodsPriceInSecond.select(GoodsPriceInSecond.current_price).where(
        GoodsPriceInSecond.goods == goods.id).order_by(GoodsPriceInSecond.price_time.desc()).limit(1).get()
    return data


def daily_count():
    query = Users.select(Userstatus.volume, Users.money, Userstatus.goods, Users.name).left_outer_join(Userstatus, on=(Users.id == Userstatus.user_id) & (Userstatus.close.is_null()))
    # 获取每个资产收盘价格
    # 将资产*收盘价格*数量 + 账户资产
    users = {}
    # cur = database.cursor()
    # print(cur.mogrify(*query.sql()))
    # print(len(query))
    for item in query:
        if item.name not in users:
            users[item.name] = item.money
        try:
            goods_price = query_goods_current_price(item.userstatus.goods)
            users[item.name] += goods_price.current_price * item.userstatus.volume
        except Exception as e:
            print(item.name + str(e))
    for key in users:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        today_record = DailyAccount.select().where(DailyAccount.account_name == key, DailyAccount.date == today)
        if len(today_record) > 0:
            print("已存在")
        else:
            daily = DailyAccount(account_name=key, value=users[key], date=today)
            daily.save()

