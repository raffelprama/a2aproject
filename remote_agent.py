from fastapi import FastAPI, HTTPException, Request
from typing import List, Dict
import httpx
import os
from pydantic import BaseModel

# LangGraph and LangChain imports
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable

app = FastAPI()

# Dummy in-memory employee data
EMPLOYEES = [
    {"id": 1, "name": "Alice Smith", "country": "USA", "job_role": "Software Engineer"},
    {"id": 2, "name": "Bob Johnson", "country": "Canada", "job_role": "Data Scientist"},
    {"id": 3, "name": "Charlie Brown", "country": "UK", "job_role": "Product Manager"},
    {"id": 4, "name": "Diana Miller", "country": "Australia", "job_role": "UX Designer"},
    {"id": 5, "name": "Ethan Davis", "country": "Germany", "job_role": "DevOps Engineer"},
    {"id": 6, "name": "Fiona White", "country": "France", "job_role": "Marketing Specialist"},
    {"id": 7, "name": "George Green", "country": "Japan", "job_role": "HR Manager"},
    {"id": 8, "name": "Hannah Black", "country": "Brazil", "job_role": "Financial Analyst"},
    {"id": 9, "name": "Ivy King", "country": "India", "job_role": "Technical Writer"},
    {"id": 10, "name": "Jack Lee", "country": "South Korea", "job_role": "Sales Representative"},
    {"id": 11, "name": "Karen Hall", "country": "Mexico", "job_role": "Customer Support"},
    {"id": 12, "name": "Liam Scott", "country": "Spain", "job_role": "Business Analyst"},
    {"id": 13, "name": "Mia Adams", "country": "Italy", "job_role": "Legal Counsel"},
    {"id": 14, "name": "Noah Baker", "country": "Netherlands", "job_role": "Research Scientist"},
    {"id": 15, "name": "Olivia Wright", "country": "Sweden", "job_role": "Project Coordinator"},
    {"id": 16, "name": "Peter Clark", "country": "Ireland", "job_role": "Network Engineer"},
    {"id": 17, "name": "Quinn Lewis", "country": "New Zealand", "job_role": "Content Creator"},
    {"id": 18, "name": "Rachel Young", "country": "Singapore", "job_role": "Operations Manager"},
    {"id": 19, "name": "Sam Harris", "country": "Argentina", "job_role": "Data Engineer"},
    {"id": 20, "name": "Tina Walker", "country": "Switzerland", "job_role": "Accountant"},
    {"id": 21, "name": "Uma Garcia", "country": "Portugal", "job_role": "QA Engineer"},
    {"id": 22, "name": "Victor Rodriguez", "country": "Chile", "job_role": "Cloud Architect"},
    {"id": 23, "name": "Wendy Martinez", "country": "Belgium", "job_role": "Scrum Master"},
    {"id": 24, "name": "Xavier Perez", "country": "Norway", "job_role": "Cybersecurity Analyst"},
    {"id": 25, "name": "Yara Sanchez", "country": "Denmark", "job_role": "Product Designer"},
    {"id": 26, "name": "Zack Kim", "country": "Finland", "job_role": "Machine Learning Engineer"},
    {"id": 27, "name": "Anna Chen", "country": "China", "job_role": "Software Engineer"},
    {"id": 28, "name": "Ben Taylor", "country": "Russia", "job_role": "Data Scientist"},
    {"id": 29, "name": "Chloe Moore", "country": "Egypt", "job_role": "Marketing Specialist"},
    {"id": 30, "name": "David Wilson", "country": "South Africa", "job_role": "Financial Analyst"},
    {"id": 31, "name": "Sarah CEO", "country": "USA", "job_role": "CEO"},
    {"id": 32, "name": "Mike CTO", "country": "Canada", "job_role": "CTO"},
    {"id": 33, "name": "Lisa CFO", "country": "UK", "job_role": "CFO"},
    {"id": 34, "name": "Tom COO", "country": "Germany", "job_role": "COO"},
    {"id": 35, "name": "Emma CMO", "country": "France", "job_role": "CMO"},
    {"id": 36, "name": "Alex VP Engineering", "country": "Japan", "job_role": "VP Engineering"},
    {"id": 37, "name": "Jordan VP Sales", "country": "Brazil", "job_role": "VP Sales"},
    {"id": 38, "name": "Casey VP Marketing", "country": "India", "job_role": "VP Marketing"},
    {"id": 39, "name": "Riley Director IT", "country": "South Korea", "job_role": "Director IT"},
    {"id": 40, "name": "Taylor Director HR", "country": "Spain", "job_role": "Director HR"}
]

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_URL')
model = os.getenv('MODEL')

# Update EmployeeSearchState to include results
class EmployeeSearchState(BaseModel):
    query: str
    results: List[Dict] = []

@app.get("/")
def root():
    return {"message": "Remote AI Agent is running."}

def validate_api_key(request: Request):
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key != "dummy-dekallm-key":
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")

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
        "User: employees in Japan\nOutput: {\"country\": \"Japan\"}\n"
        "User: all employees\nOutput: {\"all\": true}\n"
        "User: show all employees\nOutput: {\"all\": true}"
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
        print(f"\n\ndata = {data}")
        # Try to extract the JSON from the LLM's response
        try:
            content = data["choices"][0]["message"]["content"]
            import re
            content = re.sub(r"^```json\\s*|```$", "", content.strip(), flags=re.MULTILINE)
            import json as pyjson
            criteria = pyjson.loads(content)
            return criteria
        except Exception as e:
            print("\nLLM parse error:", e)
            return {}

@tool
async def employee_search_tool(query: str) -> List[Dict]:
    """Search employees by criteria extracted from the query using LLM."""
    criteria = await call_llm(query)
    print(f"\nLLM criteria:{criteria}")
    if not criteria:
        return []
    
    # Handle "all employees" query
    if "all" in criteria and criteria["all"]:
        print("\nReturning all employees")
        print(EMPLOYEES)
        return EMPLOYEES
    
    results = EMPLOYEES
    if "id" in criteria:
        try:
            id_val = int(criteria["id"])
            results = [e for e in results if e["id"] == id_val]
        except Exception:
            pass
    if "name" in criteria:
        name_val = criteria["name"].lower()
        results = [e for e in results if name_val in e["name"].lower()]
    if "country" in criteria:
        country_val = criteria["country"].lower()
        results = [e for e in results if country_val in e["country"].lower()]
    if "job_role" in criteria:
        job_val = criteria["job_role"].lower()
        results = [e for e in results if job_val in e["job_role"].lower()]
    print("\nFiltered results:", results)
    return results

# Wrapper node to extract query from state and call the tool
async def employee_search_node(state: EmployeeSearchState) -> dict:
    results = await employee_search_tool.ainvoke(state.query)
    return {"query": state.query, "results": results}

# LangGraph state and workflow
def build_graph():
    graph = StateGraph(EmployeeSearchState)
    graph.add_node("employee_search", employee_search_node)
    graph.set_entry_point("employee_search")
    graph.set_finish_point("employee_search")
    return graph.compile()

langraph_workflow = build_graph()

@app.post("/tasks/send")
async def a2a_task(request: Request):
    validate_api_key(request)
    body = await request.json()
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query.")
    # Run the LangGraph workflow
    state = await langraph_workflow.ainvoke({"query": query})
    return {"results": state["results"]} 