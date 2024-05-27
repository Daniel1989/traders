from models.base import LlmClient
from dotenv import load_dotenv
import os

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

load_dotenv()

SPARKAI_URL = 'wss://spark-api.xf-yun.com/v1.1/chat'
SPARKAI_DOMAIN = 'general'

SPARKAI_API_SECRET = os.getenv("SPARKAI_API_SECRET")
SPARKAI_API_KEY = os.getenv("SPARKAI_API_KEY")
SPARKAI_APP_ID = os.getenv("SPARKAI_APP_ID")


class XunfeiModel(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        self.client = ChatSparkLLM(
            spark_api_url=SPARKAI_URL,
            spark_app_id=SPARKAI_APP_ID,
            spark_api_key=SPARKAI_API_KEY,
            spark_api_secret=SPARKAI_API_SECRET,
            spark_llm_domain=SPARKAI_DOMAIN,
            streaming=False,
        )

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        messages = [ChatMessage(
            role="user",
            content=prompt_text
        )]
        handler = ChunkPrintHandler()
        response = self.client.generate([messages], callbacks=[handler])
        return response.generations[0][0].text
