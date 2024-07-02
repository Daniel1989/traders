import random

from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
from llm.base import LlmClient
import os

from service.ip import get_useable_ip

load_dotenv()


class DoubaoModel(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.client = client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3")

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        ip_list = get_useable_ip()
        ip = random.choice(ip_list).ip

        os.environ["http_proxy"] = ip
        os.environ["https_proxy"] = ip
        response = self.client.chat.completions.create(
            model="ep-20240615044418-lmzkv",
            messages=[
                {"role": "system", "content": system_prompt or 'You are a help assistant.'},
                {"role": "user", "content": prompt_text},
            ],
        )
        return response.choices[0].message.content
