from pydantic import BaseModel, Field, ConfigDict

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

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path of the file")
    task_description: str = Field(description="The task to be performed on the file")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="The list of implementation tasks")
    model_config: ConfigDict = ConfigDict(extra="allow")