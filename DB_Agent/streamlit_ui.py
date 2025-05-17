# streamlit_db_agent.py

import streamlit as st
import asyncio
from DB_Agent import graph  # Your compiled ModularDBAgent.graph
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Database Assistant")

# 💬 Custom chat styling
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

st.title("📊 Database Assistant")

# 🌱 Session state for chat history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

chat_container = st.container()

# 🖼️ Render previous conversation
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

# 📤 Streaming function for DBAgent
async def run_db_agent_stream(user_message: str):
    from langchain_core.messages import AIMessageChunk

    config = {"configurable": {"thread_id": "db_agent_thread"}}
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "result": [],
        "error": "",
        "retries": 0,
        "intent": user_message,
    }

    bot_response = ""
    response_placeholder = st.empty()
    bot_response = ""
    async for event in graph.astream_events(initial_state, config=config, version="v2", stream_mode="updates"):
        if event["event"] == "on_chain_stream" and event["metadata"].get("langgraph_node") == "validate_and_generate_result":
            chunk_data = event["data"].get("chunk", {})
            if chunk_data.get("event") == "on_custom_stream":
                token = chunk_data["data"]["chunk"].content
                bot_response += token
                print('-------------------on_chain_stream-----------------------',token)
                response_placeholder.markdown(
                f'<div class="bot-message-container"><div class="bot-message">{bot_response}</div></div>',
                unsafe_allow_html=True,
            )

        elif event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node") == "validate_and_generate_result":
            data = event["data"]
            token = data["chunk"].content if hasattr(data["chunk"], "content") else str(data["chunk"])
            bot_response += token
            print('-----------------------on_chat_model_stream-------------------------',token)
            response_placeholder.markdown(
                f'<div class="bot-message-container"><div class="bot-message">{bot_response}</div></div>',
                unsafe_allow_html=True,
            )

    return bot_response

# 🧠 Main chat handler
def chat_with_db_agent():
    user_input = st.chat_input("Ask a database question, like 'How many customers are there?'")
    if user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        with chat_container:
            st.markdown(
                f'<div class="user-message-container"><div class="user-message">{user_input}</div></div>',
                unsafe_allow_html=True,
            )

        response = asyncio.run(run_db_agent_stream(user_input))

        st.session_state.conversation_history.append({"role": "assistant", "content": response})

# 🚀 Launch it
chat_with_db_agent()
