import datetime

import requests
import os
from dotenv import load_dotenv

load_dotenv()
DING_TOKEN = os.getenv("DING_TOKEN") or ""


def send_message_to_ding(action, name, current_price):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + DING_TOKEN
    # 发送HTTP POST请求
    try:
        content = f"时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n操作：{action.action}\n价格：{current_price}\n数量：{action.volume}\n止损：{action.stop_loss}\n止盈：{action.take_profit}\n原因：{'、'.join(action.reasons)}"
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "来自"+name+"的通知:\n" + content}
        })
    except Exception as e:
        print(e)
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "来自" + name + "的通知:\n" + "解析action出错"}
        })
