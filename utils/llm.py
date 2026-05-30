import os
from groq import Groq
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
client = Groq(api_key=")

def call_llm(model, messages, system="", max_tokens=8192, retries=3, retry_delay=2.0):
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