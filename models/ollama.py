from models.base import LlmClient
import requests
import json


class Ollama(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.is_chinese = False

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        data = {
            "model": self.model_name,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            "options": {
                "temperature": 0
            }
        }
        url = "http://localhost:11434/api/chat"
        response = requests.post(url, json=data)
        return json.loads(response.text)["message"]["content"]
