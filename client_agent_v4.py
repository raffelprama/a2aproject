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

async def call_llm(prompt: str, user_query: str, temperature: float = 0.2) -> str:
    """
    Call the LLM with a specific prompt and user query.
    """
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

def get_all_employees() -> dict:
    """
    Get all employee information from Employee Info Agent.
    """
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
    """
    Get all salary information from HR Agent.
    """
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
        # print(f"📥 Response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with HR Agent: {str(e)}"}

def perform_comparison(query_type: str) -> dict:
    """
    Perform comparison queries (highest/lowest salary, role, etc.).
    """
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
            
            # Sort by salary
            if query_type == "highest_salary":
                combined_data.sort(key=lambda x: x["salary"]["base_salary"], reverse=True)
                result = combined_data[0]
                return {
                    "comparison_type": "highest_salary",
                    "result": result,
                    "message": f"{result['employee']['name']} has the highest salary: {result['salary']['base_salary']} {result['salary']['currency']}"
                }
            else:  # lowest_salary
                combined_data.sort(key=lambda x: x["salary"]["base_salary"])
                result = combined_data[0]
                return {
                    "comparison_type": "lowest_salary",
                    "result": result,
                    "message": f"{result['employee']['name']} has the lowest salary: {result['salary']['base_salary']} {result['salary']['currency']}"
                }
        
        elif query_type in ["highest_role", "lowest_role"]:
            # Get all employees
            employees_result = get_all_employees()
            
            if "error" in employees_result:
                return {"error": "Failed to get employee data"}
            
            employees = employees_result.get("results", [])
            
            if not employees:
                return {"error": "No employee data found"}
            
            # Define role hierarchy (lower number = higher role)
            role_hierarchy = {
                "CEO": 1, "CTO": 2, "CFO": 2, "COO": 2, "CMO": 2,
                "VP Engineering": 3, "VP Sales": 3, "VP Marketing": 3,
                "Director IT": 4, "Director HR": 4,
                "Engineering Manager": 5, "Lead Data Scientist": 5, "Product Manager": 5,
                "Lead Engineer": 6, "Data Scientist": 7, "Software Engineer": 8,
                "UX Designer": 8, "DevOps Engineer": 8, "Marketing Specialist": 8,
                "HR Manager": 8, "Financial Analyst": 8, "Technical Writer": 8,
                "Sales Representative": 8, "Customer Support": 8, "Business Analyst": 8,
                "Legal Counsel": 8, "Research Scientist": 8, "Project Coordinator": 8,
                "Network Engineer": 8, "Content Creator": 8, "Operations Manager": 8,
                "Data Engineer": 8, "Accountant": 8, "QA Engineer": 8,
                "Cloud Architect": 8, "Scrum Master": 8, "Cybersecurity Analyst": 8,
                "Product Designer": 8, "Machine Learning Engineer": 8
            }
            
            # Add hierarchy level to each employee
            for emp in employees:
                emp["role_level"] = role_hierarchy.get(emp["job_role"], 9)  # Default to lowest level
            
            # Sort by role level
            if query_type == "highest_role":
                employees.sort(key=lambda x: x["role_level"])
                result = employees[0]
                return {
                    "comparison_type": "highest_role",
                    "result": result,
                    "message": f"{result['name']} has the highest role: {result['job_role']} (Level {result['role_level']})"
                }
            else:  # lowest_role
                employees.sort(key=lambda x: x["role_level"], reverse=True)
                result = employees[0]
                return {
                    "comparison_type": "lowest_role",
                    "result": result,
                    "message": f"{result['name']} has the lowest role: {result['job_role']} (Level {result['role_level']})"
                }
        
        else:
            return {"error": f"Unknown comparison type: {query_type}"}
            
    except Exception as e:
        return {"error": f"Error performing comparison: {str(e)}"}

async def generate_natural_response(user_query: str, result: dict) -> str:
    """
    Use LLM to generate a natural language response based on the query and results.
    """
    if "error" in result:
        return f"I'm sorry, but I encountered an error: {result['error']}"
    
    # Prepare context for LLM
    context = {
        "user_query": user_query,
        "result": result
    }
    
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
    """
    Route the query to the appropriate agent(s) and return the response.
    """
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