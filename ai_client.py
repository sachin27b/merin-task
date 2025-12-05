import os
import base64
from typing import Tuple, Dict, Any
from google import genai
from google.genai import types
import json
import re

from dotenv import load_dotenv
load_dotenv() 

API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

def generate_text_from_model(prompt: str, model: str = "gemini-2.5-flash", seed: int = 42):

    response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        seed=seed,
        temperature=0.1
        ),
    )
    text = response.text
    tokens = response.usage_metadata.total_token_count
    return {"text": text, "tokens": tokens}


def generate_image_from_prompt(prompt: str, model: str = "gemini-3-pro-image-preview"):

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            seed=42,
            temperature=0.1
        )
    )
    image_bytes = response.parts[0].inline_data.data
    tokens = response.usage_metadata.total_token_count
    
    return {"image_bytes": image_bytes, "tokens": tokens}


def verify_image_matches_query(user_query: str, image_base64: str, mime: str = "image/png", model: str = "gemini-2.5-flash"):

    prompt = f"""
        You are an image-judging assistant.

        Task:
        - Compare the USER_QUERY with the IMAGE you are given.
        - Decide if the image matches what the user asked for.
        - if the core idea is present, mark as match = true.

        USER_QUERY:
        \"{user_query}\"

        Output:
        Return ONLY

        {{
        "match": true or false,
        }}
        """
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
      types.Part.from_bytes(
        data=image_base64,
        mime_type='image/jpeg',
      ),
      prompt
    ],
    config=types.GenerateContentConfig(
            seed=42,
        )
  )

    
    data = json.loads(re.sub(r"^```.*?\n|```$", "", response.text, flags=re.DOTALL).strip())
    match = bool(data.get("match", True))

    return {"match": match}
