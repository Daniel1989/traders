from models.base import LlmClient
from dotenv import load_dotenv
import os
from dashscope import Generation

load_dotenv()


class AliModel(LlmClient):
    def __init__(self, name):
        super().__init__(name)

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        messages = [
            {'role': 'user', 'content': prompt_text}]
        responses = Generation.call(self.model_name,
                                    messages=messages,
                                    result_format='message',  # 设置输出为'message'格式
                                    stream=False,  # 设置输出方式为流式输出
                                    incremental_output=False  # 增量式流式输出
                                    )
        return responses.output.choices[0]['message']['content']
