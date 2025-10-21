
from openai import OpenAI

# REPLACE WITH YOUR CEREBRAS KEY
api_key = "csk_h3cxfxjnyrjfkhx3e9h9chj9pkch23345n9444xn9dv5dpkf"

client = OpenAI(
    api_key=api_key,
    base_url="https://api.cerebras.ai/v1"
)

print("Testing Cerebras AI...")
response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[{"role": "user", "content": "capital of France?"}]
)

print(f"✅ Response: {response.choices[0].message.content}")
print("🎉 CEREBRAS TEST PASSED!")