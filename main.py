import json
import requests
from prompt import generate_prompt
import re
from user import Action, query_user, query_user_status_by_goods, query_user_status_info_by_goods
from models.openai_gpt import OpenaiModel
from models.ollama import Ollama
from models.google_gpt import GoogleModel
from models.baidu import BaiduModal
from models.ali import AliModel
from models.kimi import KimiModal
from models.deepseek import DeepseekModal
from models.coze import CozeModal
from models.cn_coze import CnCozeModal
from models.hunyuan import HunyuanModal
from models.xunfei import XunfeiModel

# llm = OpenaiModel("gpt-3.5-turbo")
# llm = Ollama("llama3")
# llm = GoogleModel("gemini-1.5-pro-latest")
llm = BaiduModal("ernie-speed-128k")
# llm = KimiModal("moonshot-v1-128k")
# llm = DeepseekModal("deepseek-chat")
# llm = CozeModal("") # use gpt4
# llm = CnCozeModal("") # totally free
# llm = HunyuanModal("hunyuan-lite") # hunyuan-pro
# llm = XunfeiModel("")

def analyze(data, current_price, goods, max_shares_num, current_position='default', total_profit=0):
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
        prompt_lib_file = "prompt_template/ask_clear_action_cn.txt" if current_position != 'default' else (
            "prompt_template/ask_action_cn.txt")
    else:
        if total_profit != 0:
            current_loss = "The current position has resulted in a " + (
                "profit" if total_profit > 0 else "loss") + " of " + str(total_profit) + " yuan for you."
        curr_input = ["2024-04-17", current_price, "gold create new history high price",
                      "bullish", "short-term profits", "high", goods, history_data, max_shares_num, current_position, current_loss]
        prompt_lib_file = "prompt_template/ask_clear_action.txt" if current_position != 'default' else (
            "prompt_template/ask_action.txt")

    prompt = generate_prompt(curr_input, prompt_lib_file)
    res = llm.do_prompt(prompt)
    print(res)
    matches = re.findall(r'\{([^{}]*)\}', res)
    json_data = json.loads("{" + matches[0] + "}")
    json_data["origin_response"] = res
    return Action(**json_data)


def do_action(daily, goods, data):
    current_price = float(daily[4])
    user = query_user()
    status = query_user_status_by_goods(user.id, goods)
    current_status = query_user_status_info_by_goods(user.id, goods)
    current_position = 'default'
    total_profit = 0
    if status["buy"] > 0 or status["sell"] > 0:
        max_shares_num = max(status["buy"], status["sell"])
        total_profit = (current_price - current_status.price) * current_status.volume * (1 if current_status.type == 'buy' else -1)
        # TODO 如果损失结合当前的资金已为负数，则必须强平（后续调整这个负数）
        current_position = "long" if status["buy"] > 0 else "short"
    else:
        max_shares_num = user.money // current_price
        if max_shares_num < 1:
            print("Not enough money")
            return

    action = analyze(data, current_price, goods, max_shares_num, current_position, total_profit)
    user.action(action, goods, current_price)


if __name__ == '__main__':
    if llm.is_chinese:
        name = "白银"
    else:
        name = "silver"
    url = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=ag2406"
    history = requests.get(url).json()
    last5Days = []
    for index, item in enumerate(history):
        if len(last5Days) > 5:
            last5Days.pop(0)
        last5Days.append(item)
        if 100 < index:
            print("start ", index)
            do_action(item, name, last5Days)

