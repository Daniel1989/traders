from llm.base import LlmClient
from dotenv import load_dotenv
import os
from openai import OpenAI
import time
from datetime import datetime

load_dotenv()
openai_api_key = os.getenv("KIMI")


class KimiModal(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.client = OpenAI(api_key=openai_api_key, base_url="https://api.moonshot.cn/v1")

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        print("开始准备请求:", datetime.now())
        time.sleep(30)
        print("真正开始请求:", datetime.now())
        result = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt or 'You are a help assistant.'},
                {"role": "user", "content": prompt_text},
            ]
        )
        return result.choices[0].message.content
