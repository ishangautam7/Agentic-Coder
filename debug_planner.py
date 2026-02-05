
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict
import os

load_dotenv()

# Copy from states.py
class File(BaseModel):
    name: str = Field(description="The name of the file")
    content: str = Field(description="The content of the file")
    path: str = Field(description="The path of the file")
    purpose: str = Field(description="The purpose of the file")

class Plan(BaseModel):
    name: str = Field(description="The name of app to be built")
    description: str = Field(description="A oneline description of app to be built. E.g: A web application for managing students attendance.")
    techstack: str = Field(description="The techstack to be used to build the app. E.g: Django, React, Node.js, etc.")
    features: list[str] = Field(description = f"""The list of features that will be provided in the given app. E.g: ["User authentication", "CRUD operations", "Data visualization"]""")
    files: list[File] = Field(description = """The list of files that will be provided in the given app. E.g: ["index.html", "style.css", "script.js"]""")

# Setup LLM
try:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2)
    
    # Prompt
    user_prompt = "Create a simple calculator web app"
    PLANNER_PROMPT = f"""
    You are a PLANNER agent. Convert the user prompt into complete engineering prompt with proper plan.
    Return ONLY the structured JSON data according to the TaskPlan schema. 
    Do not include any conversational text, headers, or markdown formatting outside the tool call.

    User request: {user_prompt}
    """
    
    print("Invoking LLM...")
    resp = llm.with_structured_output(Plan).invoke(PLANNER_PROMPT)
    print("Success!")
    print(resp)

except Exception as e:
    print("Caught Exception:")
    print(e)
    import traceback
    traceback.print_exc()
