from fastapi import FastAPI, HTTPException, Request
from typing import List, Dict
import httpx
import os
from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph.graph import StateGraph
from hr_dummy_data import HR_SALARIES_DATA, HR_JOB_HIERARCHY_DATA, HR_SCHEDULES_DATA
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_URL')
model = os.getenv('MODEL')

class HRQueryState(BaseModel):
    query: str
    query_type: str = "general"
    results: List[Dict] = []

@app.get("/")
def root():
    return {"message": "HR AI Agent is running."}

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
        "You are an assistant that extracts employee search criteria from user queries. "
        "Available employee names: Alice Smith, Bob Johnson, Charlie Brown, Diana Miller, Ethan Davis, "
        "Fiona White, George Green, Hannah Black, Ivy King, Jack Lee, Karen Hall, Liam Scott, "
        "Mia Adams, Noah Baker, Olivia Wright, Peter Clark, Quinn Lewis, Rachel Young, Sam Harris, "
        "Tina Walker, Uma Garcia, Victor Rodriguez, Wendy Martinez, Xavier Perez, Yara Sanchez, "
        "Zack Kim, Anna Chen, Ben Taylor, Chloe Moore, David Wilson, Sarah CEO, Mike CTO, Lisa CFO, "
        "Tom COO, Emma CMO, Alex VP Engineering, Jordan VP Sales, Casey VP Marketing, Riley Director IT, "
        "Taylor Director HR.\n"
        "Return a JSON object with any found fields.\n"
        "Examples:\n"
        "User: what is Alice Smith's salary\nOutput: {\"name\": \"Alice Smith\"}\n"
        "User: salary for Karen\nOutput: {\"name\": \"Karen Hall\"}\n"
        "User: salary for ID 1\nOutput: {\"id\": 1}\n"
        "User: who reports to Product Manager\nOutput: {\"job_role\": \"Product Manager\"}\n"
        "User: schedule for Bob Johnson\nOutput: {\"name\": \"Bob Johnson\"}\n"
        "User: hierarchy for Software Engineer\nOutput: {\"job_role\": \"Software Engineer\"}\n"
        "User: what is Zack's salary\nOutput: {\"name\": \"Zack Kim\"}\n"
        "User: all salaries\nOutput: {\"all\": true}\n"
        "User: show all salaries\nOutput: {\"all\": true}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.1
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        print(f"\n\ndata = {data}")
        try:
            content = data["choices"][0]["message"]["content"]
            import re
            content = re.sub(r"^```json\\s*|```$", "", content.strip(), flags=re.MULTILINE)
            import json as pyjson
            criteria = pyjson.loads(content)
            return criteria
        except Exception as e:
            print("\nLLM parse error:", e)
            print("\nRaw LLM response:", content if 'content' in locals() else "No content")
            return {}

@tool
async def salary_search_tool(query: str) -> List[Dict]:
    """Always return all salary data for any query."""
    print("\nReturning all salaries (no filtering)")
    return HR_SALARIES_DATA

@tool
async def hierarchy_search_tool(query: str) -> List[Dict]:
    """Search job hierarchy information by criteria extracted from the query using LLM."""
    criteria = await call_llm(query)
    print("\nLLM criteria for hierarchy:", criteria)
    if not criteria:
        return []
    
    results = []
    for hierarchy_record in HR_JOB_HIERARCHY_DATA:
        match = True
        if "job_role" in criteria:
            job_val = criteria["job_role"].lower()
            if job_val not in hierarchy_record["job_role"].lower():
                match = False
        
        if match:
            results.append(hierarchy_record)
    
    print("\nHierarchy search results:", results)
    return results

@tool
async def schedule_search_tool(query: str) -> List[Dict]:
    """Search employee work schedule information by criteria extracted from the query using LLM."""
    criteria = await call_llm(query)
    print("\nLLM criteria for schedule:", criteria)
    if not criteria:
        return []
    
    results = []
    for schedule_record in HR_SCHEDULES_DATA:
        match = True
        if "id" in criteria:
            try:
                id_val = int(criteria["id"])
                if schedule_record["employee_id"] != id_val:
                    match = False
            except Exception:
                match = False
        elif "name" in criteria:
            name_to_id_map = {
                "alice smith": 1, "bob johnson": 2, "charlie brown": 3,
                "diana miller": 4, "ethan davis": 5, "fiona white": 6,
                "george green": 7, "hannah black": 8, "ivy king": 9,
                "jack lee": 10, "karen hall": 11, "liam scott": 12,
                "mia adams": 13, "noah baker": 14, "olivia wright": 15,
                "peter clark": 16, "quinn lewis": 17, "rachel young": 18,
                "sam harris": 19, "tina walker": 20, "uma garcia": 21,
                "victor rodriguez": 22, "wendy martinez": 23, "xavier perez": 24,
                "yara sanchez": 25, "zack kim": 26, "anna chen": 27,
                "ben taylor": 28, "chloe moore": 29, "david wilson": 30
            }
            search_name = criteria["name"].lower()
            
            if search_name in name_to_id_map:
                if schedule_record["employee_id"] != name_to_id_map[search_name]:
                    match = False
            else:
                for full_name, emp_id in name_to_id_map.items():
                    if search_name in full_name or full_name.startswith(search_name):
                        if schedule_record["employee_id"] != emp_id:
                            match = False
                        break
                else:
                    match = False
        
        if match:
            results.append(schedule_record)
    
    print("\nSchedule search results:", results)
    return results

async def hr_search_node(state: HRQueryState) -> dict:
    query_type = state.query_type.lower()
    
    print(f"🔍 HR search node: query='{state.query}', query_type='{query_type}'")
    
    if query_type == "salary":
        results = await salary_search_tool.ainvoke(state.query)
    elif query_type == "hierarchy":
        results = await hierarchy_search_tool.ainvoke(state.query)
    elif query_type == "schedule":
        results = await schedule_search_tool.ainvoke(state.query)
    else:
        results = await salary_search_tool.ainvoke(state.query)
    
    print(f"📊 HR search results: {len(results)} items")
    return {"query": state.query, "query_type": state.query_type, "results": results}

def build_graph():
    graph = StateGraph(HRQueryState)
    graph.add_node("hr_search", hr_search_node)
    graph.set_entry_point("hr_search")
    graph.set_finish_point("hr_search")
    return graph.compile()

langraph_workflow = build_graph()

@app.post("/hr-tasks/send")
async def hr_task(request: Request):
    validate_api_key(request)
    body = await request.json()
    query = body.get("query", "")
    query_type = body.get("query_type", "general")
    
    print(f"\n📥 HR Agent received: query='{query}', query_type='{query_type}'")
    
    if not query:
        raise HTTPException(status_code=400, detail="Missing query.")
    
    state = await langraph_workflow.ainvoke({"query": query, "query_type": query_type})
    print(f"📤 HR Agent returning: {len(state['results'])} results")
    return {"results": state["results"]} 