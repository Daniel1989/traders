import json
import requests
from prompt import generate_prompt
import re
from user import Action, query_user, query_goods_status, query_user_status_info_by_goods
from llm.openai_gpt import OpenaiModel
from llm.ollama import Ollama
from llm.google_gpt import GoogleModel
from llm.baidu import BaiduModal
from llm.ali import AliModel
from llm.kimi import KimiModal
from llm.deepseek import DeepseekModal
from llm.coze import CozeModal
from llm.cn_coze import CnCozeModal
from llm.hunyuan import HunyuanModal
from llm.xunfei import XunfeiModel

llm = OpenaiModel("gpt-3.5-turbo") # 免费，可用
# llm = Ollama("llama3") # 免费，可用
# llm = GoogleModel("gemini-1.5-pro-latest")
# llm = BaiduModal("ernie-speed-128k") # 免费，可用
# llm = KimiModal("moonshot-v1-128k")
# llm = DeepseekModal("deepseek-chat")
# llm = CozeModal("") # use gpt4
# llm = CnCozeModal("") # totally free
# llm = HunyuanModal("hunyuan-lite") # hunyuan-pro
# llm = XunfeiModel("")

DEFALUT_POSITION = "empty"

def analyze(data, current_price, goods, max_shares_num, current_position=DEFALUT_POSITION, total_profit=0):
    current_loss = ''
    history_data = ''
    for item in data:
        history_data += f"date: {item[0]}, open: {item[1]}, high: {item[2]}, low: {item[3]}, close: {item[4]}, volume: {item[5]}\n"
    if llm.is_chinese:
        if total_profit != 0:
            current_loss = "当前持仓已经产生了" + str(total_profit) + "元的" + ("浮盈" if total_profit > 0 else "浮亏")
        direction = {
            "long": "看多",
            "short": "看空",
            "default": ""
        }
        curr_input = ["2024-04-17", current_price, "黄金创造历史新高",
                      "牛市", "短期收益", "高", goods, history_data, max_shares_num, direction[current_position], current_loss]
        prompt_lib_file = "prompt_template/ask_clear_action_cn.txt" if current_position != DEFALUT_POSITION else (
            "prompt_template/ask_action_cn.txt")
    else:
        if total_profit != 0:
            current_loss = "The current position has resulted in a " + (
                "profit" if total_profit > 0 else "loss") + " of " + str(total_profit) + " yuan for you."
        curr_input = ["2024-04-17", current_price, "gold create new history high price",
                      "bullish", "short-term profits", "high", goods, history_data, max_shares_num, current_position, current_loss]
        prompt_lib_file = "prompt_template/ask_clear_action.txt" if current_position != DEFALUT_POSITION else (
            "prompt_template/ask_action.txt")
        print("use prompt file", prompt_lib_file)

    prompt = generate_prompt(curr_input, prompt_lib_file)
    res = llm.do_prompt(prompt)
    print(res)
    try:
        matches = re.findall(r'\{([^{}]*)\}', res)
        cleaned_json_string = re.sub(r'//.*', '', matches[0])
        json_data = json.loads("{" + cleaned_json_string + "}")
        json_data["origin_response"] = res
        return Action(**json_data)

    except Exception as error:
        print("解析出错")
        print(error)
        raise error


def do_action(daily, goods, data, retry_num=0):
    current_price = float(daily[4])
    user = query_user()
    status = query_goods_status(user.id, goods)
    current_status = query_user_status_info_by_goods(user.id, goods)
    current_position = DEFALUT_POSITION
    total_profit = 0
    is_force_close = False

    if status["buy"] > 0 or status["sell"] > 0:
        max_shares_num = max(status["buy"], status["sell"])
        actual_vol = current_status.volume * 10  # 杠杆系数设置为10
        total_profit = (current_price - current_status.price) * actual_vol * (1 if current_status.type == 'buy' else -1)
        print("当前收益: ", total_profit)
        left_money = user.money + total_profit
        print("当前剩余可用资金: ", left_money)
        print("当前总资产: ", current_price * current_status.volume + left_money)

        # 是否人工强平
        current_position = "long" if status["buy"] > 0 else "short"
        if left_money < -1000:
            action = Action('close', max_shares_num, "low money", "", 0, 0)
            user.action(action, goods, current_price)
            is_force_close = True
        elif current_status.type == 'buy':
            if current_price >= current_status.take_profit:
                action = Action('close', max_shares_num, "react to take profit", "", 0, 0)
                user.action(action, goods, current_price)
                is_force_close = True

            elif current_price <= current_status.stop_loss:
                action = Action('close', max_shares_num, "react to stop loss", "", 0, 0)
                user.action(action, goods, current_price)
                is_force_close = True

        elif current_status.type == 'sell':
            if current_price <= current_status.take_profit:
                action = Action('close', max_shares_num, "react to take profit", "", 0, 0)
                user.action(action, goods, current_price)
                is_force_close = True

            elif current_price >= current_status.stop_loss:
                action = Action('close', max_shares_num, "react to stop loss", "", 0, 0)
                user.action(action, goods, current_price)
                is_force_close = True
    else:
        max_shares_num = user.money // current_price
        if max_shares_num < 1:
            print("买一手的钱都没有了:(")
            # TODO 这里需要更新用户状态为死亡
            return

    try:
        if is_force_close:
            # 强平后仓位重设为empty
            current_position = DEFALUT_POSITION
        action = analyze(data, current_price, goods, max_shares_num, current_position, total_profit)
        user.action(action, goods, current_price)
    except Exception as e:
        if retry_num < 5:
            print("分析出错，重试", e)
            retry_num += 1
            do_action(daily, goods, data, retry_num)
        else:
            print("重试五次都失败，跳过")


if __name__ == '__main__':
    if llm.is_chinese:
        name = "白银"
    else:
        name = "silver"
    url = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=ag2408"
    history = requests.get(url).json()
    history_data_len = 5
    last5Days = []
    for index, item in enumerate(history):

        if len(last5Days) == history_data_len:
            vol = [float(d[5]) for d in last5Days]
            mean_vol = sum(vol) / history_data_len
            if mean_vol > float(item[5]) * 5:
                print("交易量不到5分之一, 可疑日期，跳过", item)
                continue
            last5Days.pop(0)
            last5Days.append(item)
            if 180 < index:
                print("开始分析 ", item[0])
                do_action(item, name, last5Days)
        else:
            last5Days.append(item)

