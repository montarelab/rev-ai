import subprocess
from typing import Optional

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from psutil import Error


@tool()
def regex_file_search(query: str, lines_of_code: int, config: RunnableConfig):
    """
    Search the codebase using a regular expression and return matching lines with context.
    This tool uses ripgrep to find symbols like functions, classes, or variables
    that may have been changed and are referenced elsewhere.
    """
    pass
    args = [query]

    if lines_of_code:
        args.append(f'-C{lines_of_code}')

    try:
        configurable = config["configurable"]
        print("configurable:", configurable)
        project_path = configurable.get("project_path")  # get task id from agent
    except BaseException as e:
        print("Config issue:")
        print(config)
        # print("Keys at config:", config.keys())
        # print("Keys at configurable:", config["configurable"].keys())
        # print("Full config: ", config)


    args.append(project_path)

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