from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

load_dotenv()

client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3")
response = client.chat.completions.create(
    model="ep-20240615044418-lmzkv",
    messages=[
        {"role": "system", "content": 'You are a help assistant.'},
        {"role": "user", "content": 'who you are'},
    ],
)
print(response)