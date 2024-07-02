import requests
import os
from dotenv import load_dotenv

load_dotenv()
DING_TOKEN = os.getenv("DING_TOKEN") or ""


def send_message_to_ding(content):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + DING_TOKEN
    # 发送HTTP POST请求
    requests.post(url, json={
        "msgtype": "text",
        "text": {"content": "通知:\n" + content}
    })
