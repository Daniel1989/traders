from db import add_record, query_users, update_user


def query_user():
    data = query_users()
    user = User(data[0], data[1], data[2], data[3])
    return user


class Action():
    def __init__(self, action, volume, stop_loss, take_profit, reasons, origin_response):
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
            return
        # TODO 要添加平仓逻辑
        self.add_record(action, goods, current_price)
        self.money -= action.volume * current_price
        if self.money < 100:
            self.status = "dead"
        self.update()
        # TODO 添加持仓状态

    def add_record(self, action: Action, goods, current_price):
        add_record(self.id, goods, action.volume, current_price, action.action, action.reasons,
                   action.origin_response)

    def update(self):
        update_user(self.id, self.name, self.money, self.status)
