from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from prompts import planner_prompt, architect_prompt, coder_system_prompt, reviewer_prompt
from states import Plan, TaskPlan, ReviewResult
from langgraph.graph import StateGraph, END
from tools import tools, read_file, write_file, list_files, get_current_directory, run_command, set_project_base_path
load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2)

user_prompt = "create a simple calculator web app"

state = {
    "user_prompt": user_prompt,
    "task_plan": None,
    "review_result": None,
    "plan": None 
}

def planner_agent(state: dict)->dict:
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    state["plan"] = resp
    
    project_path = set_project_base_path(resp.name)
    print(f"Project path set to: {project_path}")
    
    return state

def architect_agent(state: dict)-> dict:
    plan_data = state["plan"].model_dump_json()
    architect_prompt_with_plan = architect_prompt(plan_data)
    resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt_with_plan)
    if resp is None:
        raise ValueError("Architecture did not return a valid response")
    
    state["task_plan"] = resp
    return state

# planner_resp = planner_agent(state)
# print(planner_resp)
# print(20*"-")
# print("\n")

# architect_resp = architect_agent(planner_resp)
# print(architect_resp)
# print(20*"-")
# print("\n")

def coder_agent(state: dict) -> dict:
    task_plan = state["task_plan"]
    
    coder_tools = [read_file, write_file, list_files, get_current_directory, run_command]
    tool_map = {t.name: t for t in coder_tools}
    llm_with_tools = llm.bind_tools(coder_tools)
    
    for task in task_plan.implementation_steps:
        print(f"Executing task for: {task.filepath}")
        
        messages = [
            SystemMessage(content=coder_system_prompt()),
            HumanMessage(content=f"Current Task: {task.task_description}\nFile: {task.filepath}\n\nExecute the necessary tools to complete this task.")
        ]
        
        for _ in range(5):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                break

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                if tool_name in tool_map:
                    print(f"Calling tool: {tool_name} with args: {tool_args}")
                    try:
                        tool_func = tool_map[tool_name]
                        tool_result = tool_func.invoke(tool_args)
                    except Exception as e:
                        tool_result = f"Error executing tool: {e}"
                        
                    messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_result)))
                else:
                    messages.append(ToolMessage(tool_call_id=tool_call["id"], content="Tool not found"))
                    
    return state

def should_continue(state:dict)->str:
    review = state.get("review_result")
    
    if review and review.is_working:
        return "end"
    return "continue"


def reviewer_agent(state: dict)->dict:
    plan = state["plan"].model_dump_json()
    task_plan = state["task_plan"].model_dump_json()
    
    resp = llm.with_structured_output(ReviewResult).invoke(reviewer_prompt(plan, task_plan))
    state["review_result"] = resp
    return state


graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)
graph.add_node("reviewer", reviewer_agent)

graph.set_entry_point("planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_edge("coder", "reviewer")

graph.add_conditional_edges("reviewer", should_continue, {
    "continue": "coder",
    "end": END
})

agent = graph.compile()

if __name__ == "__main__":
    user_prompt = "Create a simple calculator web app with good ui"
    result = agent.invoke({"user_prompt": user_prompt})
    print(result)