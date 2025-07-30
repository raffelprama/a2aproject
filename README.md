# A2A Employee Information System (V4)

This project demonstrates an expanded Agent-to-Agent (A2A) communication system for retrieving various types of employee information using three Python-based AI agents with LLM-powered natural language processing:

- **Employee Information Agent:** Manages and serves general employee data via a RESTful API (A2A protocol, FastAPI/Uvicorn).
- **HR Agent:** Manages and serves sensitive HR-related data (salary, job hierarchy, schedules) via a separate RESTful API.
- **Client AI Agent (V4):** LLM-powered CLI tool that intelligently routes queries, clarifies user input, and generates natural language responses.

## Features
- In-memory dummy employee data (30 records)
- In-memory dummy HR data (salaries, job hierarchy, work schedules)
- A2A-compliant REST APIs (FastAPI) for both agents
- **LLM-powered query clarification and natural language processing**
- **Intelligent query routing with multi-agent communication**
- **Natural language response generation**
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
6. Run the Client AI Agent (V4):
   ```bash
   python client_agent_v4.py
   ```

## Usage

### Natural Language Queries
The system now supports natural language input with LLM-powered clarification:

**Input Examples:**
- `bob salary`
- `alice schedule`
- `find marketing people`
- `who is employee 5`
- `show hierarchy`

**LLM Processing Flow:**
1. **Query Clarification**: `"bob salary"` → `"What is Bob Johnson's salary?"`
2. **Smart Routing**: Determines which agent(s) to use
3. **Natural Response**: Generates conversational responses

### Example Interactions

**Input:** `"bob salary"`
**Response:** `"Bob Johnson (ID: 2) is a Data Scientist from Canada. His base salary is 85,000 CAD and he is eligible for bonuses."`

**Input:** `"alice schedule"`
**Response:** `"Alice Smith works as a Software Engineer from the United States. Her schedule is Monday to Friday, 9:00 AM to 5:00 PM EST, with a standard day shift."`

The Client Agent V4 automatically routes your query to the appropriate agent(s) and provides natural language responses.

## Project Structure
- `remote_agent.py` - Employee Information Agent (FastAPI server on port 8000)
- `hr_agent.py` - HR Agent (FastAPI server on port 8001)
- `client_agent.py` - Original Client Agent
- `client_agent_v2.py` - Client AI Agent with routing (CLI tool)
- `client_agent_v3.py` - Client AI Agent with multi-agent communication
- `client_agent_v4.py` - **Client AI Agent V4 (LLM-powered)** - Current version
- `hr_dummy_data.py` - HR dummy data (salaries, hierarchy, schedules)
- `SRS.md` - Software Requirements Specification (V2)
- `log.md` - Development log

## System Architecture
```
Client Agent (V4) → Employee Info Agent (Port 8000)
(LLM-Powered)     → HR Agent (Port 8001)
                ↓
        LLM Processing
    (Clarification & Response)
```

## Notes
- All employee and HR data is in-memory and for demonstration only.
- API key authentication is simulated (not secure).
- The Client Agent V4 uses LLM for query clarification and natural response generation.
- See `SRS.md` for detailed requirements and architecture. 