from fastapi import FastAPI
from langchain.prompts import PromptTemplate
from azure_openai_llm import get_llm

app = FastAPI()
llm = get_llm()

system_prompt = PromptTemplate(
    input_variables=["input"],
    template=(
        "You are an engaging and friendly assistant. Respond to the user's queries with enthusiasm, "
        "clarity, and a conversational tone. Encourage follow-up questions and make the interaction enjoyable. "
        "User: {input}"
    )
)

def get_response(prompt: str):
    try:
        response = llm.invoke(system_prompt.format(input=prompt))
        if response:
            response = response.content
            return response
        return "Unable to get a response. Please try again."
    except Exception as e:
        return str(e)
    
@app.get("/assistant")
async def assistant(input: str):
    """
    Endpoint to get a response from the assistant.
    """
    try:
        print(f"Input: {input}")
        response = get_response(input)
        return response
    except Exception as e:
        return f"Error: {str(e)}"
    
# curl -X GET "http://localhost:8000/assistant?input=Hello