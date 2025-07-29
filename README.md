# A2A Employee Information System

This project demonstrates an Agent-to-Agent (A2A) communication system for retrieving employee information using two Python-based AI agents:

- **Remote AI Agent (Agent Skill):** Manages and serves employee data via a RESTful API (A2A protocol, FastAPI/Uvicorn).
- **Client AI Agent (Chatbot):** CLI tool that queries the Remote Agent for employee information.

## Features
- In-memory dummy employee data (30 records)
- A2A-compliant REST API (FastAPI)
- CLI-based chatbot for querying employee data
- Simulated API key authentication (dekallm)
- Agent orchestration using LangGraph or LangChain

## Requirements
- Python 3.9+
- FastAPI
- Uvicorn
- LangChain or LangGraph
- python-dotenv
- pydantic
- (A2A Python SDK, if available)

## Setup
1. Clone the repository and navigate to the `project` directory.
2. Create a `.env` file in the project directory with the following content:
   ```env
   API_KEY=sk-G1_wkZ37sEmY4eqnGdcNig
   API_URL=https://dekallm.cloudeka.ai/v1/chat/completions/
   MODEL=qwen/qwen25-72b-instruct
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn langchain langgraph python-dotenv pydantic
   ```
4. Start the Remote AI Agent:
   ```bash
   uvicorn remote_agent:app --reload
   ```
5. In a new terminal, run the Client AI Agent:
   ```bash
   python client_agent.py
   ```

## Usage
- Use the CLI to type queries like:
  - `find employee with ID 123`
  - `who is John Doe`
  - `employees in marketing`
- The Client Agent will display the results or an error message.

## Project Structure
- `remote_agent.py` - Remote AI Agent (FastAPI server)
- `client_agent.py` - Client AI Agent (CLI tool)
- `SRS.md` - Software Requirements Specification
- `log.md` - Development log

## Notes
- All employee data is in-memory and for demonstration only.
- API key authentication is simulated (not secure).
- See `SRS.md` for detailed requirements and architecture. 