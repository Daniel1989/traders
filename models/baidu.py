from models.base import LlmClient
import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()

API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")


class BaiduModal(LlmClient):
    def __init__(self, name):
        super().__init__(name)

    def get_access_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/"+self.model_name+"?access_token=" + self.get_access_token()

        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return json.loads(response.text)["result"]
