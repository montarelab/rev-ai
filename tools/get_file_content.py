from pathlib import Path

from langchain_core.tools import tool


@tool(parse_docstring=True)
def get_file_content(file_path: str):
    """
    Read the full contents of a specified source code file.
    Use this to investigate file-level logic when regex-based search doesn't provide enough context.

    Args:
        file_path (str): Absolute or relative path to the file.

    Returns:
        str: Full contents of the file.
    """
    path_obj = Path(file_path)

    with open(path_obj, "r", encoding="utf-8") as f:
        return f.read()