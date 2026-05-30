import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def call_llm(model, messages, system="", max_tokens=4096, retries=3, retry_delay=2.0):
    all_messages = []
    if system:
        all_messages.append({"role": "system", "content": system})
    all_messages.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=all_messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
