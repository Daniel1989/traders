from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from models import Startup
from datetime import datetime
import requests
from service.fpp3 import calc_interval, draw_interval
from service.futures_data import get_goods_minute_data, sync_daily_data, get_main_code_no, save_forecast_item

load_dotenv()

# 统计每日账户资金
# client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3")
# response = client.chat.completions.create(
#     model="ep-20240615044418-lmzkv",
#     messages=[
#         {"role": "system", "content": 'You are a help assistant.'},
#         {"role": "user", "content": 'who you are'},
#     ],
# )
# print(response)
# draw_daily_account()

# forecast预测
# url = ("http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol"
#                 "=ag2412")
# daily_history = requests.get(url).json()
# result, _ = calc_interval(daily_history)
# data = get_goods_minute_data("AG2412")
# result_minute, origin_data = calc_interval(data, is_minute=True)
# p95_min = min(result_minute.iloc[:, 2].to_list())
# p95_max = max(result_minute.iloc[:, 5].to_list())
# p80_min = min(result_minute.iloc[:, 3].to_list())
# p80_max = max(result_minute.iloc[:, 4].to_list())
# s1 = ("基于近一年的每日收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对今日收盘价格进行预测，"
#      "得到80%的置性区间为：["+str(result.iloc[0][3])+", "+str(result.iloc[0][4])+"]。"
#      "95%的置性区间为：["+str(result.iloc[0][2])+", "+str(result.iloc[0][5])+"]。")
#
# s2 = ("基于最近6个小时内的每分钟收盘价格，通过使用Auto-Regressive Integrated Moving Average(ARIMA)模型对接下去的一小时内的每分钟收盘价格进行预测，"
#      "得到结果如下，有80%的可能价格在["+str(p80_min)+", "+str(p80_max)+"]的区间内变动,"
#      "95%的的可能价格在["+str(p95_min)+", "+str(p95_max)+"]的区间内变动。")
# draw_interval(result, origin_data)

# 同步每日数据
# dateStr = datetime.now().strftime('%Y%m%d')
# date_list = [
#     '20240701',
#     '20240702',
#     '20240703',
#     '20240704',
#     '20240705',
#     '20240708',
#     '20240709',
#     '20240710',
#     '20240711',
#     '20240712',
# ]
# for item in date_list:
#     sync_daily_data(item)
#
# data = get_main_code_no()
# for item in data:
#     save_forecast_item(item)
#     break

# def intercept_request(request):
#     # we can update requests with custom headers
#     # request.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
#     # request.headers['Accept-Encoding'] = "gzip, deflate"
#     # request.headers['Accept-Language'] = "zh-CN,zh;q=0.9"
#     # request.headers['Cache-Control'] = "no-cache"
#     # request.headers['Connection'] = "keep-alive"
#     if "stealth.min.js" in request.url:
#         print("ha")
#     if "secret" in request.url :
#         request.headers['x-secret-token'] = "123"
#         print("patched headers of a secret request")
#     # or adjust sent data
#     if request.method == "POST":
#         request.post_data = "patched"
#         print("patched POST request")
#     return request
#
# def intercept_response(response):
#     # print(response.status)
#     # we can extract details from background requests
#     if response.request.resource_type == "xhr":
#         print(response.headers.get('cookie'))
#     return response
#
# with sync_playwright() as p:
#     target = p.chromium
#     for browser_type in [target]:  # p.firefox, p.chromium, p.webkit
#         browser = browser_type.launch(headless=False)
#         page = browser.new_page()
#         # page.add_init_script("() => {"
#         #
#         #                      "}")
#         page.on("request", intercept_request)
#         page.on("response", intercept_response)
#         responses = page.goto("https://bot.sannysoft.com/")
#         # page.add_script_tag(url="https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js")
#
#         page.pause()
#         # page.screenshot(path="screenshot.png")
#         print(responses.status)
#         browser.close()

import json
from llm.cn_coze import CnCozeModal
from llm.volc import DoubaoModel

stories = [
    "现代励志故事，一个失业青年如何克服生活困境，终于实现自我突破，成为行业翘楚的心路历程。",
    "一个现代女性穿越到古代某朝代后发生的传奇故事。",
    "现代背景，一名神探警察遇到了一桩棘手的连环失踪案并将其侦破的故事。",
    "古代背景，皇家侍卫和公主历经层层考验，突破身份桎梏的爱情故事。",
    "现代玄幻背景，在一所驯服神兽的魔法学校中，围绕着三个学生小伙伴发生的奇幻冒险故事。",
    "古代侦探系列，一位才华横溢的年轻学士，在解决一连串神秘案件中揭露皇室阴谋的故事。",
    "二十一世纪初，一个小镇上发生的一系列神秘事件，让一群青少年开始探索超自然现象，并发现了小镇隐藏的古老秘密的故事。",
    "现代都市背景，一个名不见经传的漫画家，通过与自己创作的虚拟角色“交流”，解决一系列诡秘案件的故事。",
    "古代异界背景，一位天赋异禀的少年，在师傅的指导下学习古老的灵术，最终踏上寻找失落的神器，拯救家园的冒险旅程的故事。",
    "繁华都市背景，一个单亲妈妈如何在抚养孩子和维持生计之间找到平衡，同时保持对自己梦想的追求的故事。",
    "现代悬疑系列，一位心理学家利用自己的专业知识，帮助警方侦破一系列复杂的心理游戏案件。",
    "现代心理惊悚背景，一名精神科医生被卷入一连串的脑控实验阴谋，如何在精神与现实的边缘徘徊求生的故事。",
    "虚构古代背景，一位年轻的书生因缘巧合获得一本神秘典籍，开启了他成为一代宗师的修道之旅。",
    "古代神话背景，一位勇者如何经过重重试炼，最终获取神器，拯救世界于水深火热之中的传奇故事。",
    "虚拟现实背景，一群玩家在一款极度真实的VR游戏中探索未知世界并揭露游戏背后隐藏的秘密的故事。",
    "穿越时空背景，一群来自不同时代的人意外聚集在一个神秘的地方，他们如何互相协作，解开时空之谜的故事。",
    "科幻背景，一个机器人意识觉醒后，它如何在追求自我身份的同时，挑战人类社会关于存在和自由的根本问题。",
    "20世纪60年代的欧洲，一个侦探在解决一起跨国艺术品盗窃案中，逐渐揭露出一个关于失落宝藏的大阴谋。",
    "现代都市背景，一位因交通事故失去双腿的舞者，通过先进的义肢技术重新站起来，重新找回舞台与自我的故事。",
    "古代背景，一个普通医女奋斗成为朝廷高官，最终影响整个王朝政治格局变化的故事。"
]
cncoze = CnCozeModal("doubao")
doubao = DoubaoModel("doubao")

with open("submit.json", "w") as file:
    for task in stories:
        for t in range(50):
            start = datetime.now()
            content = doubao.do_prompt(
                "你是一个熟读各类小说的专家，请你根据以下内容写一段800字左右的小说。注意，不要输出小说标题\n" + task)
            data = {"instruction": "你是一个熟读各类小说的专家，请你根据要求写一段800字左右的小说。", "input": task,
                    "output": content}
            end = datetime.now()
            print("任务：",task, "第", t, "次", "耗时：", end - start)
            # 将每个元素写入文件，并添加换行符
            file.write(json.dumps(data, ensure_ascii=False) + "\n")
