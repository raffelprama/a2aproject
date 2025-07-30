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
    agent_type: "employee", "hr", or "multi_agent"
    query_type: "salary", "hierarchy", "schedule", or "general"
    """
    query_lower = user_query.lower()
    
    # HR-related keywords that require multi-agent communication
    hr_keywords = {
        "salary": ["salary", "pay", "compensation", "wage", "earnings"],
        "hierarchy": ["hierarchy", "reports to", "reporting", "level", "boss", "manager", "supervisor"],
        "schedule": ["schedule", "hours", "shift", "work time", "working hours", "shift type"]
    }
    
    # Check for HR-specific queries that need employee info first
    for query_type, keywords in hr_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            # Check if query mentions a specific person (name or ID)
            if any(word in query_lower for word in ["what is", "salary of", "schedule of", "for", "id", "employee"]):
                return "multi_agent", query_type
    
    # Default to employee info for general queries
    return "employee", "general"

def get_employee_info(employee_query: str) -> dict:
    """
    Get employee information from Employee Info Agent.
    """
    try:
        response = requests.post(
            EMPLOYEE_AGENT_URL,
            headers={"x-api-key": API_KEY},
            json={"query": employee_query},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with Employee Info Agent: {str(e)}"}

def get_hr_info(employee_id: int, query_type: str) -> dict:
    """
    Get HR information from HR Agent using employee ID.
    """
    try:
        response = requests.post(
            HR_AGENT_URL,
            headers={"x-api-key": API_KEY},
            json={"query": f"ID {employee_id}", "query_type": query_type},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with HR Agent: {str(e)}"}

def route_query_to_agent(user_query: str, use_llm: bool = False) -> dict:
    """
    Route the query to the appropriate agent(s) and return the response.
    """
    agent_type, query_type = determine_agent_and_query_type(user_query)
    
    print(f"Routing strategy: {agent_type} for {query_type} query")
    
    if agent_type == "multi_agent":
        # Multi-agent communication: Employee Info → HR Agent
        print("Step 1: Getting employee information...")
        employee_result = get_employee_info(user_query)
        
        if "error" in employee_result:
            return employee_result
        
        if not employee_result.get("results"):
            return {"error": "Employee not found"}
        
        # Extract employee ID from the first result
        employee = employee_result["results"][0]
        employee_id = employee.get("id")
        
        if not employee_id:
            return {"error": "Could not determine employee ID"}
        
        print(f"Found employee: {employee['name']} (ID: {employee_id})")
        print(f"Step 2: Getting {query_type} information from HR Agent...")
        
        # Get HR information using the employee ID
        hr_result = get_hr_info(employee_id, query_type)
        
        if "error" in hr_result:
            return hr_result
        
        # Combine the results
        combined_result = {
            "employee_info": employee,
            "hr_info": hr_result.get("results", []),
            "query_type": query_type
        }
        
        return combined_result
    
    elif agent_type == "hr":
        # Direct HR query (for hierarchy queries that don't need employee info)
        endpoint = HR_AGENT_URL
        print(f"Routing to HR Agent for {query_type} query")
        
        if use_llm:
            import asyncio
            criteria = asyncio.run(call_llm(user_query))
            payload = {"query": json.dumps(criteria) if criteria else user_query}
        else:
            payload = {"query": user_query}
        
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
            return {"error": f"Error communicating with HR Agent: {str(e)}"}
    
    else:
        # Employee Info Agent query
        endpoint = EMPLOYEE_AGENT_URL
        print(f"Routing to Employee Info Agent for general query")
        
        if use_llm:
            import asyncio
            criteria = asyncio.run(call_llm(user_query))
            payload = {"query": json.dumps(criteria) if criteria else user_query}
        else:
            payload = {"query": user_query}
        
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
            return {"error": f"Error communicating with Employee Info Agent: {str(e)}"}

def format_response(result: dict) -> str:
    """
    Format the response for better display.
    """
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    if "employee_info" in result and "hr_info" in result:
        # Multi-agent response
        employee = result["employee_info"]
        hr_data = result["hr_info"]
        query_type = result["query_type"]
        
        response = f"👤 Employee: {employee['name']} (ID: {employee['id']})\n"
        response += f"🌍 Country: {employee['country']}\n"
        response += f"💼 Job Role: {employee['job_role']}\n\n"
        
        if query_type == "salary" and hr_data:
            salary = hr_data[0]
            response += f"💰 Salary Information:\n"
            response += f"   Base Salary: {salary['base_salary']} {salary['currency']}\n"
            response += f"   Bonus Eligible: {'Yes' if salary['bonus_eligibility'] else 'No'}\n"
        
        elif query_type == "schedule" and hr_data:
            schedule = hr_data[0]
            response += f"📅 Schedule Information:\n"
            response += f"   Work Days: {', '.join(schedule['work_days'])}\n"
            response += f"   Hours: {schedule['start_time']} - {schedule['end_time']}\n"
            response += f"   Timezone: {schedule['timezone']}\n"
            response += f"   Shift Type: {schedule['shift_type']}\n"
        
        return response
    
    elif "results" in result:
        # Single agent response
        if not result["results"]:
            return "❌ No results found"
        
        response = "📋 Results:\n"
        for item in result["results"]:
            if "name" in item:  # Employee info
                response += f"   {item['name']} (ID: {item['id']}) - {item['job_role']} from {item['country']}\n"
            elif "base_salary" in item:  # Salary info
                response += f"   Salary: {item['base_salary']} {item['currency']} (Bonus: {'Yes' if item['bonus_eligibility'] else 'No'})\n"
            elif "job_role" in item:  # Hierarchy info
                response += f"   {item['job_role']} (Level: {item['level']}, Reports to: {item['reports_to'] or 'None'})\n"
            elif "work_days" in item:  # Schedule info
                response += f"   Schedule: {', '.join(item['work_days'])} {item['start_time']}-{item['end_time']} {item['timezone']}\n"
        
        return response
    
    return "❌ Unexpected response format"

def main():
    print("A2A Client AI Agent CLI (V3 - Multi-Agent Communication)")
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
            formatted_response = format_response(result)
            print(formatted_response)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 