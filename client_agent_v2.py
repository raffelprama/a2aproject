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

# Agent endpoints
EMPLOYEE_AGENT_URL = "http://localhost:8000/tasks/send"
HR_AGENT_URL = "http://localhost:8001/hr-tasks/send"
API_KEY = "dummy-dekallm-key"

async def call_llm(query: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = (
        "You are an assistant that extracts employee search criteria (id, name, country, job_role) from user queries. "
        "Return a JSON object with any found fields.\n"
        "Examples:\n"
        "User: who is the hr manager\nOutput: {\"job_role\": \"HR Manager\"}\n"
        "User: find employee with ID 2\nOutput: {\"id\": 2}\n"
        "User: show me employees in marketing\nOutput: {\"job_role\": \"Marketing Specialist\"}\n"
        "User: who is Alice Smith\nOutput: {\"name\": \"Alice Smith\"}\n"
        "User: employees in Japan\nOutput: {\"country\": \"Japan\"}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.2
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
            import re
            content = re.sub(r"^```json\\s*|```$", "", content.strip(), flags=re.MULTILINE)
            criteria = json.loads(content)
            return criteria
        except Exception as e:
            print("LLM parse error:", e)
            return {}

def determine_agent_and_query_type(user_query: str) -> tuple[str, str]:
    """
    Analyze the user query to determine which agent to route to and what type of query it is.
    Returns: (agent_type, query_type)
    agent_type: "employee" or "hr"
    query_type: "salary", "hierarchy", "schedule", or "general"
    """
    query_lower = user_query.lower()
    
    # HR-related keywords
    hr_keywords = {
        "salary": ["salary", "pay", "compensation", "wage", "earnings"],
        "hierarchy": ["hierarchy", "reports to", "reporting", "level", "boss", "manager", "supervisor"],
        "schedule": ["schedule", "hours", "shift", "work time", "working hours", "shift type"]
    }
    
    # Check for HR-specific queries
    for query_type, keywords in hr_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return "hr", query_type
    
    # Default to employee info for general queries
    return "employee", "general"

def route_query_to_agent(user_query: str, use_llm: bool = False) -> dict:
    """
    Route the query to the appropriate agent and return the response.
    """
    agent_type, query_type = determine_agent_and_query_type(user_query)
    
    # Determine endpoint
    if agent_type == "hr":
        endpoint = HR_AGENT_URL
        print(f"Routing to HR Agent for {query_type} query")
    else:
        endpoint = EMPLOYEE_AGENT_URL
        print(f"Routing to Employee Info Agent for general query")
    
    # Prepare payload
    if use_llm:
        import asyncio
        criteria = asyncio.run(call_llm(user_query))
        payload = {"query": json.dumps(criteria) if criteria else user_query}
    else:
        payload = {"query": user_query}
    
    # Add query type for HR agent
    if agent_type == "hr":
        payload["query_type"] = query_type
    
    try:
        response = requests.post(
            endpoint,
            headers={"x-api-key": API_KEY},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with {agent_type.title()} Agent: {str(e)}"}

def main():
    print("A2A Client AI Agent CLI (V2 - Multi-Agent Router)")
    print("Type your query (or 'exit' to quit):")
    use_llm = input("Use LLM to parse your query before sending? (y/n): ").strip().lower() == 'y'
    
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            break
        
        if not user_input:
            continue
            
        try:
            result = route_query_to_agent(user_input, use_llm)
            print("Response:", result)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main() 