# Software Requirements Specification (SRS) for A2A Employee Information System (V2)

## 1. Introduction
### 1.1. Purpose
This document outlines the requirements for an expanded Agent-to-Agent (A2A) communication system designed to retrieve various types of employee information. The system will now consist of three main components: a Remote AI Agent (Employee Information Agent) that manages general employee data, a new Remote AI Agent (HR Agent) that handles sensitive HR-related data (salary, job hierarchy, schedules), and a Client AI Agent (Chatbot) that acts as the user interface, intelligently routing queries to the appropriate Remote Agent.

### 1.2. Scope
The scope of this project includes the development of:

- A Remote AI Agent (Employee Information Agent) capable of storing and querying dummy employee data (ID, name, country, job role). (Existing)
- A new Remote AI Agent (HR Agent) capable of storing and querying dummy data related to employee salaries, job role hierarchies, and work schedules.
- RESTful APIs for both Remote Agents, compliant with the A2A protocol, deployable via Uvicorn.
- A Client AI Agent (Chatbot) that intelligently routes user queries to either the Employee Information Agent or the HR Agent via CLI.
- Integration points for dekallm API keys for simulated authentication/authorization across all agents.
- The use of langraph (or a similar agent orchestration library like LangChain) for defining agent capabilities within each Remote Agent.

This project does not include:

- A graphical user interface (GUI) for any agent.
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
This system is an expanded demonstration of A2A protocol communication between three Python-based AI agents. The Employee Information Agent and HR Agent act as specialized data providers, and the Client Agent acts as an intelligent consumer and router.

### 2.2. Product Functions
**Remote AI Agent (Employee Information Agent):**
- Store and manage a predefined set of dummy employee data (ID, name, country, job role).
- Expose an A2A-compliant endpoint to receive requests.
- Process requests to retrieve general employee information based on provided criteria (e.g., ID, name, job role, country).
- Respond with structured employee data.

**New Remote AI Agent (HR Agent):**
- Store and manage predefined dummy data for employee salaries, job role hierarchy, and work schedules.
- Expose a separate A2A-compliant endpoint to receive HR-specific requests.
- Process requests to retrieve:
  - Employee salary information.
  - Job role hierarchy details (e.g., who reports to whom, or levels).
  - Employee work schedules/hours.
- Respond with structured HR-related data.

**Client AI Agent (Chatbot):**
- Accept user input via the CLI.
- Intelligently route user queries to either the Employee Information Agent or the HR Agent based on the nature of the query (e.g., "who is X" goes to Employee Info, "what is X's salary" goes to HR Agent).
- Formulate A2A requests to the appropriate Remote Agent.
- Send requests and receive responses.
- Parse responses and display relevant information to the user.

### 2.3. User Characteristics
- **Developer/Demonstrator**: Will interact with all agents via the command line, understand Python code, and potentially modify it for further experimentation.
- **End-User (simulated)**: Will interact with the Client AI Agent via simple text commands.

### 2.4. General Constraints
- **Technology Stack**: Python 3.9+, FastAPI, Uvicorn, A2A Python SDK, LangChain/LangGraph.
- **API Key**: Simulated dekallm API keys are required for all agents.
- **Deployment**: Remote Agents will be deployed locally using Uvicorn on different ports.
- **Data**: Employee and HR data are static and in-memory (dummy data).

## 3. Specific Requirements
### 3.1. Functional Requirements
#### 3.1.1. Remote AI Agent (Employee Information Agent) - (Existing)
- **FR-RA-001**: Employee Data Management: The agent SHALL store a predefined set of 30 dummy employee records. Each record SHALL include: id (unique identifier), name (full name), country (country of origin/residence), job_role (job title within the company).
- **FR-RA-002**: A2A Endpoint Exposure: The agent SHALL expose an HTTP endpoint (e.g., /tasks/send) compliant with the A2A protocol specification.
- **FR-RA-003**: Request Processing: The agent SHALL be able to receive A2A Task requests containing queries for employee information.
- **FR-RA-004**: Employee Information Retrieval: The agent SHALL implement a "skill" to search for employee records based on one or more criteria (e.g., ID, name, job role, country). The search SHALL be case-insensitive for string fields.
- **FR-RA-005**: Response Generation: The agent SHALL generate an A2A Task response containing the retrieved employee data (if found) or an appropriate message indicating no match.
- **FR-RA-006**: API Key Validation (Simulated): The agent SHALL expect a dekallm API key and simulate its validation before processing requests.
- **FR-RA-007**: LangGraph Integration: The agent's employee data retrieval logic SHALL be encapsulated within a LangChain/LangGraph runnable or tool.

#### 3.1.2. New Remote AI Agent (HR Agent)
- **FR-HR-001**: HR Data Management: The agent SHALL store predefined dummy data for:
  - Salaries: Mapping employee IDs to their respective salary information (e.g., base salary, bonus, currency).
  - Job Hierarchy: Defining reporting structures or job levels (e.g., "Software Engineer reports to Lead Engineer").
  - Work Schedules: Mapping employee IDs to their typical working hours or shifts (e.g., "9 AM - 5 PM, Mon-Fri").
- **FR-HR-002**: A2A Endpoint Exposure: The agent SHALL expose its own distinct HTTP endpoint (e.g., /hr-tasks/send) compliant with the A2A protocol.
- **FR-HR-003**: Request Processing: The agent SHALL be able to receive A2A Task requests for HR-specific information.
- **FR-HR-004**: Salary Information Retrieval: The agent SHALL implement a "skill" to retrieve salary details for a given employee ID or name.
- **FR-HR-005**: Hierarchy Information Retrieval: The agent SHALL implement a "skill" to retrieve job role hierarchy information for a given job role or employee.
- **FR-HR-006**: Schedule Information Retrieval: The agent SHALL implement a "skill" to retrieve work schedule details for a given employee ID or name.
- **FR-HR-007**: Response Generation: The agent SHALL generate an A2A Task response with the requested HR data or a "not found" message.
- **FR-HR-008**: API Key Validation (Simulated): The agent SHALL expect a dekallm API key and simulate its validation.
- **FR-HR-009**: LangGraph Integration: The HR agent's data retrieval logic SHALL be encapsulated within LangChain/LangGraph runnables or tools.

#### 3.1.3. Client AI Agent (Chatbot) - (Modified)
- **FR-CA-001**: CLI Interaction: The agent SHALL provide a command-line interface for user input.
- **FR-CA-002**: Query Routing: The agent SHALL analyze user input to determine whether the query pertains to general employee information (Employee Information Agent) or HR-specific information (HR Agent). It SHALL then route the query to the appropriate agent.
- **FR-CA-003**: Query Formulation: The agent SHALL formulate A2A Task requests suitable for the chosen Remote Agent.
- **FR-CA-004**: A2A Communication: The agent SHALL send formulated A2A requests to the appropriate Remote Agent's endpoint.
- **FR-CA-005**: Response Display: The agent SHALL receive A2A responses, parse the relevant data, and display it to the user in a readable format.
- **FR-CA-006**: Error Handling: The agent SHALL display informative messages for communication errors or if a Remote Agent returns an error.
- **FR-CA-007**: API Key Inclusion (Simulated): The agent SHALL include a dekallm API key in its requests to both Remote Agents.

### 3.2. Non-Functional Requirements
- **NFR-001**: Performance: Response time for all queries should be under 3 seconds for the given dummy data.
- **NFR-002**: Security (Simulated): API keys are used for simulated authentication. Actual security measures (e.g., OAuth, robust key management) are out of scope for this demo.
- **NFR-003**: Maintainability: The code should be well-commented and modular, allowing for easy understanding and future extensions. Each agent's logic should be encapsulated.
- **NFR-004**: Usability: The CLI for the Client Agent should be intuitive for basic queries across both types of information.
- **NFR-005**: Scalability: Not a primary concern for this demo, as data is in-memory and deployment is local.

## 4. System Architecture
The system follows a distributed client-server architecture based on the A2A protocol, now featuring three agents.

```
+---------------------+
|                     |
|  Client AI Agent    |
|  (Chatbot)          |
|                     |
| - CLI Input/Output  |
| - A2A Client SDK    |
| - Query Router      | -----+
| - Request Formulator|      |
| - Response Parser   |      |
| - Dekallm API Key   |      |
+---------------------+      |
                             |
         +-------------------------------------------------+
         |                 A2A Protocol                    |
         +-------------------------------------------------+
                  |                                  |
                  V                                  V
+---------------------+                     +---------------------+
|                     |                     |                     |
|  Remote AI Agent    |                     |  New Remote AI Agent|
|  (Employee Info)    |                     |  (HR Agent)         |
|                     |                     |                     |
| - FastAPI Server    |                     | - FastAPI Server    |
| - A2A Server SDK    |                     | - A2A Server SDK    |
| - LangChain/LangGraph|                     | - LangChain/LangGraph|
|   (Employee Skill)  |                     |   (HR Skills)       |
| - Dummy Employee Data|                     | - Dummy HR Data     |
| - Dekallm API Key   |                     | - Dekallm API Key   |
+---------------------+                     +---------------------+
      (Python Script/Uvicorn on Port 8000)      (Python Script/Uvicorn on Port 8001, etc.)
```

## 5. Data Model
### 5.1. Employee Data Structure (Existing)
Employee data will be stored as a list of dictionaries in Python. Each dictionary will represent an employee with the following keys:

- id (int)
- name (str)
- country (str)
- job_role (str)

### 5.2. HR Data Structure (New)
#### 5.2.1. Salaries
A list of dictionaries mapping employee IDs to salary details.

- employee_id (int)
- base_salary (float)
- currency (str)
- bonus_eligibility (bool)

#### 5.2.2. Job Hierarchy
A list of dictionaries defining reporting structures or job levels. This can be simplified for the demo.

- job_role (str)
- reports_to (Optional[str]) - The job role this role reports to.
- level (int) - A numerical representation of the hierarchy level (e.g., 1 for CEO, 5 for individual contributor).

#### 5.2.3. Work Schedules
A list of dictionaries mapping employee IDs to their work schedules.

- employee_id (int)
- work_days (List[str]) - e.g., ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
- start_time (str) - e.g., "09:00 AM"
- end_time (str) - e.g., "05:00 PM"
- timezone (str) - e.g., "GMT+7"

## 6. Use Cases
### 6.1. Use Case: Retrieve Employee by ID (Existing - Routed to Employee Info Agent)
**Actor:** User (via Client AI Agent)

**Preconditions:** Both Remote Agents are running.

**Flow:**
1. User types a query like "find employee with ID 123" into the Client Agent CLI.
2. Client Agent analyzes the query, determines it's general employee info, and routes it to the Employee Information Agent.
3. Client Agent parses the query, extracts the ID, and creates an A2A Task request.
4. Client Agent sends the request to the Employee Information Agent, including the API key.
5. Employee Information Agent receives the request, validates the API key, and uses its employee skill to find the employee by ID.
6. Employee Information Agent constructs an A2A Task response with the employee's details or a "not found" message.
7. Employee Information Agent sends the response back to the Client Agent.
8. Client Agent parses the response and displays the employee's details or the "not found" message to the user.

### 6.2. Use Case: Retrieve Employee Salary (New - Routed to HR Agent)
**Actor:** User (via Client AI Agent)

**Preconditions:** Both Remote Agents are running.

**Flow:**
1. User types a query like "what is Alice Smith's salary?" or "salary for ID 1" into the Client Agent CLI.
2. Client Agent analyzes the query, determines it's HR-related (salary), and routes it to the HR Agent.
3. Client Agent parses the query, extracts the employee identifier, and creates an A2A Task request for salary.
4. Client Agent sends the request to the HR Agent, including the API key.
5. HR Agent receives the request, validates the API key, and uses its salary skill to find the employee's salary.
6. HR Agent constructs an A2A Task response with the salary details or a "not found" message.
7. HR Agent sends the response back to the Client Agent.
8. Client Agent parses the response and displays the salary information or the "not found" message to the user.

### 6.3. Use Case: Retrieve Job Hierarchy Information (New - Routed to HR Agent)
**Actor:** User (via Client AI Agent)

**Preconditions:** Both Remote Agents are running.

**Flow:**
1. User types a query like "what is the hierarchy for Software Engineer?" or "who reports to Product Manager?" into the Client Agent CLI.
2. Client Agent analyzes the query, determines it's HR-related (hierarchy), and routes it to the HR Agent.
3. Client Agent parses the query, extracts the job role, and creates an A2A Task request for hierarchy.
4. Client Agent sends the request to the HR Agent, including the API key.
5. HR Agent receives the request, validates the API key, and uses its hierarchy skill to find the relevant information.
6. HR Agent constructs an A2A Task response with the hierarchy details or a "not found" message.
7. HR Agent sends the response back to the Client Agent.
8. Client Agent parses the response and displays the hierarchy information or the "not found" message to the user.

### 6.4. Use Case: Retrieve Employee Work Schedule (New - Routed to HR Agent)
**Actor:** User (via Client AI Agent)

**Preconditions:** Both Remote Agents are running.

**Flow:**
1. User types a query like "what is Bob Johnson's schedule?" or "schedule for ID 2" into the Client Agent CLI.
2. Client Agent analyzes the query, determines it's HR-related (schedule), and routes it to the HR Agent.
3. Client Agent parses the query, extracts the employee identifier, and creates an A2A Task request for schedule.
4. Client Agent sends the request to the HR Agent, including the API key.
5. HR Agent receives the request, validates the API key, and uses its schedule skill to find the employee's schedule.
6. HR Agent constructs an A2A Task response with the schedule details or a "not found" message.
7. HR Agent sends the response back to the Client Agent.
8. Client Agent parses the response and displays the schedule information or the "not found" message to the user.

## 7. Future Enhancements (Out of Scope for Initial Release)
- Integration with a persistent database (e.g., SQLite, PostgreSQL) for employee and HR data.
- More sophisticated natural language processing for query parsing and routing (e.g., using an LLM to decide which agent/skill to call).
- Support for additional query parameters or complex filtering.
- Deployment to a cloud platform.
- Robust error logging and monitoring.
- Implementation of streaming or push notifications for long-running tasks.
- Adding more specialized agents (e.g., IT Support Agent, Legal Agent). 