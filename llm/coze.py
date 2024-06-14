from llm.base import LlmClient
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
api_key = os.environ["COZE"]

class CozeModal(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.is_chinese = False

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        header = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"
        }
        data = {
            "conversation_id": "fakeid",
            "bot_id": "7312634722897723400",
            "user": "fakeuserid",
            "query": prompt_text,
            "stream": False
        }
        url = "https://api.coze.com/open_api/v2/chat"
        response = requests.post(url, json=data, headers=header)
        messages = json.loads(response.text)["messages"]
        return messages[0]["content"]
