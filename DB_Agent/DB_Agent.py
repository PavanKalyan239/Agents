# modular_db_agent.py
import logging
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import MessagesState
from sqlalchemy import create_engine, inspect, text
from pydantic import BaseModel
from azure_openai_llm import get_llm # can use Your Own LLM Instance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

class SQLQuery(BaseModel):
    query: list[str]

class DBState(MessagesState):
    intent: str | None = None
    query: list[str] | None = None
    result: list[dict] | str | None = None
    retries: int = 0
    error: str | None = None


class SQLiteAdapter:
    def __init__(self, db):
        self.db = db

    def get_schema_metadata(self):
        try:
            engine = create_engine(self.db)
            inspector = inspect(engine)
            schema_info = {}
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                schema_info[table_name] = {
                    "columns": [
                        {"name": col["name"], "type": str(col["type"]), "nullable": col["nullable"]}
                        for col in columns
                    ],
                    "foreign_keys": foreign_keys,
                    "primary_key": inspector.get_pk_constraint(table_name)["constrained_columns"]
                }
            logger.info("Schema metadata retrieved successfully.")
            return schema_info
        except Exception as e:
            logger.error(f"Failed to retrieve schema metadata: {e}")
            raise

    def execute_query(self, query: str):
        if not query:
            logger.warning("No query found to execute.")
            return {"result": "No query found to execute."}

        try:
            engine = create_engine(self.db)
            with engine.connect() as connection:
                result_proxy = connection.execute(text(query))
                rows = result_proxy.fetchall()
                column_names = result_proxy.keys()

                # Format results as a list of dictionaries
                results = [dict(zip(column_names, row)) for row in rows]
                logger.info("Query executed successfully.")
                return {"result": results}
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

class ModularDBAgent:
    def __init__(self, db, llm):
        self.db = db
        self.llm = llm
        self.memory = MemorySaver()
        try:
            self.metadata = self.db.get_schema_metadata()
        except Exception as e:
            logger.error(f"Failed to initialize metadata: {e}")
            raise

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
        try:
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
            state["intent"] = [response.content.strip()]
            logger.info("User intent extracted successfully.")
            return state
        except Exception as e:
            logger.error(f"Failed to extract user intent: {e}")
            raise

    def generate_sql_query(self, state: DBState):
        try:
            schema_str = self.format_schema()
            user_query = state["intent"] if state["intent"] else ""
            previous_error = state.get("error", None)
            if user_query == "No query found.":
                state["result"] = ["No actionable query."]
                logger.warning("No actionable query found.")
                return state

            prompt = f"""
You are a SQL expert. Given the following database schema:

{schema_str}
The user has asked the following question or made the following request:

{f"The previous query attempt failed with the following error:\n{previous_error}\nPlease correct it." if previous_error else ""}

"{user_query}"
Analyze the user's intent and, if necessary, break it down into multiple steps.
Write one or more SQL queries (as a list) to fulfill the user's request, ensuring that the queries align with the schema and handle any dependencies between tables.
            """
            structured_sql = self.llm.with_structured_output(SQLQuery)
            result = structured_sql.invoke(prompt)
            state["query"] = result.query
            state.pop("error", None)
            logger.info("SQL query generated successfully.")
            return state
        except Exception as e:
            logger.error(f"Failed to generate SQL query: {e}")
            raise

    def execute_sql_query(self, state: DBState):
        results = []
        state["error"] = None  # Reset previous error
        try:
            for query in state["query"]:
                res = self.db.execute_query(query)
                results.append(res)
            state["result"] = results
            logger.info("SQL query executed successfully.")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            state["result"] = None
            state["error"] = error_msg  # Set the error explicitly
            logger.error(f"SQL query execution failed: {error_msg}")
        return state

    async def validate_and_generate_result(self, state: DBState):
        try:
            state.setdefault("retries", 0)
            if state["error"]:
                if state["retries"] < 2:
                    state["retries"] += 1
                    error_msg = f"Retry {state['retries'] + 1}/3 due to error: {state['error']}"
                    logger.warning(error_msg)
                else:
                    final_msg = f"Query failed after 3 attempts. Last error: {state['error']}"
                    state["messages"].append(AIMessage(content=final_msg))
                    state["error"] = None
                    logger.error(final_msg)
                    yield {"event": "on_custom_stream", "data": {"chunk": AIMessage(content=final_msg)}}
            else:
                result = state.get("result", [])
                if not result:
                    response_msg = "The query ran successfully but returned no data."
                    state["messages"].append(AIMessage(content=response_msg))
                    logger.info(response_msg)
                    yield {"event": "on_custom_stream", "data": {"chunk": AIMessage(content=response_msg)}}
                else:
                    user_query = state["messages"][-1].content
                    prompt = f"""
You are a helpful assistant. The user asked:"{user_query}"

Generate a natural-language summary of the result : "{result} in the proper structured format".
"""
                    response = self.llm.invoke(prompt)
                    state["messages"].append(AIMessage(content=response.content.strip()))
                    logger.info("Result validated and summarized successfully.")

            yield state

        except Exception as e:
            error_msg = f"Validation failed: {type(e).__name__}: {str(e)}"
            state["messages"].append(AIMessage(content=error_msg))
            logger.error(error_msg)
            yield state

    def route_validation(self, state: DBState) -> str:
        if state["error"]:
            logger.info("Routing back to 'generate_sql' due to error.")
            return "generate_sql"
        else:
            logger.info("Validation successful, routing to END.")
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




db = SQLiteAdapter("sqlite:///northwind.db")

llm = get_llm()

agent = ModularDBAgent(db=db, llm=llm)
graph = agent.compile_graph()

# initial_state = DBState(messages=[
#     HumanMessage(content="How Many employees are there in the database?"),
# ])

# result = graph.invoke(initial_state, config={"configurable": {"thread_id": "thread_1"}})
# print("Final Result:", result["result"])

# print("__________", result["messages"][-1].content, "__________")