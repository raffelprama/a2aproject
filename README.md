# A2A Employee Information System (V2)

This project demonstrates an expanded Agent-to-Agent (A2A) communication system for retrieving various types of employee information using three Python-based AI agents:

- **Employee Information Agent:** Manages and serves general employee data via a RESTful API (A2A protocol, FastAPI/Uvicorn).
- **HR Agent:** Manages and serves sensitive HR-related data (salary, job hierarchy, schedules) via a separate RESTful API.
- **Client AI Agent (V2):** CLI tool that intelligently routes queries to the appropriate agent and displays results.

## Features
- In-memory dummy employee data (30 records)
- In-memory dummy HR data (salaries, job hierarchy, work schedules)
- A2A-compliant REST APIs (FastAPI) for both agents
- Intelligent query routing in Client Agent
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
   API_KEY=sk-G1_wkZ37sEmY4eqnGdcNig
   API_URL=http://dekallm.cloudeka.ai/v1/chat/completions
   MODEL=qwen/qwen25-72b-instruct
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn langchain langgraph python-dotenv pydantic httpx requests
   ```
4. Start the Employee Information Agent:
   ```bash
   uvicorn remote_agent:app --reload --port 8000
   ```
5. Start the HR Agent (in a new terminal):
   ```bash
   uvicorn hr_agent:app --reload --port 8001
   ```
6. Run the Client AI Agent (V2):
   ```bash
   python client_agent_v2.py
   ```

## Usage

### Employee Information Queries
- `find employee with ID 123`
- `who is John Doe`
- `employees in marketing`
- `show me employees in Japan`

### HR Queries
- `what is Alice Smith's salary`
- `salary for ID 1`
- `who reports to Product Manager`
- `hierarchy for Software Engineer`
- `what is Bob Johnson's schedule`
- `schedule for ID 2`

The Client Agent will automatically route your query to the appropriate agent and display the results.

## Project Structure
- `remote_agent.py` - Employee Information Agent (FastAPI server on port 8000)
- `hr_agent.py` - HR Agent (FastAPI server on port 8001)
- `client_agent_v2.py` - Client AI Agent with routing (CLI tool)
- `hr_dummy_data.py` - HR dummy data (salaries, hierarchy, schedules)
- `SRS.md` - Software Requirements Specification (V2)
- `log.md` - Development log

## System Architecture
```
Client Agent (V2) → Employee Info Agent (Port 8000)
                → HR Agent (Port 8001)
```

## Notes
- All employee and HR data is in-memory and for demonstration only.
- API key authentication is simulated (not secure).
- The Client Agent V2 intelligently routes queries based on keywords.
- See `SRS.md` for detailed requirements and architecture. 