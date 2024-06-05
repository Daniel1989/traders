from db import add_record, query_users, update_user, UserStatus


def query_user():
    data = query_users()
    user = User(data[0], data[1], data[2], data[3])
    return user


def query_user_status_by_goods(user_id, goods):
    status = UserStatus.select().where(UserStatus.user_id.in_([user_id]) & UserStatus.goods.in_([goods]))
    result = {
        "buy": 0,
        "sell": 0
    }
    for item in status:
        result[item.type] = item.volume
    return result


def query_user_status_info_by_goods(user_id, goods):
    status = UserStatus.select().where(UserStatus.user_id.in_([user_id]) & UserStatus.goods.in_([goods]))
    if len(status) == 0:
        return None
    if len(status) > 1:
        raise Exception("多条" + goods + "持仓记录")
    return status[0]


class Action():
    def __init__(self, action, volume, reasons, origin_response, stop_loss=0, take_profit=0):
        self.action = action
        self.volume = volume
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reasons = reasons
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

        if action.action == 'close' or action.action == 'add':
            raise Exception("平仓加仓操作未实现")

        if self.money < 100:
            self.status = "dead"
        self.update()

    def add_record(self, action: Action, goods, current_price):
        add_record(self.id, goods, action.volume, current_price, action.action, action.reasons,
                   action.origin_response)

    def add_status(self, action, goods, current_price):
        status = UserStatus(user_id=self.id, goods=goods, volume=action.volume, price=current_price, type=action.action,
                            stop_loss=action.stop_loss, take_profit=action.take_profit)
        status.save()

    def update(self):
        update_user(self.id, self.name, self.money, self.status)
