# main.py
from db_plugins.sqlite_adapter import SQLiteAdapter
from modular_db_agent import ModularDBAgent, DBState
from azure_openai_llm import get_llm
from langchain_core.messages import HumanMessage
from IPython.display import display, Image

sqlite_adapter = SQLiteAdapter("sqlite:///northwind.db")
llm = get_llm()

agent = ModularDBAgent(adapter=sqlite_adapter, llm=llm)
graph = agent.compile_graph()

initial_state = DBState(messages=[
    HumanMessage(content="Get all customers from France and their orders.")
])

display(Image(graph.get_graph().draw_mermaid_png()))

# result = graph.invoke(initial_state, config={"configurable": {"thread_id": "thread_1"}})
# print("Final Result:", result["result"])
