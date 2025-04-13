import streamlit as st
import asyncio
from research_Agent import graph  # Your agent with graph.astream_events
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Research Agent")

# Styling for chat bubbles
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        width: 100%;
    }
    .user-message-container {
        display: flex;
        justify-content: flex-end;
        margin: 5px 0;
    }
    .user-message {
        padding: 10px 14px;
        background-color: #DCF8C6;
        border-radius: 14px;
        max-width: 65%;
        font-size: 15px;
        word-wrap: break-word;
        color: black;
    }
    .bot-message-container {
        display: flex;
        justify-content: flex-start;
        margin: 5px 0;
    }
    .bot-message {
        padding: 10px 14px;
        background-color: #E5E5EA;
        border-radius: 14px;
        max-width: 75%;
        font-size: 15px;
        word-wrap: break-word;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Research Agent:")

# Initialize conversation state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

chat_container = st.container()

# Render conversation history
with chat_container:
    for msg in st.session_state.conversation_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-message-container"><div class="user-message">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f'<div class="bot-message-container"><div class="bot-message">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )

# Streaming function
async def run_agent_stream(user_message: str):
    config = {"configurable": {"thread_id": "streamlit_thread"}}
    initial_state = {
        "messages": [{"role": "user", "content": user_message}],
        "research_needed": False,
        "wikipedia_results": [],
        "tavily_results": [],
        "final_response": ""
    }

    bot_response = ""
    response_placeholder = st.empty()

    async for event in graph.astream_events(initial_state, config):
        if (
            event["event"] == "on_chat_model_stream"
            and event["metadata"].get("langgraph_node") == "generate_response"
        ):
            chunk = event["data"]["chunk"]
            bot_response += chunk.content
            response_placeholder.markdown(
                f'<div class="bot-message-container"><div class="bot-message">{bot_response}</div></div>',
                unsafe_allow_html=True,
            )
    return bot_response

# Main chat handler
def chat_with_researchbot():
    user_input = st.chat_input("Ask about anything, and I'll research it for you!")
    if user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        with chat_container:
            st.markdown(
                f'<div class="user-message-container"><div class="user-message">{user_input}</div></div>',
                unsafe_allow_html=True,
            )

        response = asyncio.run(run_agent_stream(user_input))

        st.session_state.conversation_history.append({"role": "assistant", "content": response})

chat_with_researchbot()
