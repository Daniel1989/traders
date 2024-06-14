from llm.base import LlmClient
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
os.environ["http_proxy"] = "http://127.0.0.1:1087"
os.environ["https_proxy"] = "http://127.0.0.1:1087"
# for m in genai.list_models():
#     print(m.name)
'''
llm/chat-bison-001
llm/text-bison-001
llm/embedding-gecko-001
llm/gemini-1.0-pro
llm/gemini-1.0-pro-001
llm/gemini-1.0-pro-latest
llm/gemini-1.0-pro-vision-latest
llm/gemini-1.5-flash-latest
llm/gemini-1.5-pro-latest
llm/gemini-pro
llm/gemini-pro-vision
llm/embedding-001
llm/text-embedding-004
llm/aqa
'''


class GoogleModel(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.client = genai.GenerativeModel(self.model_name)
        self.is_chinese = False

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        messages = [{'role': 'user',
                     'parts': [prompt_text]}]

        response = self.client.generate_content(messages)
        return response.text
