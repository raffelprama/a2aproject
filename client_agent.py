import requests
import sys
import httpx
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_URL')
model = os.getenv('MODEL')

REMOTE_AGENT_URL = "http://localhost:8000/tasks/send"
API_KEY = "dummy-dekallm-key"

async def call_llm(query: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an assistant that extracts employee search criteria (id, name, country, job_role) from user queries. Return a JSON object with any found fields."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.0
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
            criteria = json.loads(content)
            return criteria
        except Exception:
            return {}

def main():
    import asyncio
    print("A2A Client AI Agent CLI. Type your query (or 'exit' to quit):")
    use_llm = input("Use LLM to parse your query before sending? (y/n): ").strip().lower() == 'y'
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            break
        try:
            if use_llm:
                criteria = asyncio.run(call_llm(user_input))
                payload = {"query": json.dumps(criteria) if criteria else user_input}
            else:
                payload = {"query": user_input}
            response = requests.post(
                REMOTE_AGENT_URL,
                headers={"x-api-key": API_KEY},
                json=payload
            )
            print("Response:", response.json())
        except Exception as e:
            print("Error communicating with Remote Agent:", e)

if __name__ == "__main__":
    main() 