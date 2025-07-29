# Software Requirements Specification (SRS) for A2A Employee Information System

## 1. Introduction
### 1.1. Purpose
This document outlines the requirements for an Agent-to-Agent (A2A) communication system designed to retrieve employee information. The system will consist of two main components: a Remote AI Agent (Agent Skill) that manages employee data and exposes it via the A2A protocol, and a Client AI Agent (Chatbot) that interacts with the Remote Agent through a Command Line Interface (CLI) to fetch and display employee details.

### 1.2. Scope
The scope of this project includes the development of:
- A Remote AI Agent (Agent Skill) capable of storing and querying dummy employee data (ID, name, country, job role).
- A RESTful API for the Remote Agent, compliant with the A2A protocol, deployable via Uvicorn.
- A Client AI Agent (Chatbot) that interacts with the Remote Agent via CLI.
- Integration points for dekallm API keys for simulated authentication/authorization.
- The use of langraph (or a similar agent orchestration library like LangChain) for defining agent capabilities.

This project does not include:
- A graphical user interface (GUI) for either agent.
- Complex natural language understanding (NLU) or generation (NLG) beyond basic keyword matching for the demo.
- Robust error handling or production-grade security measures beyond API key simulation.
- Integration with actual dekallm services for LLM inference (it's simulated for API key usage).
- Database persistence for employee data (it will be in-memory dummy data).

### 1.3. Definitions, Acronyms, and Abbreviations
- **A2A**: Agent-to-Agent Protocol
- **AI Agent**: An autonomous software entity capable of perceiving its environment, making decisions, and taking actions.
- **API**: Application Programming Interface
- **CLI**: Command Line Interface
- **LLM**: Large Language Model
- **SRS**: Software Requirements Specification
- **Uvicorn**: An ASGI web server for Python.
- **Dekallm**: A placeholder for an external LLM API provider.
- **Langraph**: A library for building robust, stateful, and multi-actor applications with LLMs.

## 2. Overall Description
### 2.1. Product Perspective
This system is a standalone demonstration of A2A protocol communication between two Python-based AI agents. The Remote Agent acts as a data provider, and the Client Agent acts as a consumer.

### 2.2. Product Functions
**Remote AI Agent (Agent Skill):**
- Store and manage a predefined set of dummy employee data.
- Expose an A2A-compliant endpoint to receive requests.
- Process requests to retrieve employee information based on provided criteria (e.g., ID, name, job role).
- Respond with structured employee data.

**Client AI Agent (Chatbot):**
- Accept user input via the CLI.
- Formulate A2A requests to the Remote Agent.
- Send requests and receive responses.
- Parse responses and display relevant employee information to the user.

### 2.3. User Characteristics
- **Developer/Demonstrator**: Will interact with both agents via the command line, understand Python code, and potentially modify it for further experimentation.
- **End-User (simulated)**: Will interact with the Client AI Agent via simple text commands.

### 2.4. General Constraints
- **Technology Stack**: Python 3.9+, FastAPI, Uvicorn, A2A Python SDK, LangChain/LangGraph.
- **API Key**: Simulated dekallm API keys are required for both agents.
- **Deployment**: Remote Agent will be deployed locally using Uvicorn.
- **Data**: Employee data is static and in-memory (dummy data).

## 3. Specific Requirements
### 3.1. Functional Requirements
#### 3.1.1. Remote AI Agent (Agent Skill)
- **FR-RA-001: Employee Data Management**: The agent SHALL store a predefined set of 30 dummy employee records. Each record SHALL include:
  - id (unique identifier)
  - name (full name)
  - country (country of origin/residence)
  - job_role (job title within the company)
- **FR-RA-002: A2A Endpoint Exposure**: The agent SHALL expose an HTTP endpoint (e.g., /tasks/send) compliant with the A2A protocol specification.
- **FR-RA-003: Request Processing**: The agent SHALL be able to receive A2A Task requests containing queries for employee information.
- **FR-RA-004: Employee Information Retrieval**: The agent SHALL implement a "skill" to search for employee records based on one or more criteria (e.g., ID, name, job role, country). The search SHALL be case-insensitive for string fields.
- **FR-RA-005: Response Generation**: The agent SHALL generate an A2A Task response containing the retrieved employee data (if found) or an appropriate message indicating no match.
- **FR-RA-006: API Key Validation (Simulated)**: The agent SHALL expect a dekallm API key (e.g., in a header or query parameter) and simulate its validation before processing requests. If the key is missing or invalid, it SHALL return an error.
- **FR-RA-007: LangGraph Integration**: The agent's employee data retrieval logic SHALL be encapsulated within a LangChain/LangGraph runnable or tool to demonstrate agentic capabilities.

#### 3.1.2. Client AI Agent (Chatbot)
- **FR-CA-001: CLI Interaction**: The agent SHALL provide a command-line interface for user input.
- **FR-CA-002: Query Formulation**: The agent SHALL interpret user input (e.g., "find employee with ID 123", "who is John Doe", "employees in marketing") and formulate appropriate A2A Task requests.
- **FR-CA-003: A2A Communication**: The agent SHALL send formulated A2A requests to the Remote Agent's endpoint.
- **FR-CA-004: Response Display**: The agent SHALL receive A2A responses from the Remote Agent, parse the employee data, and display it to the user in a readable format.
- **FR-CA-005: Error Handling**: The agent SHALL display informative messages for communication errors or if the Remote Agent returns an error.
- **FR-CA-006: API Key Inclusion (Simulated)**: The agent SHALL include a dekallm API key in its requests to the Remote Agent.

### 3.2. Non-Functional Requirements
- **NFR-001: Performance**: Response time for employee queries should be under 2 seconds for the given dummy data.
- **NFR-002: Security (Simulated)**: API keys are used for simulated authentication. Actual security measures (e.g., OAuth, robust key management) are out of scope for this demo.
- **NFR-003: Maintainability**: The code should be well-commented and modular, allowing for easy understanding and future extensions.
- **NFR-004: Usability**: The CLI for the Client Agent should be intuitive for basic queries.
- **NFR-005: Scalability**: Not a primary concern for this demo, as data is in-memory and deployment is local.

## 4. System Architecture
The system follows a client-server architecture based on the A2A protocol.

```
+---------------------+           +---------------------+
|                     |           |                     |
|  Client AI Agent    |           |  Remote AI Agent    |
|  (Chatbot)          |           |  (Agent Skill)      |
|                     |           |                     |
| - CLI Input/Output  | --------> | - FastAPI Server    |
| - A2A Client SDK    |           | - A2A Server SDK    |
| - Request Formulator|           | - LangChain/LangGraph|
| - Response Parser   | <-------- |   (Employee Skill)  |
| - Dekallm API Key   |           | - Dummy Employee Data|
|                     |           | - Dekallm API Key   |
+---------------------+           +---------------------+
      (Python Script)                     (Uvicorn)
```

## 5. Data Model
### 5.1. Employee Data Structure
Employee data will be stored as a list of dictionaries in Python. Each dictionary will represent an employee with the following keys:
- id (int)
- name (str)
- country (str)
- job_role (str)

## 6. Use Cases
### 6.1. Use Case: Retrieve Employee by ID
**Actor:** User (via Client AI Agent)

**Preconditions:** Remote Agent is running.

**Flow:**
1. User types a query like "find employee with ID 123" into the Client Agent CLI.
2. Client Agent parses the query, extracts the ID, and creates an A2A Task request.
3. Client Agent sends the request to the Remote Agent, including the API key.
4. Remote Agent receives the request, validates the API key, and uses its employee skill to find the employee by ID.
5. Remote Agent constructs an A2A Task response with the employee's details or a "not found" message.
6. Remote Agent sends the response back to the Client Agent.
7. Client Agent parses the response and displays the employee's details or the "not found" message to the user.

### 6.2. Use Case: Retrieve Employees by Job Role
**Actor:** User (via Client AI Agent)

**Preconditions:** Remote Agent is running.

**Flow:**
1. User types a query like "show me employees in marketing" into the Client Agent CLI.
2. Client Agent parses the query, extracts the job role, and creates an A2A Task request.
3. Client Agent sends the request to the Remote Agent, including the API key.
4. Remote Agent receives the request, validates the API key, and uses its employee skill to find all employees with that job role.
5. Remote Agent constructs an A2A Task response with a list of employee details or a "not found" message.
6. Remote Agent sends the response back to the Client Agent.
7. Client Agent parses the response and displays the list of employees or the "not found" message to the user.

## 7. Future Enhancements (Out of Scope for Initial Release)
- Integration with a persistent database (e.g., SQLite, PostgreSQL) for employee data.
- More sophisticated natural language processing for query parsing.
- Support for additional query parameters (e.g., age, hire date).
- Deployment to a cloud platform.
- Robust error logging and monitoring.
- Implementation of streaming or push notifications for long-running tasks. 