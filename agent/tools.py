import pathlib
import subprocess
from typing import Tuple

from langchain_core.tools import tool

PROJECT_ROOT = pathlib.Path.cwd() / "generated"
_CURRENT_PROJECT_PATH = PROJECT_ROOT

def set_project_base_path(project_name: str):
    global _CURRENT_PROJECT_PATH
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    _CURRENT_PROJECT_PATH = PROJECT_ROOT / safe_name
    _CURRENT_PROJECT_PATH.mkdir(parents=True, exist_ok=True)
    return str(_CURRENT_PROJECT_PATH)

def safe_path(path: str) -> pathlib.Path:
    p = (_CURRENT_PROJECT_PATH / path).resolve()
    if not str(p).startswith(str(_CURRENT_PROJECT_PATH)):
        raise ValueError("Path traversal detected")
    return p
    
@tool
def write_file(path:str, content:str)->pathlib.Path:
    """Writes the content to a file"""
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p

@tool
def read_file(path:str)->Tuple[str, str]:
    """Reads the content of a file"""
    p = safe_path(path)
    return p.read_text()

@tool
def get_current_directory()->str:
    """Returns the current working directory"""
    return str(_CURRENT_PROJECT_PATH)

@tool
def run_command(command:str)->Tuple[str, str]:
    """Runs a command in terminal"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=_CURRENT_PROJECT_PATH)
    return result.stdout, result.stderr

@tool
def list_files(path:str)->list[str]:
    """Lists all files in a directory"""
    p = safe_path(path)
    return [str(f) for f in p.rglob("*") if f.is_file()]

tools = [write_file, read_file, get_current_directory, run_command, list_files]