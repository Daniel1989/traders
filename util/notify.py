import datetime

import requests
import os
from dotenv import load_dotenv

load_dotenv()
DING_TOKEN = os.getenv("DING_TOKEN") or ""

send_history = {}


def send_common_to_ding(content, target=None):
    if target is not None:
        code = target["code"]
        msg_type = target["type"]

        if code in send_history:
            if send_history[code] == msg_type:
                return
        send_history[code] = msg_type
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + DING_TOKEN
    try:
        content_with_time = f"时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n内容: {content}"
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "消息通知:\n" + content_with_time}
        })
    except Exception as e:
        print(e)
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "出错通知:\n" + str(e)}
        })


def send_action_msg_to_ding(action, name, current_price):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + DING_TOKEN
    # 发送HTTP POST请求
    try:
        content = f"时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n操作：{action.action}\n价格：{current_price}\n数量：{action.volume}\n止损：{action.stop_loss}\n止盈：{action.take_profit}\n原因：{'、'.join(action.reasons)}"
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "来自" + name + "的通知:\n" + content}
        })
    except Exception as e:
        print(e)
        requests.post(url, json={
            "msgtype": "text",
            "text": {"content": "来自" + name + "的通知:\n" + "解析action出错"}
        })
