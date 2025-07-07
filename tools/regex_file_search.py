import subprocess
from typing import Optional

from langchain_core.tools import tool


@tool(parse_docstring=True)
def regex_file_search(query: str, lines_of_code: Optional[int] = None):
    """
    Search the codebase using a regular expression and return matching lines with context.
    This tool uses ripgrep to find symbols like functions, classes, or variables
    that may have been changed and are referenced elsewhere.

    Args:
        query (str): The regex pattern to search for.
        lines_of_code (int): Number of context lines to include before and after each match.

    Returns:
        list[str]: Matching lines with surrounding context.
    """
    pass
    args = [query]

    if lines_of_code:
        args.append(f'-C{lines_of_code}')

    args.append(project_path_str)
    # args.append('--no-filename')

    result = subprocess.run(
        ['rg'] + args,
        capture_output=True,
        encoding='utf-8',
    )

    if result.returncode == 0:
        return result.stdout
    elif result.returncode == 1:
        return "No matches found."
    else:
        return f"Error:\n{result.stderr}"