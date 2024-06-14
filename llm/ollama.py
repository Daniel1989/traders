from llm.base import LlmClient
import requests
import json
import ollama


class Ollama(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.is_chinese = False

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        response = ollama.chat(model='llama3', messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ])
        return response["message"]["content"]
