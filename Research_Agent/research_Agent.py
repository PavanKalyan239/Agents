import os
import asyncio
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from azure_openai_llm import get_llm
from langchain_core.messages import HumanMessage
from tavily import TavilyClient
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv

load_dotenv()


llm = get_llm()

# Initialize OpenAI LLM 
# llm = ChatOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     model="gpt-3.5-turbo",
# )

# Get API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_wikipedia(topic: str, top_k: int = 2):
    """
    Searches Wikipedia using LangChain's wrapper and returns structured results.
    
    Parameters:
        topic (str): The topic to search for.
        top_k (int): Number of top results to return.
    
    Returns:
        List[dict]: Each result contains title, summary (page_content), and URL.
    """
    # Create API wrapper with limited results
    wiki_api = WikipediaAPIWrapper(top_k_results=top_k)
    # wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api)

    # Load raw results as document objects
    docs = wiki_api.load(topic)

    # Structure the results
    structured_results = []
    for doc in docs:
        result = {
            "title": doc.metadata.get("title", "Unknown Title"),
            "summary": doc.page_content,
            "url": f"https://en.wikipedia.org/wiki/{doc.metadata.get('title', '').replace(' ', '_')}"
        }
        structured_results.append(result)

    return structured_results


def search_tavily(query: str, max_results: int = 2):
    """
    Searches the web using Tavily API and returns structured results.

    Parameters:
        query (str): The search query string.
        max_results (int): Maximum number of search results to return.

    Returns:
        List[dict]: Each result contains title, content, and url.
    """
    
    # Handle case where API key is not set
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
    
    # Initialize Tavily client
    client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # Perform the search
    response = client.search(query=query, max_results=max_results)
    
    # Structure the results
    structured_results = []
    for result in response.get("results", []):
        structured_results.append({
            "title": result.get("title", "No Title"),
            "url": result.get("url", ""),
            "content": result.get("content", "")
        })
    
    return structured_results


# Define the state structure
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]     # Tracks conversation history
    research_needed: bool                       # Flag to trigger research - Safely allows multiple nodes to read this key in parallel
    wikipedia_results: List[dict]               # Stores Wikipedia results
    tavily_results: List[dict]                  # Stores Tavily results
    final_response: str                         # Final response to user


# Wikipedia search node
def wikipedia_node(state: AgentState):
    if state["research_needed"]:
        topic = state["messages"][-1].content
        results = search_wikipedia(topic)
        return {"wikipedia_results": results}
    return {"wikipedia_results": []}


def tavily_node(state: AgentState):
    if state["research_needed"]:
        query = state["messages"][-1].content
        results = search_tavily(query)
        return {"tavily_results": results}
    return {"tavily_results": []}


# Node to determine if research is required
def decide_research(state: AgentState) -> AgentState:
    last_message = state["messages"][-1].content
    research_prompt = (
        f"Determine if the following user message requires research: '{last_message}'. "
        "Respond with 'yes' or 'no'."
    )
    response = llm.invoke(research_prompt).content.strip().lower()
    state["research_needed"] = response == "yes"
    return state

def route_research(state: AgentState) -> List[str]:
    if state["research_needed"]:
        return ["wikipedia_node", "tavily_node"]
    else:
        return ["generate_response"]


async def generate_response(state: AgentState):
    # Prepend system prompt if not already in messages
    messages = [{"role": "system", "content": "You are a Research Agent. You can Browse the Internet to find answers to questions using Tavily and wikipedia."}] + state["messages"]

    final_response = ""

    # No research: respond based on full history
    if not state["research_needed"]:
        async for chunk in llm.astream(messages):
            final_response += chunk.content
            yield {
                "final_response": final_response,
                "__event__": {
                    "name": "on_chat_model_stream",
                    "data": {"chunk": chunk},
                }
            }

        yield {
            "messages": state["messages"] + [{"role": "assistant", "content": final_response}],
            "final_response": final_response
        }

    # Research needed: build context and inject into history
    else:
        context = "Research results:\n"
        if state["wikipedia_results"]:
            context += "Wikipedia:\n"
            for result in state["wikipedia_results"]:
                context += f"- {result['title']}: {result['summary']}... ({result['url']})\n"
        if state["tavily_results"]:
            context += "Tavily:\n"
            for result in state["tavily_results"]:
                context += f"- {result['title']}: {result['content']}... ({result['url']})\n"

        user_question = state["messages"][-1].content
        contextual_prompt = f"Based on the following context, respond to the user message '{user_question}':\n{context}\nInclude all URLs for reference."

        extended_messages = messages + [{"role": "user", "content": contextual_prompt}]

        async for chunk in llm.astream(extended_messages):
            final_response += chunk.content
            yield {
                "final_response": final_response,
                "__event__": {
                    "name": "on_chat_model_stream",
                    "data": {"chunk": chunk},
                }
            }

        yield {
            "messages": state["messages"] + [{"role": "assistant", "content": final_response}],
            "final_response": final_response
        }


# Build Graph
workflow = StateGraph(AgentState)

# define nodes
workflow.add_node("decide_research", decide_research)
workflow.add_node("wikipedia_node", wikipedia_node)
workflow.add_node("tavily_node", tavily_node)
workflow.add_node("generate_response", generate_response)

# define edges
workflow.add_edge(START, "decide_research")
workflow.add_conditional_edges(
    "decide_research",
    route_research,
    {
        "wikipedia_node": "wikipedia_node",
        "tavily_node": "tavily_node",
        "generate_response": "generate_response"
    } # “condition mapping” — it tells the graph which nodes are valid destinations for the condition function (route_research) to return.
)
workflow.add_edge("wikipedia_node", "generate_response")
workflow.add_edge("tavily_node", "generate_response")

workflow.add_edge("generate_response", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)


async def run_research_agent_stream(user_message: str, thread_id: str = "default_thread"):
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "research_needed": False,
        "wikipedia_results": [],
        "tavily_results": [],
        "final_response": ""
    }

    async for event in graph.astream_events(initial_state, config):
        if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node") == "generate_response":
            data = event["data"]
            print(data["chunk"].content, end="", flush=True)


# Usage
# if __name__ == "__main__":
#     asyncio.run(run_research_agent_stream("What are the Latest Trends in AI", "thread_1"))


