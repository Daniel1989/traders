import time
from models import Startup
from service.account import daily_count
from agent import Agent
import datetime
import uuid
from concurrent.futures import ProcessPoolExecutor, TimeoutError

from service.fpp3 import calc_interval
from service.futures_data import get_goods_minute_data, sync_daily_data, get_main_code_no, save_forecast_item, \
    is_daily_data_synced
from util.cache import request
from util.notify import send_common_to_ding
from util.utils import is_trade_time, is_sync_time, is_sync_daily_time

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

# gpt = OpenaiModel("gpt-3.5-turbo")  # 免费，可用，评分为基准60分
# llama = Ollama("llama3")  # 免费，可用, 评分为75分
# google = GoogleModel("gemini-1.5-pro-latest") # 不免费，目前不可用了
# baidu = BaiduModal("ernie-speed-128k") # 免费，可用，评分为40分
ali = AliModel("qwen-long")  # 不免费，但是阿里云付费，可用，评分为75分
# kimi = KimiModal("moonshot-v1-128k") # 不免费，可用，有赠送的代金劵可用，有RPM为3的限制，需要每个请求sleep30秒，评分为35分
# deepseek = DeepseekModal("deepseek-chat")  # 不免费，可用，有送的，评分为60分
# coze = CozeModal("coze")  # use gpt4 # 不免费，不可用，赠送的token已用光，评分为70分
cncoze = CnCozeModal("cncoze")  # # 免费，可用，评分为70分，个人感觉用的就是gpt4吧？
# hunyuan = HunyuanModal("hunyuan-lite") # 免费，但是弱智，返回的值乱写 评分为0分. hunyuan-pro有送，但是也弱智
# xunfei = XunfeiModel("xunfei") # lite免费，3.5有送的，但是，全部都是弱智，vol乱写，评分为0分
doubao = DoubaoModel("doubao")  # 不免费，有赠送，但是收费很便宜，可以很低，评分65
llm_list = [ali, cncoze, doubao]


# 目前看，gpt3.5，扣子中文，llama3，阿里云，扣子，DeepseekModal，DoubaoModel
# 其中阿里云，扣子，DeepseekModal，DoubaoModel收费，要小心，但是阿里云和doubao没有找到明显的收费的地方


def item_exists(data_list, field, value):
    return any(item[field] == value for item in data_list)


def execution(startup_uid, agent_name, analyze_data):
    llm = [item for item in llm_list if item.model_name == agent_name][0]
    agent_list = Startup.select().where(Startup.uid == startup_uid, Startup.model_name == llm.model_name)
    print(agent_name, len(agent_list))
    if len(agent_list) > 0:
        agent_name = agent_list[0].agent_name
        agent = Agent(llm, agent_name)
    else:
        agent = Agent(llm)
        startup_agent = Startup(uid=startup_uid, model_name=llm.model_name, agent_name=agent.name)
        startup_agent.save()
    return agent.handler(analyze_data)


def forecast_check(minute_history_data, history_daily_data):
    today = minute_history_data[len(minute_history_data) - 1]
    current_price = today[4]

    minute_result, _ = calc_interval(minute_history_data[:-1], is_minute=True)
    daily_result, _ = calc_interval(history_daily_data, is_minute=False)
    p95_min = min(minute_result.iloc[:, 2].to_list())
    p95_max = max(minute_result.iloc[:, 5].to_list())
    p80_min = min(minute_result.iloc[:, 3].to_list())
    p80_max = max(minute_result.iloc[:, 4].to_list())
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

    s1 = ("基于近一年的每日收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对今日收盘价格进行预测，"
          "得到80%的置性区间为：[" + str(daily_result.iloc[0][3]) + ", " + str(daily_result.iloc[0][4]) + "]。"
                                                                                                         "95%的置性区间为：[" + str(
        daily_result.iloc[0][2]) + ", " + str(daily_result.iloc[0][5]) + "]。")

    s2 = ("基于最近6个小时内的每分钟收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对接下去的一小时内的每分钟收盘价格进行预测，"
          "得到结果如下，有80%的可能价格在[" + str(p80_min) + ", " + str(p80_max) + "]的区间内变动,"
                                                                                   "95%的的可能价格在[" + str(
        p95_min) + ", " + str(p95_max) + "]的区间内变动。")
    return s1 + "同时，" + s2 + "\n"


if __name__ == '__main__':
    # reset()
    # startup_id = str(uuid.uuid4())
    startup_id = "4a283c5d-3f43-42ca-a369-69a918e74ce9"
    results = []
    while True:
        today = datetime.date.today()
        if today.weekday() == 5 or today.weekday() == 6:
            time.sleep(5 * 60)
            continue
        if not is_trade_time():
            if is_sync_time():
                daily_count()
            if is_sync_daily_time():
                today_str = datetime.datetime.now().strftime('%Y-%m-%d')
                if not is_daily_data_synced(today_str):
                    sync_daily_data(today_str.replace('-', ""))
                    main_code_list = get_main_code_no()
                    for item in main_code_list:
                        save_forecast_item(item)

            time.sleep(5 * 60)
            continue

        try:
            url = (
                "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol"
                "=ag2408")
            daily_history = request(url)
        except Exception as e:
            print(e)
            continue

        minute_history = get_goods_minute_data('AG2408')
        forecast_result = forecast_check(minute_history, daily_history)
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(execution, startup_id, item.model_name, {
                "daily_history": daily_history,
                "minute_history": minute_history,
                "forecast_result": forecast_result
            }) for item in llm_list if item.model_name != 'llama3']
            for future in futures:
                try:
                    result = future.result(timeout=10000000)  # Wait for all processes to complete
                    results.append(result)  # Append the result to the list
                except TimeoutError:
                    print(f"Timeout occurred for a task.")
        time.sleep(5 * 60)
        # llama3 比较特殊，不知道为什么使用线程池失败
        # results.append(execution("llama3", history))
