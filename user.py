from models import Records, Users, Userstatus


def query_user():
    data = Users.select()[0]
    user = User(data.id, data.name, data.money, data.status)
    return user


def query_goods_status(user_id, goods):
    status = Userstatus.select().where(Userstatus.user_id.in_([user_id]) & Userstatus.goods.in_([goods]) & (Userstatus.is_clear == 0))
    result = {
        "buy": 0,
        "sell": 0
    }
    for item in status:
        result[item.type] = item.volume
    return result


def query_user_status_info_by_goods(user_id, goods):
    status = Userstatus.select().where(Userstatus.user_id.in_([user_id]) & Userstatus.goods.in_([goods]) & (Userstatus.is_clear == 0))
    if len(status) == 0:
        return None
    if len(status) > 1:
        raise Exception("多条" + goods + "持仓记录")
    return status[0]


class Action():
    def __init__(self, action, volume, reason, origin_response, stop_loss=0, take_profit=0):
        self.action = action
        self.volume = volume
        self.stop_loss = stop_loss or 0
        self.take_profit = take_profit or 0
        self.reasons = reason
        self.origin_response = origin_response


class User():
    def __init__(self, id, name, money, status):
        self.id = id
        self.name = name
        self.money = money
        self.status = status

    def action(self, action: Action, goods, current_price):
        if action.action == 'hold':
            self.add_record(action, goods, current_price)
            return
        if action.action == 'sell' or action.action == 'buy':
            self.add_record(action, goods, current_price)
            self.add_status(action, goods, current_price)
            self.money -= action.volume * current_price

        if action.action == 'close':
            self.add_record(action, goods, current_price)
            current_status = query_user_status_info_by_goods(self.id, goods)
            total_profit = (current_price - current_status.price) * current_status.volume * (
                1 if current_status.type == 'buy' else -1) * 10  # 杠杆系数设置为10
            self.update_status(action, goods, current_price)
            print("平仓，收益为: ", total_profit, "，剩余资金为: ", self.money)
            self.money += total_profit + action.volume * current_status.price
            print("结算资金为: ", self.money)


        if action.action == 'add':
            self.add_record(action, goods, current_price)
            self.update_status(action, goods, current_price)
            self.money -= action.volume * current_price


        # if self.money < 100:
        #     self.status = "dead"
        self.update()

    def add_record(self, action: Action, goods, current_price):
        records = Records(user_id=self.id, goods=goods, volume=action.volume, price=current_price, type=action.action, origin_response=action.origin_response, reasons="\n".join(action.reasons))
        records.save()

    def add_status(self, action, goods, current_price):
        status = Userstatus(user_id=self.id, goods=goods, volume=action.volume, price=current_price, type=action.action,
                            stop_loss=action.stop_loss, take_profit=action.take_profit, is_clear=0)
        status.save()

    def update_status(self, action, goods, current_price):
        current_status = query_user_status_info_by_goods(self.id, goods)
        if action.action == 'close':
            current_status.is_clear = 1
            current_status.save()
        else:
            total = current_status.price * current_status.volume + action.volume * current_price
            current_status.volume += action.volume
            current_status.price = total / current_status.volume
            current_status.stop_loss = action.stop_loss
            current_status.take_profit = action.take_profit
            current_status.save()

    def update(self):
        user = Users.select().where(Users.id == self.id)[0]
        user.name = self.name
        user.money = self.money
        user.status = self.status
        user.save()
