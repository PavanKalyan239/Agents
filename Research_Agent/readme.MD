# 🧠 Research Agent – Real-Time Web Research with LangGraph + Streamlit

A beginner-friendly AI Research Assistant that can **autonomously decide** if a user’s question needs research, run **parallel web searches**, and generate **streamed, real-time answers** with conversation memory.

This project is designed to help developers **understand how AI agents actually work** — no black-box abstractions, just clean and clear logic using [LangGraph](https://www.langgraph.dev/) and [Streamlit](https://streamlit.io).

---

## 🚀 Features

✅ **LangGraph-based Agent**  
Transparent graph-based design with custom nodes for decision-making, tools, and response generation.

✅ **Research Decision Logic**  
Agent decides when a user’s question requires web research (vs just using its own knowledge).

✅ **Parallel Web Tools**  
Runs both **Wikipedia** and **Tavily** web searches in parallel.

✅ **Streaming Responses**  
Uses OpenAI (or Azure OpenAI) to generate responses **token-by-token** — visible in real-time.

✅ **Conversation Memory**  
Keeps track of user and AI messages to provide contextual answers.

✅ **Clean Streamlit UI**  
Interactive chat interface styled like a messaging app, powered by Streamlit.

---

## 🖼️ UI Preview

> ![screenshot](assets/research_agent_demo.png)  
> *A lightweight AI chatbot that streams web-researched answers in real time.*

---

## 🛠️ Tech Stack

| Layer          | Tool                |
|----------------|---------------------|
| 🧠 LLM          | OpenAI / Azure OpenAI |
| 🔀 Workflow     | LangGraph            |
| 🔎 Search APIs  | Wikipedia + Tavily   |
| 🧱 UI Framework | Streamlit            |
| 📦 Python Env   | Python 3.10+, LangChain ecosystem |

---

## 📌 How It Works

1. **User sends a question**
2. The agent decides: *"Do I need to research this?"*
3. If yes, it runs:
   - `wikipedia_search` and `tavily_search` nodes in parallel
4. All context is passed to the `generate_response` node
5. The LLM begins streaming a final response in real-time to the frontend
6. Memory is updated with the full conversation

---

## 🎓 Designed for Learning

This project was built for developers who want to:
- Understand **LangGraph's power and simplicity**
- Learn how to **manually control agent logic**
- Build real-time, **memory-aware AI apps**
- Extend with custom tools or APIs (YouTube, Arxiv, Scholar, etc.)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/research-agent
cd research-agent

# Create and activate a virtual env
python -m venv env
source env/bin/activate  # or .\env\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Set your API keys (OpenAI, Tavily)
export OPENAI_API_KEY=your_key # Set Your Own API
export TAVILY_API_KEY=your_key

# Run the app
streamlit run app.py
