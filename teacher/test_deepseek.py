import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    timeout=30.0,
    max_retries=2
)

try:
    response = client.chat.completions.create(
        model="deepseek-coder",
        messages=[{"role": "user", "content": "Say hello in Portuguese"}],
        max_tokens=20
    )
    print("SUCCESS:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))