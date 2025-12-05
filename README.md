# Image Generator API

The application consists of three main components:

1. **AI Client** (`ai_client.py`): Handles all interactions with Google's Gemini API
2. **API Server** (`main.py`): FastAPI application that orchestrates the image generation workflow
3. **Static Frontend**: Web interface for user interaction

## Prerequisites

- Python 3.10.11
- Google Gemini API key

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
uvicorn main:app 
```

### API Endpoints

#### `GET /`
Serves the static web interface.

#### `POST /userquery`
Generates an image from a text query.

**Request Body:**
```json
{
  "query": "some query"
}
```

**Response:**
```json
{
  "image_base64": "<base64-encoded-image>",
  "mime": "image/jpeg",
  "prompt_text": "visual description...",
  "tokens": {
    "text_tokens": 150,
    "image_tokens": 2000
  },
  "verification": {
    "match": true
  }
}
```
