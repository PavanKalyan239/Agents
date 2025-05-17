# modular_db_agent.py
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from pydantic import BaseModel
from typing import List
from db_plugins.base_adapter import BaseDBAdapter

class SQLQuery(BaseModel):
    query: list[str]

class DBState(MessagesState):
    intent: str | None = None
    query: list[str] | None = None
    result: list[dict] | str | None = None
    retries: int = 0
    error: str | None = None


class ModularDBAgent:
    def __init__(self, adapter: BaseDBAdapter, llm):
        self.adapter = adapter
        self.llm = llm
        self.memory = MemorySaver()
        self.metadata = self.adapter.get_schema_metadata()

    def format_schema(self) -> str:
        """
        Converts parsed schema dict into a readable schema format for the LLM.
        """
        formatted = []
        for table_name, table_data in self.metadata.items():
            columns = ", ".join(
                f"{col['name']} ({col['type']})"
                for col in table_data.get("columns", [])
            )
            formatted.append(f"Table: {table_name}\n  Columns: {columns}")
        return "\n\n".join(formatted)

    def extract_user_intent(self, state: DBState):
        prior, latest = state["messages"][:-1], state["messages"][-1]
        convo = "\n".join(f"User: {m.content}" for m in prior)
        prompt = f"""
You are an assistant helping to interact with a database. Here is the conversation so far:

{convo}
The user has now said:

{latest.content}
Based on the conversation, understand the user's intent and generate a clear and detailed prompt that can be used to create SQL queries. 
Ensure the prompt provides enough context and clarity for generating accurate SQL queries aligned with the user's intent.
If the intent is unclear or not related to the database, return "No prompt generated."
        """
        response = self.llm.invoke(prompt)
        state["messages"].append(AIMessage(content=response.content.strip()))
        state["intent"] = [response.content.strip()]
        return state

    def generate_sql_query(self, state: DBState):
        schema_str = self.format_schema()
        user_query = state["intent"] if state["intent"] else ""

        if user_query == "No query found.":
            state["result"] = ["No actionable query."]
            return state

        prompt = f"""
You are a SQL expert. Given the following database schema:

{schema_str}
The user has asked the following question or made the following request:

"{user_query}"
Analyze the user's intent and, if necessary, break it down into multiple steps.
Write one or more SQL queries (as a list) to fulfill the user's request, ensuring that the queries align with the schema and handle any dependencies between tables.
        """
        structured_sql = self.llm.with_structured_output(SQLQuery)
        result = structured_sql.invoke(prompt)
        state["query"] = result.query
        state["messages"].append(AIMessage(content="\n".join(result.query)))
        return state

    def execute_sql_query(self, state: DBState):
        results = []
        state["error"] = None  # Reset previous error
        try:
            for query in state["query"]:
                res = self.adapter.execute_query(query)
                results.append(res)
            state["result"] = results
            state["messages"].append(AIMessage(content=str(results)))
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            state["result"] = None
            state["error"] = error_msg  # Set the error explicitly
            state["messages"].append(AIMessage(content=f"Query failed with error: {error_msg}"))
        return state

    def validate_and_generate_result(self, state: DBState):
        try:
            if state["error"]:
                if state["retries"] < 2:
                    state["retries"] += 1
                    error_msg = f"Retry {state['retries'] + 1}/3 due to error: {state['error']}"
                    state["messages"].append(AIMessage(content=error_msg))
                else:
                    final_msg = f"Query failed after 3 attempts. Last error: {state['error']}"
                    state["messages"].append(AIMessage(content=final_msg))
            else:
                result = state.get("result", [])
                if not result:
                    response_msg = "The query ran successfully but returned no data."
                    state["messages"].append(AIMessage(content=response_msg))
                else:
                    # Use LLM to explain the result clearly
                    user_query = state.get("intent", "")
                    prompt = f"""
You are a helpful assistant. The user asked:

"{user_query}"
The query was executed and returned the following data:

{result}
Please provide a natural-language summary of what the results mean.
"""
                response = self.llm.invoke(prompt)
                state["messages"].append(AIMessage(content=response.content.strip()))

            return state

        except Exception as e:
            error_msg = f"Validation failed: {type(e).__name__}: {str(e)}"
            state["messages"].append(AIMessage(content=error_msg))
            return state

    def route_validation(self, state: DBState) -> str:
        if state["error"]:
            return "generate_sql"
        else:
            return END

    def compile_graph(self):
        graph = StateGraph(DBState)
        graph.add_node("extract_user_intent", self.extract_user_intent)
        graph.add_node("generate_sql", self.generate_sql_query)
        graph.add_node("execute_sql", self.execute_sql_query)
        graph.add_node("validate_and_generate_result", self.validate_and_generate_result)

        graph.set_entry_point("extract_user_intent")
        graph.add_edge("extract_user_intent", "generate_sql")
        graph.add_edge("generate_sql", "execute_sql")
        graph.add_edge("execute_sql", "validate_and_generate_result")
        graph.add_conditional_edges(
            "validate_and_generate_result",
            self.route_validation,
            {
                "generate_sql": "generate_sql",
                END: END
            }  # “condition mapping” — it tells the graph which nodes are valid destinations for the condition function (validate_result) to return.
        )


        return graph.compile(checkpointer=self.memory)
