import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://jot-bot-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    transcript: str
    task: str  # "summary", "sentiment", "action_items"

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    prompt_map = {
        "summary": f"Summarize the following transcript in 3 concise bullet points:\n\n{request.transcript}",
        "sentiment": f"Analyze the sentiment (positive/neutral/negative) of the following transcript:\n\n{request.transcript}",
        "action_items": f"Extract actionable next steps from the following transcript:\n\n{request.transcript}"
    }

    prompt = prompt_map.get(request.task.lower())
    if not prompt:
        return {"error": "Invalid task type"}

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 200
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        result = response.json()

    output = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    return {"output": output}
