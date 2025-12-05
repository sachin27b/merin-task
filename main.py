from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import re
import base64
from pydantic import BaseModel, Field, field_validator


from ai_client import generate_text_from_model, generate_image_from_prompt, verify_image_matches_query

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Image Generator")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ImageGenerationResponse(BaseModel):
    image_base64: str
    mime: str
    prompt_text: str
    tokens: dict
    verification: dict

class ImageGenerationRequest(BaseModel):
    query: str = Field(..., description="Image description query")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        
        if not v:
            raise ValueError("Query cannot be empty")
        
        return v

@app.get("/", response_class=FileResponse)
async def index():
    index_path = STATIC_DIR / "index.html"
    return FileResponse(index_path)


@app.post("/userquery", response_model=ImageGenerationResponse)
async def api_generate(request: ImageGenerationRequest):

    user_query = request.query

    prompt_template = f"""
        You are an assistant that transforms a user query into a detailed, image-generation prompt.

        Your goal:
        - Expand the user’s idea into a visual description
        - Clarify the required image and use a white background unless requested.
        - Keep it concise but richly descriptive

        OUTPUT FORMAT:
        Return ONLY:

        {{
        "image_prompt": "<prompt>"
        }}

        USER QUERY:
        \"{user_query}\"
        """
    text_resp = generate_text_from_model(prompt_template, model="gemini-2.5-flash", seed=42)
    image_prompt = None
    raw_text = text_resp.get("text", "")
    
    parsed = json.loads(re.sub(r"^```.*?\n|```$", "", raw_text, flags=re.DOTALL).strip())
   
    image_prompt = parsed["image_prompt"]

    image_resp = generate_image_from_prompt(image_prompt, model="gemini-3-pro-image-preview")
    image_base64 = image_resp.get("image_bytes")

    verification = verify_image_matches_query(user_query, image_base64, model="gemini-2.5-flash")

    tokens = {
        "text_tokens": text_resp.get("tokens"),
        "image_tokens": image_resp.get("tokens"),
    }

    return JSONResponse(
        {
            "image_base64": base64.b64encode(image_base64).decode("utf-8"),
            "mime": "image/jpeg",
            "prompt_text": image_prompt,
            "tokens": tokens,
            "verification": verification,
        }
    )

