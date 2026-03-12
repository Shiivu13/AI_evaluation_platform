import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    # 1. Try environment variable (local .env or explicit export)
    key = os.getenv("GEMINI_API_KEY")
    if key and key != "dummy":
        return key
    
    # 2. Try Streamlit Secrets (for cloud deployment)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    return "dummy"

# Re-initialize client dynamically inside functions to ensure it picks up keys
# defined at runtime (helpful for streamlit cloud latency)


def generate_response(prompt: str, model: str = "gemini-2.5-flash", temperature: float = 0.7) -> str:
    """
    Generate a response from the LLM based on the prompt.
    """
    api_key = get_api_key()
    if api_key == "dummy":
        return f"[MOCK GEN] For input: {prompt}"
        
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        if "quota" in str(e).lower() or "429" in str(e):
             return f"[MOCK GEN - QUOTA EXCEEDED] For input: {prompt}"
        return f"Error: {str(e)}"

def evaluate_with_llm(system_prompt: str, user_prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Specialized call for LLM-as-a-judge containing system instructions.
    Usually requires json_object response format if the prompt asks for JSON.
    """
    api_key = get_api_key()
    if api_key == "dummy":
        return '{"score": 0.8, "rationale": "Mocked rationale."}'
        
    try:
         client = genai.Client(api_key=api_key)
         # Gemini structured output via response_mime_type
         response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                response_mime_type="application/json",
            )
        )
         return response.text
    except Exception as e:
        print(f"Error in LLM evaluation: {e}")
        if "quota" in str(e).lower() or "429" in str(e):
            return '{"score": 0.5, "rationale": "Mocked rationale (quota exceeded)."}'
        return '{"score": 0.0, "rationale": "Error during LLM call"}'
