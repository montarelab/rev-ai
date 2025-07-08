from pathlib import Path

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


@tool(parse_docstring=True)
def get_file_content(file_path: str, config: RunnableConfig):
    """
    Read the full contents of a specified source code file.
    Use this to investigate file-level logic when regex-based search doesn't provide enough context.

    Args:
        file_path (str): Absolute or relative path to the file.
        config: Agent runtime config (RunnableConfig).

    Returns:
        str: Full contents of the file.
    """
    path_obj = Path(file_path)
    if path_obj.is_absolute():
        full_file_path = path_obj
    else:
        try:
            configurable = config["configurable"]
            project_path = configurable.get("project_path")
            full_file_path = project_path / path_obj
        except BaseException as e:
            raise ValueError("Project path not found in configuration. Ensure 'project_path' is set in the agent's config.") from e

    return read_file(full_file_path)


def get_file_content_with_project_oath(file_path: str, project_path: str):
    path_obj = Path(project_path) / file_path
    return read_file(path_obj)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()