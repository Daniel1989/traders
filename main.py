import requests
from user import reset
from agent import Agent

from llm.openai_gpt import OpenaiModel
from llm.llama import Ollama
from llm.google_gpt import GoogleModel
from llm.baidu import BaiduModal
from llm.ali import AliModel
from llm.kimi import KimiModal
from llm.deepseek import DeepseekModal
from llm.coze import CozeModal
from llm.cn_coze import CnCozeModal
from llm.hunyuan import HunyuanModal
from llm.xunfei import XunfeiModel
from llm.volc import DoubaoModel

from concurrent.futures import ProcessPoolExecutor, TimeoutError

import matplotlib.pyplot as plt
import pandas as pd

gpt = OpenaiModel("gpt-3.5-turbo")  # 免费，可用，评分为基准60分
llama = Ollama("llama3")  # 免费，可用, 评分为75分
# llm3 = GoogleModel("gemini-1.5-pro-latest") # 不免费，目前不可用了
# llm4 = BaiduModal("ernie-speed-128k") # 免费，可用，评分为40分
ali = AliModel("qwen-max")  # 不免费，但是阿里云付费，可用，评分为75分
# llm6 = KimiModal("moonshot-v1-128k") # 不免费，可用，有赠送的代金劵可用，有RPM为3的限制，需要每个请求sleep30秒，评分为35分
deepseek = DeepseekModal("deepseek-chat")  # 不免费，可用，有送的，评分为60分
coze = CozeModal("coze")  # use gpt4 # 不免费，不可用，赠送的token已用光，评分为70分
cncoze = CnCozeModal("cncoze")  # # 免费，可用，评分为70分，个人感觉用的就是gpt4吧？
# llm10 = HunyuanModal("hunyuan-lite") # 免费，但是弱智，返回的值乱写 评分为0分. hunyuan-pro有送，但是也弱智
# llm11 = XunfeiModel("xunfei") # lite免费，3.5有送的，但是，全部都是弱智，vol乱写，评分为0分
doubao = DoubaoModel("doubao")  # 不免费，有赠送，但是收费很便宜，可以很低，评分65
# llm_list = [gpt, llama, cncoze, ali, deepseek, doubao]
llm_list = [ali]


# 目前看，gpt3.5，扣子中文，llama3，阿里云，扣子，DeepseekModal，DoubaoModel
# 其中阿里云，扣子，DeepseekModal，DoubaoModel收费，要小心，但是阿里云和doubao没有找到明显的收费的地方


def item_exists(data_list, field, value):
    return any(item[field] == value for item in data_list)


def merge_lists(lists, key='date'):
    merged_dict = {}

    for lst in lists:
        for item in lst:
            item_id = item[key]
            if item_id not in merged_dict:
                merged_dict[item_id] = item
            else:
                # If the same ID exists, merge the dictionaries, prioritizing the existing fields
                for k, v in item.items():
                    if k not in merged_dict[item_id]:
                        merged_dict[item_id][k] = v

    # Convert merged_dict back to a list of dictionaries
    merged_list = list(merged_dict.values())
    return merged_list


def save_img(data):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    plt.figure(figsize=(20, 6))
    for key in df.columns:
        if key != 'date':
            plt.plot(df['date'], df[key], marker='o', label=key)

    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.title('account trend')
    plt.legend()
    plt.grid(True)
    plt.savefig('plot.png')
    plt.close()


def execution(agent_name, data):
    llm = [item for item in llm_list if item.model_name == agent_name][0]
    agent = Agent(llm)
    return agent.handler(data)


if __name__ == '__main__':
    reset()
    results = []
    url = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=ag2408"
    # url = "https://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=ag2408"
    history = requests.get(url).json()

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(execution, item.model_name, history) for item in llm_list if item.model_name != 'llama3']
        for future in futures:
            try:
                result = future.result(timeout=10000000)  # Wait for all processes to complete
                results.append(result)    # Append the result to the list
            except TimeoutError:
                print(f"Timeout occurred for a task.")

    # llama3 比较特殊，不知道为什么使用线程池失败
    # results.append(execution("llama3", history))
    all_history = merge_lists([item for item in results])
    save_img(all_history)
