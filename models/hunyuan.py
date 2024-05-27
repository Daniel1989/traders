from models.base import LlmClient
import requests
from dotenv import load_dotenv
import json
import os
import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

load_dotenv()

HUNYUAN_ID = os.getenv("HUNYUAN_ID")
HUNYUAN_KEY = os.getenv("HUNYUAN_KEY")


class HunyuanModal(LlmClient):
    def __init__(self, name):
        super().__init__(name)
        cred = credential.Credential(HUNYUAN_ID, HUNYUAN_KEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = hunyuan_client.HunyuanClient(cred, "", clientProfile)

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        req = models.ChatCompletionsRequest()
        params = {
            "Model": self.model_name,
            "Messages": [
                {"Role": "system", "Content": system_prompt or 'You are a help assistant.'},
                {
                    "Role": "user",
                    "Content": prompt_text
                }
            ],
            "Stream": False,
        }
        req.from_json_string(json.dumps(params))
        response = self.client.ChatCompletions(req)
        return response.Choices[0].Message.Content
