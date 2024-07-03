import time
import requests
from models import Startup
from service.account import daily_count
from agent import Agent
import datetime
import uuid

# from llm.openai_gpt import OpenaiModel
# from llm.llama import Ollama
# from llm.google_gpt import GoogleModel
# from llm.baidu import BaiduModal
from llm.ali import AliModel
# from llm.kimi import KimiModal
# from llm.deepseek import DeepseekModal
# from llm.coze import CozeModal
from llm.cn_coze import CnCozeModal
# from llm.hunyuan import HunyuanModal
# from llm.xunfei import XunfeiModel
from llm.volc import DoubaoModel

from service.futures_data import get_goods_minute_data
from concurrent.futures import ProcessPoolExecutor, TimeoutError

from util.utils import is_trade_time, is_sync_time

# gpt = OpenaiModel("gpt-3.5-turbo")  # 免费，可用，评分为基准60分
# llama = Ollama("llama3")  # 免费，可用, 评分为75分
# google = GoogleModel("gemini-1.5-pro-latest") # 不免费，目前不可用了
# baidu = BaiduModal("ernie-speed-128k") # 免费，可用，评分为40分
ali = AliModel("qwen-max")  # 不免费，但是阿里云付费，可用，评分为75分
# kimi = KimiModal("moonshot-v1-128k") # 不免费，可用，有赠送的代金劵可用，有RPM为3的限制，需要每个请求sleep30秒，评分为35分
# deepseek = DeepseekModal("deepseek-chat")  # 不免费，可用，有送的，评分为60分
# coze = CozeModal("coze")  # use gpt4 # 不免费，不可用，赠送的token已用光，评分为70分
cncoze = CnCozeModal("cncoze")  # # 免费，可用，评分为70分，个人感觉用的就是gpt4吧？
# hunyuan = HunyuanModal("hunyuan-lite") # 免费，但是弱智，返回的值乱写 评分为0分. hunyuan-pro有送，但是也弱智
# xunfei = XunfeiModel("xunfei") # lite免费，3.5有送的，但是，全部都是弱智，vol乱写，评分为0分
doubao = DoubaoModel("doubao")  # 不免费，有赠送，但是收费很便宜，可以很低，评分65
llm_list = [cncoze, ali, doubao]


# 目前看，gpt3.5，扣子中文，llama3，阿里云，扣子，DeepseekModal，DoubaoModel
# 其中阿里云，扣子，DeepseekModal，DoubaoModel收费，要小心，但是阿里云和doubao没有找到明显的收费的地方


def item_exists(data_list, field, value):
    return any(item[field] == value for item in data_list)


def execution(startup_uid, agent_name, data, daily_data):
    llm = [item for item in llm_list if item.model_name == agent_name][0]
    agent_list = Startup.select().where(Startup.uid == startup_uid, Startup.model_name == llm.model_name)
    if len(agent_list) > 0:
        agent_name = agent_list[0].agent_name
        agent = Agent(llm, agent_name)
    else:
        agent = Agent(llm)
        startup_agent = Startup(uid=startup_uid, model_name=llm.model_name, agent_name=agent.name)
        startup_agent.save()
    return agent.handler(data, daily_data)


if __name__ == '__main__':
    # reset()
    startup_id = str(uuid.uuid4())
    results = []
    daily_history_temp = []
    while True:
        today = datetime.date.today()
        if today.weekday() == 5 or today.weekday() == 6:
            time.sleep(5 * 60)
            continue
        if not is_trade_time():
            if is_sync_time():
                daily_count()
            time.sleep(5 * 60)
            continue
        history = get_goods_minute_data('AG2408')
        history.reverse()
        try:
            url = (
                "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol"
                "=ag2408")
            daily_history = requests.get(url).json()
            if len(daily_history):
                daily_history_temp = daily_history
        except Exception as e:
            print(e)
            daily_history = daily_history_temp
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(execution, startup_id, item.model_name, history[-61:], daily_history[-10:]) for
                       item in llm_list if item.model_name != 'llama3']
            for future in futures:
                try:
                    result = future.result(timeout=10000000)  # Wait for all processes to complete
                    results.append(result)  # Append the result to the list
                except TimeoutError:
                    print(f"Timeout occurred for a task.")
        time.sleep(5 * 60)
        # llama3 比较特殊，不知道为什么使用线程池失败
        # results.append(execution("llama3", history))
