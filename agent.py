import json
import traceback

from prompt import generate_prompt
import re

from service.fpp3 import calc_interval
from service.futures_data import get_goods_minute_data
from user import Action, query_user, query_goods_status, query_user_status_info_by_goods, User
from constants.model import DEFAULT_POSITION, RATION
import matplotlib.pyplot as plt
import pandas as pd
from models import Users
import uuid

from util.cache import request
from util.notify import send_common_to_ding


class Agent:
    def __init__(self, model, name=None):
        self.name = model.model_name + "@" + str(uuid.uuid4()) if name is None else name
        self.modal_name = model.model_name
        self.llm = model
        self.history = []
        print("agent init", self.name)
        user = self.get_user(name)

    def get_user(self, name):
        if name is None:
            user = Users(money=100000, name=self.name, status="alive")
            user.save()
            return user
        return query_user(name)

    def handler(self):
        if self.llm.is_chinese:
            name = "白银"
        else:
            name = "silver"
        try:
            self.do_action(name)
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            print("分析出错，跳过", self.name)

        return self.history

    def save_img(self):
        df = pd.DataFrame(self.history)
        # Convert the 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])
        # Plot the data
        plt.figure(figsize=(20, 6))
        plt.plot(df['date'], df[self.name], marker='o', label=self.name)
        # plt.plot(df['date'], df['v2'], marker='s', label='v2')

        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.title('account trend')
        plt.legend()
        plt.grid(True)
        plt.savefig('plot.png')
        plt.close()

    def get_interval_statement(self, minute_history_data, history_daily_data):
        minute_result, _ = calc_interval(minute_history_data[:-1], is_minute=True)
        daily_result, _ = calc_interval(history_daily_data, is_minute=False)
        p80_min = min(minute_result.iloc[:, 2].to_list())
        p80_max = max(minute_result.iloc[:, 5].to_list())
        p95_min = min(minute_result.iloc[:, 3].to_list())
        p95_max = max(minute_result.iloc[:, 4].to_list())
        s1 = ("基于近一年的每日收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对今日收盘价格进行预测，"
              "得到80%的置性区间为：[" + str(daily_result.iloc[0][3]) + ", " + str(daily_result.iloc[0][4]) + "]。"
                                                                                                             "95%的置性区间为：[" + str(
            daily_result.iloc[0][2]) + ", " + str(daily_result.iloc[0][5]) + "]。")

        s2 = ("基于最近6个小时内的每分钟收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对接下去的一小时内的每分钟收盘价格进行预测，"
              "得到结果如下，有80%的可能价格在[" + str(p80_min) + ", " + str(p80_max) + "]的区间内变动,"
                                                                                       "95%的的可能价格在[" + str(
            p95_min) + ", " + str(p95_max) + "]的区间内变动。")
        return s1 + "同时，" + s2 + "\n"

    def forecast_check(self, minute_history_data, history_daily_data):
        today = minute_history_data[len(minute_history_data) - 1]
        current_price = today[4]

        minute_result, _ = calc_interval(minute_history_data[:-1], is_minute=True)
        daily_result, _ = calc_interval(history_daily_data, is_minute=False)
        p80_min = min(minute_result.iloc[:, 2].to_list())
        p80_max = max(minute_result.iloc[:, 5].to_list())
        p95_min = min(minute_result.iloc[:, 3].to_list())
        p95_max = max(minute_result.iloc[:, 4].to_list())
        content = '白银当前价格' + str(current_price)
        need_send = True
        if current_price <= daily_result.iloc[0][2]:
            content += ",低于日线级别95%置性区间内的最低值" + str(daily_result.iloc[0][2])
        elif current_price <= daily_result.iloc[0][3]:
            content += ",低于日线级别80%置性区间内的最低值" + str(daily_result.iloc[0][3])
        elif current_price >= daily_result.iloc[0][5]:
            content += ",高于日线级别95%置性区间内的最大值" + str(daily_result.iloc[0][5])
        elif current_price >= daily_result.iloc[0][4]:
            content += ",高于日线级别80%置性区间内的最大值" + str(daily_result.iloc[0][4])
        elif current_price <= p95_min:
            content += ",低于分钟级别95%置性区间内的最低值" + str(p95_min)
        elif current_price <= p80_min:
            content += ",低于分钟级别80%置性区间内的最低值" + str(p80_min)
        elif current_price >= p95_max:
            content += ",高于分钟级别95%置性区间内的最大值" + str(p95_max)
        elif current_price >= p80_max:
            content += ",高于分钟级别80%置性区间内的最大值" + str(p80_max)
        else:
            need_send = False
        content += "\n区间值详细信息如下:\n"
        content += "日线80%区间: [" + str(daily_result.iloc[0][3]) + ", " + str(daily_result.iloc[0][4]) + "]\n"
        content += "日线95%区间: [" + str(daily_result.iloc[0][2]) + ", " + str(daily_result.iloc[0][5]) + "]\n"
        content += "分钟线80%区间: [" + str(p80_min) + ", " + str(p80_max) + "]\n"
        content += "分钟线95%区间: [" + str(p95_min) + ", " + str(p95_max) + "]\n"

        if need_send:
            send_common_to_ding(content)

    def analyze(self, minute_history_data, history_daily_data, daily, goods, max_shares_num,
                current_position=DEFAULT_POSITION,
                total_profit=0):
        daily_data = history_daily_data[-10:]
        data = minute_history_data[-61:-1]
        current_price = float(daily[4])
        current_loss = ''
        history_data = ''
        daily_history_data = ''
        for item in data:
            history_data += f"date: {item[0]}, open: {item[1]}, high: {item[2]}, low: {item[3]}, close: {item[4]}, volume: {item[5]}\n"
        for item in daily_data:
            daily_history_data += f"date: {item[0]}, open: {item[1]}, high: {item[2]}, low: {item[3]}, close: {item[4]}, volume: {item[5]}\n"
        forecast_result = self.get_interval_statement(minute_history_data, history_daily_data)
        if self.llm.is_chinese:
            if total_profit != 0:
                current_loss = "当前持仓已经产生了" + str(total_profit) + "元的" + (
                    "浮盈" if total_profit > 0 else "浮亏")
            direction = {
                "long": "看多",
                "short": "看空",
                "empty": ""
            }
            curr_input = [daily[0], current_price, "黄金创造历史新高",
                          "牛市", "短期收益", "高", goods, history_data, max_shares_num, direction[current_position],
                          current_loss, daily_history_data, forecast_result]
            prompt_lib_file = "prompt_template/ask_clear_action_cn.txt" if current_position != DEFAULT_POSITION else (
                "prompt_template/ask_action_cn.txt")
        else:
            if total_profit != 0:
                current_loss = "The current position has resulted in a " + (
                    "profit" if total_profit > 0 else "loss") + " of " + str(total_profit) + " yuan for you."
            curr_input = [daily[0], current_price, "gold create new history high price",
                          "bullish", "short-term profits", "high", goods, history_data, max_shares_num,
                          current_position,
                          current_loss, daily_history_data]
            prompt_lib_file = "prompt_template/ask_clear_action.txt" if current_position != DEFAULT_POSITION else (
                "prompt_template/ask_action.txt")
            print("use prompt file", prompt_lib_file)

        prompt = generate_prompt(curr_input, prompt_lib_file)
        res = self.llm.do_prompt(prompt)

        try:
            matches = re.findall(r'\{([^{}]*)\}', res)
            cleaned_json_string = re.sub(r'//.*', '', matches[0])
            json_data = json.loads("{" + cleaned_json_string + "}")
            json_data["origin_response"] = res
            json_data["date_str"] = daily[0]
            return Action(**json_data)

        except Exception as error:
            print("解析出错")
            print(error)
            raise error

    def do_action(self, goods):
        try:
            url = (
                "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol"
                "=ag2408")
            daily_history = request(url)
        except Exception as e:
            print(e)
            return
        minute_history = get_goods_minute_data('AG2408')
        # 这里插一个钉钉通知
        if self.modal_name == 'doubao':
            self.forecast_check(minute_history, daily_history)

        if len(minute_history) > 60:
            return

        current_item = minute_history[len(minute_history) - 1]
        current_price = float(current_item[4])
        current_time = current_item[0]

        user = query_user(self.name)
        status = query_goods_status(user.id, goods)
        current_status = query_user_status_info_by_goods(user.id, goods)
        current_position = DEFAULT_POSITION
        total_profit = 0
        is_force_close = False

        if status["buy"] > 0 or status["sell"] > 0:
            max_shares_num = max(status["buy"], status["sell"])
            total_profit = (current_price - current_status.price) * current_status.volume * (
                1 if current_status.type == 'buy' else -1) * RATION
            left_money = user.money + total_profit
            print("当前剩余可用资金: ", user.money)
            print("当前收益: ", total_profit)
            print("当前总资产: ", current_status.price * current_status.volume + left_money)
            self.history.append({
                "date": current_time,
                self.name: current_status.price * current_status.volume + left_money
            })
            # 是否人工强平
            current_position = "long" if status["buy"] > 0 else "short"
            if left_money < -1000:
                print("账面可用资金为负，触发强制平仓，资金为：", left_money)
                action = Action('close', max_shares_num, ["low money"], "", 0, 0, current_time)
                user.action(action, goods, current_price)
                is_force_close = True
            elif current_status.type == 'buy':
                if current_price >= current_status.take_profit:
                    print("达到止盈位，触发强制平仓，资金为：", left_money)
                    action = Action('close', max_shares_num, ["react to take profit"], "", 0, 0, current_time)
                    user.action(action, goods, current_price)
                    is_force_close = True

                elif current_price <= current_status.stop_loss:
                    print("达到止损位，触发强制平仓，资金为：", left_money)
                    action = Action('close', max_shares_num, ["react to stop loss"], "", 0, 0, current_time)
                    user.action(action, goods, current_price)
                    is_force_close = True

            elif current_status.type == 'sell':
                if current_price <= current_status.take_profit:
                    print("达到止盈位，触发强制平仓，资金为：", left_money)
                    action = Action('close', max_shares_num, ["react to take profit"], "", 0, 0, current_time)
                    user.action(action, goods, current_price)
                    is_force_close = True

                elif current_price >= current_status.stop_loss:
                    print("达到止损位，触发强制平仓，资金为：", left_money)
                    action = Action('close', max_shares_num, ["react to stop loss"], "", 0, 0, current_time)
                    user.action(action, goods, current_price)
                    is_force_close = True
        else:
            self.history.append({
                "date": current_time,
                self.name: user.money
            })
            max_shares_num = user.money // current_price
            if max_shares_num < 1:
                print("买一手的钱都没有了:(")
                # TODO 这里需要更新用户状态为死亡
                return

        try:
            if is_force_close:
                # 强平后仓位重设为empty
                # 强平后重新查询可用资金
                current_position = DEFAULT_POSITION
                user = query_user(self.name)
                max_shares_num = user.money // current_price
                if max_shares_num < 1:
                    print("买一手的钱都没有了:(")
                    # TODO 这里需要更新用户状态为死亡
                    return
            action = self.analyze(minute_history, daily_history, current_item, goods, max_shares_num, current_position,
                                  total_profit)
            user.action(action, goods, current_price)
        except Exception as e:
            raise e
