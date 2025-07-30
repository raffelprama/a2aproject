# A2A Employee Information System (V4)

This project demonstrates a clean, production-ready Agent-to-Agent (A2A) system for employee information, where all backend agents return raw data and the client agent LLM does all reasoning, ranking, and answer formatting.

- **Employee Information Agent:** Returns all employee data for relevant queries (no filtering/ranking).
- **HR Agent:** Returns all salary, hierarchy, or schedule data for relevant queries (no filtering/ranking).
- **Client AI Agent (V4):** LLM-powered CLI tool that fetches all data and uses the LLM to process, rank, and answer any user query (e.g., 'second highest salary', 'top 3', etc.).

## Features
- In-memory dummy employee and HR data (40 records)
- A2A-compliant REST APIs (FastAPI) for both agents
- **LLM-powered query clarification, reasoning, and natural language response**
- **All backend agents return raw data; all logic is handled by the client agent LLM**
- CLI-based chatbot for querying employee and HR data
- Simulated API key authentication (dekallm)
- Agent orchestration using LangGraph

## Requirements
- Python 3.9+
- FastAPI
- Uvicorn
- LangChain/LangGraph
- python-dotenv
- pydantic
- httpx
- requests

## Setup
1. Clone the repository and navigate to the `project` directory.
2. Create a `.env` file in the project directory with the following content:
   ```env
   API_KEY=your_api_key_here
   API_URL=http://dekallm.cloudeka.ai/v1/chat/completions
   MODEL=qwen/qwen25-72b-instruct
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn langchain langgraph python-dotenv pydantic httpx requests
   ```
4. Start the Employee Info Agent (Port 8000):
   ```bash
   uvicorn remote_agent:app --reload --port 8000
   ```
5. Start the HR Agent (Port 8001):
   ```bash
   uvicorn hr_agent:app --reload --port 8001
   ```
6. Run the Client Agent (V4):
   ```bash
   python client_agent_v4.py
   ```

## Usage

### Natural Language Queries
- `who is the second highest salary`
- `top 3 salaries`
- `who has the lowest salary`
- `who has the highest role`
- `find marketing people`
- `alice schedule`

**How it works:**
- The client agent always fetches all relevant data (e.g., all salaries, all employees) from the backend agents.
- The LLM in the client agent processes, ranks, and answers the query using the raw data.
- All answer formatting and logic is handled by the LLM, not the backend agents.

### Example Interactions

**Input:** `who is the second highest salary`
**Response:** `Mike CTO has the second highest salary: 200,000 CAD`

**Input:** `top 3 salaries`
**Response:** `1. Sarah CEO: 250,000 USD
2. Mike CTO: 200,000 CAD
3. Lisa CFO: 180,000 GBP`

**Input:** `who has the lowest role`
**Response:** `David Wilson has the lowest role: Financial Analyst (Level 8)`

## Project Structure
- `remote_agent.py` - Employee Information Agent (returns all employees for 'all employees' queries)
- `hr_agent.py` - HR Agent (returns all salary data for salary queries)
- `client_agent_v4.py` - LLM-powered client agent (all logic and answer formatting)
- `hr_dummy_data.py` - HR dummy data (salaries, hierarchy, schedules)
- `README.md` - This file
- `log.md` - Development log

## System Architecture
```
Client Agent (V4, LLM-powered)
        ↓
Employee Info Agent (raw data)   HR Agent (raw data)
        ↓                        ↓
      [All data to LLM]
        ↓
   LLM does all reasoning
```

## Notes
- All employee and HR data is in-memory and for demonstration only.
- API key authentication is simulated (not secure).
- All backend agents are now simple data providers; all logic is handled by the client agent LLM.
- The codebase is now clean, production-ready, and easy to extend. 