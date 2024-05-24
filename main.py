import json

from prompt import generate_prompt
import re
from user import Action, query_user
from models.openai_gpt import OpenaiModel
from models.ollama import Ollama
from models.google_gpt import GoogleModel
from models.baidu import BaiduModal
from models.ali import AliModel
from models.kimi import KimiModal
from models.deepseek import DeepseekModal
# from models.coze import CozeModal 不可用

# llm = OpenaiModel("gpt-3.5-turbo")
# llm = Ollama("llama3")
# llm = GoogleModel("gemini-1.5-pro-latest")
# llm = BaiduModal("ernie-speed-128k")
# llm = KimiModal("moonshot-v1-128k")
llm = DeepseekModal("deepseek-chat")

def analyze(current_price, goods, max_shares_num):
    data = [
        {
            "date": "2024-04-10",
            "open": 7223,
            "high": 7271,
            "low": 7135,
            "close": 7204,
            "volume": 1999764
        },
        {
            "date": "2024-04-11",
            "open": 7177,
            "high": 7261,
            "low": 7088,
            "close": 7164,
            "volume": 2207334
        },
        {
            "date": "2024-04-12",
            "open": 7192,
            "high": 7479,
            "low": 7146,
            "close": 7472,
            "volume": 1980210
        },
        {
            "date": "2024-04-15",
            "open": 7497,
            "high": 7790,
            "low": 7303,
            "close": 7436,
            "volume": 4756248
        },
        {
            "date": "2024-04-16",
            "open": 7490,
            "high": 7508,
            "low": 7320,
            "close": 7368,
            "volume": 2717032
        }
    ]
    history = ''
    for item in data:
        history += f"date: {item['date']}, open: {item['open']}, high: {item['high']}, low: {item['low']}, close: {item['close']}, volume: {item['volume']}\n"

    if llm.is_chinese:
        curr_input = ["2024-04-17", current_price, "黄金创造历史新高",
                      "牛市", "短期收益", "高", goods, history, max_shares_num]
        prompt_lib_file = "prompt_template/ask_action_cn.txt"
        prompt = generate_prompt(curr_input, prompt_lib_file)
    else:
        curr_input = ["2024-04-17", current_price, "gold create new history high price",
                      "bullish", "short-term profits", "high", goods, history, max_shares_num]
        prompt_lib_file = "prompt_template/ask_action.txt"
        prompt = generate_prompt(curr_input, prompt_lib_file)
    res = llm.do_prompt(prompt)
    print(res)
    matches = re.findall(r'\{([^{}]*)\}', res)
    json_data = json.loads("{" + matches[0] + "}")
    json_data["origin_response"] = res
    return Action(**json_data)


def do_action():
    if llm.is_chinese:
        goods = "白银"
    else:
        goods = "silver"
    # get user available money
    # TODO 持有仓位，则使用不同的prompt

    # 空仓，则使用买入，卖出，观察三种操作的某一个
    user = query_user()
    current_price = 7361
    max_shares_num = user.money // current_price
    if max_shares_num < 1:
        print("Not enough money")
        # TODO 钱不够了，是否要平一些
        return

    action = analyze(current_price, goods, max_shares_num)
    user.action(action, goods, current_price)


if __name__ == '__main__':
    do_action()
