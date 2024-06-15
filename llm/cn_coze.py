from llm.base import LlmClient
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
api_key = os.environ["COZE_CN"]

class CnCozeModal(LlmClient):
    def __init__(self, name):
        super().__init__(name)

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        header = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.cn",
            "Connection": "keep-alive"
        }
        data = {
            "conversation_id": "fakeid",
            "bot_id": "7372512631317757952",
            "user": "fakeuserid",
            "query": prompt_text,
            "stream": False
        }
        url = "https://api.coze.cn/open_api/v2/chat"
        response = requests.post(url, json=data, headers=header)
        try:
            messages = json.loads(response.text)["messages"]
            return messages[0]["content"]
        except Exception as e:
            print("cn coze error", e)
            print(response)
