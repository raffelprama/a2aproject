import requests
import httpx
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_URL')
model = os.getenv('MODEL')

# Agent endpoints
EMPLOYEE_AGENT_URL = "http://localhost:8000/tasks/send"
HR_AGENT_URL = "http://localhost:8001/hr-tasks/send"
API_KEY = "dummy-dekallm-key"

async def call_llm(prompt: str, user_query: str, temperature: float = 0.2) -> str:
    """Call the LLM with a specific prompt and user query."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": temperature
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
            return content.strip()
        except Exception as e:
            print(f"LLM parse error: {e}")
            return ""

async def clarify_user_query(user_query: str) -> str:
    """
    Use LLM to clarify and improve the user's query for better processing.
    """
    prompt = (
        "You are a helpful assistant that clarifies and improves user queries about employee information. "
        "Your job is to make the query more specific and clear for processing by AI agents.\n\n"
        "Examples:\n"
        "- 'bob salary' → 'What is Bob Johnson's salary?'\n"
        "- 'alice schedule' → 'What is Alice Smith's work schedule?'\n"
        "- 'find employee 5' → 'Find employee with ID 5'\n"
        "- 'who works in marketing' → 'Find employees with job role Marketing Specialist'\n"
        "- 'hr manager' → 'Find employees with job role HR Manager'\n"
        "- 'who has highest salary' → 'Who has the highest salary?'\n"
        "- 'who has lowest salary' → 'Who has the lowest salary?'\n"
        "- 'who has highest role' → 'Who has the highest role?'\n"
        "- 'who has lowest role' → 'Who has the lowest role?'\n\n"
        "Return only the clarified query, nothing else."
    )
    
    return await call_llm(prompt, user_query, temperature=0.1)

async def extract_search_criteria(user_query: str) -> dict:
    """
    Extract search criteria from user query using LLM.
    """
    prompt = (
        "You are an assistant that extracts employee search criteria from user queries. "
        "Return a JSON object with any found fields (id, name, country, job_role).\n\n"
        "Examples:\n"
        "User: 'who is the hr manager' → {\"job_role\": \"HR Manager\"}\n"
        "User: 'find employee with ID 2' → {\"id\": 2}\n"
        "User: 'show me employees in marketing' → {\"job_role\": \"Marketing Specialist\"}\n"
        "User: 'who is Alice Smith' → {\"name\": \"Alice Smith\"}\n"
        "User: 'employees in Japan' → {\"country\": \"Japan\"}\n\n"
        "Return only valid JSON, no other text."
    )
    
    response = await call_llm(prompt, user_query, temperature=0.1)
    try:
        import re
        # Clean up response if it has markdown formatting
        response = re.sub(r"^```json\s*|```$", "", response.strip(), flags=re.MULTILINE)
        criteria = json.loads(response)
        return criteria
    except Exception as e:
        print(f"Failed to parse criteria: {e}")
        return {}

async def determine_agent_and_query_type(user_query: str) -> tuple[str, str]:
    """
    Use LLM to determine which agent to route to and what type of query it is.
    """
    prompt = (
        "You are an assistant that determines the routing strategy for employee queries.\n\n"
        "Return a JSON object with two fields:\n"
        "- agent_type: 'employee', 'hr', 'multi_agent', or 'comparison'\n"
        "- query_type: 'salary', 'hierarchy', 'schedule', 'general', 'highest_salary', 'lowest_salary', 'highest_role', 'lowest_role'\n\n"
        "Rules:\n"
        "- 'multi_agent': for salary/schedule queries about specific people\n"
        "- 'hr': for hierarchy queries or general HR info\n"
        "- 'employee': for general employee information\n"
        "- 'comparison': for queries asking about highest/lowest (salary, role, etc.)\n\n"
        "Examples:\n"
        "User: 'What is Bob's salary?' → {\"agent_type\": \"multi_agent\", \"query_type\": \"salary\"}\n"
        "User: 'Show me the hierarchy' → {\"agent_type\": \"hr\", \"query_type\": \"hierarchy\"}\n"
        "User: 'Find Alice Smith' → {\"agent_type\": \"employee\", \"query_type\": \"general\"}\n"
        "User: 'Who has the highest salary?' → {\"agent_type\": \"comparison\", \"query_type\": \"highest_salary\"}\n"
        "User: 'Who has the lowest salary?' → {\"agent_type\": \"comparison\", \"query_type\": \"lowest_salary\"}\n"
        "User: 'Who has the highest role?' → {\"agent_type\": \"comparison\", \"query_type\": \"highest_role\"}\n"
        "User: 'Who has the lowest role?' → {\"agent_type\": \"comparison\", \"query_type\": \"lowest_role\"}\n\n"
        "Return only valid JSON, no other text."
    )
    
    response = await call_llm(prompt, user_query, temperature=0.1)
    try:
        import re
        response = re.sub(r"^```json\s*|```$", "", response.strip(), flags=re.MULTILINE)
        result = json.loads(response)
        return result.get("agent_type", "employee"), result.get("query_type", "general")
    except Exception as e:
        print(f"Failed to parse routing decision: {e}")
        return "employee", "general"

def get_employee_info(employee_query: str) -> dict:
    """Get employee information from Employee Info Agent."""
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
    """Get HR information from HR Agent using employee ID."""
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

def get_all_employees() -> dict:
    """Get all employee information from Employee Info Agent."""
    try:
        print("🔍 Getting all employees from Employee Info Agent...")
        response = requests.post(
            EMPLOYEE_AGENT_URL,
            headers={"x-api-key": API_KEY},
            json={"query": "all employees"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Got {len(result.get('results', []))} employees")
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with Employee Info Agent: {str(e)}"}

def get_all_salaries() -> dict:
    """Get all salary information from HR Agent."""
    try:
        print("💰 Getting all salaries from HR Agent...")
        payload = {"query": "all salaries", "query_type": "salary"}
        print(f"📤 Sending payload: {payload}")
        response = requests.post(
            HR_AGENT_URL,
            headers={"x-api-key": API_KEY},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Got {len(result.get('results', []))} salary records")
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with HR Agent: {str(e)}"}

def perform_comparison(query_type: str) -> dict:
    """For salary queries, just return all salary data and let LLM handle the reasoning."""
    try:
        if query_type in ["highest_salary", "lowest_salary"]:
            # Get all employees and salaries
            employees_result = get_all_employees()
            salaries_result = get_all_salaries()
            
            if "error" in employees_result or "error" in salaries_result:
                return {"error": "Failed to get employee or salary data"}
            
            # Combine employee and salary data
            employees = employees_result.get("results", [])
            salaries = salaries_result.get("results", [])
            
            # Create a mapping of employee_id to salary
            salary_map = {s["employee_id"]: s for s in salaries}
            
            # Combine employee info with salary info
            combined_data = []
            for emp in employees:
                if emp["id"] in salary_map:
                    combined_data.append({
                        "employee": emp,
                        "salary": salary_map[emp["id"]]
                    })
            
            if not combined_data:
                return {"error": "No employee salary data found"}
            
            # Return all combined data for LLM to process
            return {
                "comparison_type": "salary_data",
                "results": combined_data,
                "message": f"Found {len(combined_data)} employee salary records"
            }
        
        elif query_type in ["highest_role", "lowest_role"]:
            # Get all employees
            employees_result = get_all_employees()
            
            if "error" in employees_result:
                return {"error": "Failed to get employee data"}
            
            employees = employees_result.get("results", [])
            
            if not employees:
                return {"error": "No employee data found"}
            
            # Return all employee data for LLM to process
            return {
                "comparison_type": "role_data",
                "results": employees,
                "message": f"Found {len(employees)} employee records"
            }
        
        else:
            return {"error": f"Unknown comparison type: {query_type}"}
            
    except Exception as e:
        return {"error": f"Error performing comparison: {str(e)}"}

async def generate_natural_response(user_query: str, result: dict) -> str:
    """Use LLM to generate a natural language response based on the query and results."""
    if "error" in result:
        return f"I'm sorry, but I encountered an error: {result['error']}"
    

    
    # If this is a salary comparison, pass all salary data to the LLM
    if (
        isinstance(result, dict) and (
            result.get("comparison_type") in ["salary_data", "role_data"] or
            (isinstance(result.get("result"), dict) and "salary" in result.get("result", {})) or
            (isinstance(result.get("result"), list) and all("salary" in r for r in result.get("result", [])))
        )
    ) or (
        isinstance(result, list) and all("base_salary" in r for r in result)
    ):
        # Extract the data for LLM processing
        if isinstance(result, dict) and result.get("comparison_type") == "salary_data":
            salary_data = result.get("results", [])
            prompt = (
                "You are a helpful HR assistant. You are given a list of all employee salaries as JSON. "
                "Answer the user's question using only this data. "
                "If the user asks for the second highest salary, find it from the data. "
                "If the user asks for the lowest salary, find it from the data. "
                "If the user asks for the top 3, return the top 3, etc.\n\n"
                "User Query: {user_query}\n"
                "Salary Data: {salary_data}\n\n"
                "Provide a clear, natural answer:"
            ).format(user_query=user_query, salary_data=json.dumps(salary_data, indent=2))
        elif isinstance(result, dict) and result.get("comparison_type") == "role_data":
            role_data = result.get("results", [])
            prompt = (
                "You are a helpful HR assistant. You are given a list of all employees as JSON. "
                "Answer the user's question using only this data. "
                "If the user asks for the highest role, find it from the data. "
                "If the user asks for the lowest role, find it from the data. "
                "If the user asks for the top 3 roles, return the top 3, etc.\n\n"
                "User Query: {user_query}\n"
                "Employee Data: {role_data}\n\n"
                "Provide a clear, natural answer:"
            ).format(user_query=user_query, role_data=json.dumps(role_data, indent=2))
        else:
            # Fallback for other salary data structures
            salary_data = result if isinstance(result, list) else result.get("result") or result.get("results") or result
            prompt = (
                "You are a helpful HR assistant. You are given a list of all employee salaries as JSON. "
                "Answer the user's question using only this data. "
                "If the user asks for the second highest salary, find it from the data. "
                "If the user asks for the lowest salary, find it from the data. "
                "If the user asks for the top 3, return the top 3, etc.\n\n"
                "User Query: {user_query}\n"
                "Salary Data: {salary_data}\n\n"
                "Provide a clear, natural answer:"
            ).format(user_query=user_query, salary_data=json.dumps(salary_data, indent=2))
        return await call_llm(prompt, "", temperature=0.3)
    
    # Default: previous behavior
    prompt = (
        "You are a helpful HR assistant that provides natural, conversational responses about employee information. "
        "Based on the user's query and the data results, provide a clear and helpful response.\n\n"
        "Guidelines:\n"
        "- Be conversational and friendly\n"
        "- Include relevant details from the data\n"
        "- If no results found, explain that clearly\n"
        "- For multi-agent results, combine employee info with HR data naturally\n"
        "- Use appropriate formatting for readability\n\n"
        "User Query: {user_query}\n"
        "Data Results: {result}\n\n"
        "Provide a natural response:"
    ).format(user_query=user_query, result=json.dumps(result, indent=2))
    return await call_llm(prompt, "", temperature=0.3)

async def route_query_to_agent(user_query: str) -> dict:
    """Route the query to the appropriate agent(s) and return the response."""
    # Step 1: Clarify the user query
    print("🔍 Clarifying user query...")
    clarified_query = await clarify_user_query(user_query)
    print(f"Clarified query: {clarified_query}")
    
    # Step 2: Determine routing strategy
    print("🎯 Determining routing strategy...")
    agent_type, query_type = await determine_agent_and_query_type(clarified_query)
    print(f"Routing: {agent_type} for {query_type} query")
    
    if agent_type == "multi_agent":
        # Multi-agent communication: Employee Info → HR Agent
        print("🔄 Step 1: Getting employee information...")
        employee_result = get_employee_info(clarified_query)
        
        if "error" in employee_result:
            return employee_result
        
        if not employee_result.get("results"):
            return {"error": "Employee not found"}
        
        # Extract employee ID from the first result
        employee = employee_result["results"][0]
        employee_id = employee.get("id")
        
        if not employee_id:
            return {"error": "Could not determine employee ID"}
        
        print(f"✅ Found employee: {employee['name']} (ID: {employee_id})")
        print(f"🔄 Step 2: Getting {query_type} information from HR Agent...")
        
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
    
    elif agent_type == "comparison":
        # Comparison queries (highest/lowest salary, role, etc.)
        print(f"📊 Performing comparison query: {query_type}")
        return perform_comparison(query_type)
    
    elif agent_type == "hr":
        # Direct HR query (for hierarchy queries that don't need employee info)
        endpoint = HR_AGENT_URL
        print(f"📊 Routing to HR Agent for {query_type} query")
        
        # Extract criteria using LLM
        criteria = await extract_search_criteria(clarified_query)
        payload = {"query": json.dumps(criteria) if criteria else clarified_query}
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
        print(f"👥 Routing to Employee Info Agent for general query")
        
        # Extract criteria using LLM
        criteria = await extract_search_criteria(clarified_query)
        payload = {"query": json.dumps(criteria) if criteria else clarified_query}
        
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

async def main():
    print("🤖 A2A Client AI Agent CLI (V4 - LLM-Powered)")
    print("Type your query (or 'exit' to quit):")
    print("💡 The system will clarify your query and provide natural responses!")
    print("📊 New: Try comparison queries like 'who has highest salary' or 'who has lowest role'")
    
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "exit":
            break
        
        if not user_input:
            continue
            
        try:
            print("\n" + "="*50)
            result = await route_query_to_agent(user_input)
            
            # Generate natural language response
            print("🤖 Generating natural response...")
            print(f"input = {user_input}")
            print(f"result = {result}")
            natural_response = await generate_natural_response(user_input, result)
            print("\n" + "="*50)
            print("💬 Response:")
            print(natural_response)
            print("="*50)
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 