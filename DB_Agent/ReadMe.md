# Modular DB Agent

## Overview
The Modular DB Agent is a Python-based application designed to facilitate interaction with SQLite databases through natural language queries. It leverages a language model (LLM) to interpret user requests, generate SQL queries, execute them, and provide meaningful responses. The agent is built using a modular architecture with LangGraph, ensuring flexibility, scalability, and robust error handling.

## Features

- **Natural Language Processing**: Converts user queries into SQL queries by understanding intent using a language model.
- **Schema Awareness**: Automatically retrieves and uses database schema metadata to generate accurate SQL queries.
- **Query Execution**: Executes SQL queries on an SQLite database and returns formatted results.
- **Error Handling and Retry Logic**: Includes retry mechanisms for failed queries and detailed error logging.
- **State Management**: Maintains conversation state and query history using LangGraph's MemorySaver.
- **Modular Design**: Separates concerns into distinct components (intent extraction, query generation, execution, and result validation) for easy maintenance and extensibility.
- **Structured Output**: Uses Pydantic models to ensure consistent SQL query formatting.
- **Logging**: Comprehensive logging for debugging and monitoring.

## What We Have Implemented

- **SQLite Adapter**: A class to interact with SQLite databases, including schema retrieval and query execution.
- **Modular DB Agent**: The core agent that orchestrates the workflow, including:
  - **Intent Extraction**: Analyzes user input to determine the database-related intent.
  - **SQL Query Generation**: Generates one or more SQL queries based on the schema and user intent.
  - **Query Execution**: Executes queries and handles results or errors.
  - **Result Validation**: Validates query results, summarizes them in natural language, and retries on errors (up to 3 attempts).
- **Graph-Based Workflow**: A LangGraph-based state machine that manages the flow between intent extraction, query generation, execution, and validation.
- **State Persistence**: Uses MemorySaver to persist conversation state across interactions.
- **Error Handling**: Robust error handling with logging and user-friendly error messages.
- **Integration with LLM**: Uses an Azure OpenAI LLM (via `get_llm`) for natural language understanding and query generation.

## Requirements

To run the Modular DB Agent, ensure you have the following dependencies installed:

- `python>=3.8`
- `langchain-core>=0.2.0`
- `langgraph>=0.1.0`
- `sqlalchemy>=2.0.0`
- `pydantic>=2.0.0`
- `azure-openai>=0.1.0` (or your preferred LLM provider SDK)

Additionally, you need:

- An SQLite database file (e.g., `northwind.db`).
- Access to an LLM service (e.g., Azure OpenAI) with appropriate credentials configured.
- The `get_llm` function implemented in `azure_openai_llm.py` to initialize the LLM.

Install the dependencies using pip:

```bash
pip install langchain-core langgraph sqlalchemy pydantic azure-openai
```

## Usage

1. **Set up the Database**: Ensure your SQLite database (e.g., `northwind.db`) is accessible.
2. **Configure the LLM**: Implement the `get_llm` function in `azure_openai_llm.py` to return an initialized LLM client.
3. **Run the Agent**:

```python
from modular_db_agent import ModularDBAgent, SQLiteAdapter

db = SQLiteAdapter("sqlite:///northwind.db")
llm = get_llm()
agent = ModularDBAgent(db=db, llm=llm)
graph = agent.compile_graph()

initial_state = DBState(messages=[
    HumanMessage(content="How many employees are there in the database?"),
])
result = graph.invoke(initial_state, config={"configurable": {"thread_id": "thread_1"}})
print(result["messages"][-1].content)
```

4. **Interact**: Provide natural language queries, and the agent will process them, execute SQL queries, and return results.

## Running the Streamlit Interactive UI

To launch the Streamlit-based interactive UI for the Modular DB Agent, follow these steps:

1. **Install Streamlit**:
   Ensure you have Streamlit installed. If not, install it using pip:

   ```bash
   pip install streamlit
   ```

2. **Navigate to the Project Directory**:
   Open a terminal and navigate to the directory containing the `streamlit_ui.py` file.

3. **Run the Streamlit Application**:
   Execute the following command to start the Streamlit server:

   ```bash
   streamlit run streamlit_ui.py
   ```

4. **Access the UI**:
   Open a web browser and go to the URL displayed in the terminal (usually `http://localhost:8501`).

5. **Interact with the Database Assistant**:
   Use the chat interface to ask database-related questions, such as "How many customers are there?". The assistant will process your query and provide results interactively.

---

**Inspired by**: The need for intuitive database interaction through natural language.

