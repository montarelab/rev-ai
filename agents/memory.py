from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.config import get_store
from typing_extensions import TypedDict


class ReviewedFile(TypedDict):
    name: str


@tool(parse_docstring=True)
def mark_file_reviewed(reviewed_file: ReviewedFile, config: RunnableConfig) -> None:
    """
    Mark a file as reviewed to prevent duplicate processing.
    Should be called only after both line-by-line and cross-file analyses
    are fully completed.

    Args:
        reviewed_file: The file metadata to mark reviewed.
        config: Agent runtime config (RunnableConfig).
    """

    store = get_store()  # get store

    task_id = config["configurable"].get("task_id")  # get task id from agent

    store.put(
        ("reviewed_files",),  # collection
        task_id,  # key
        reviewed_file  # value
    )  # update files in memory

    return "Successfully marked file as reviewed."


@tool(parse_docstring=True)
def get_reviewed_files(config: RunnableConfig) -> list[str]:
    """
    Retrieve a list of all files already reviewed before you start reviewing the file.
    If the file you are assigned to review is already reviewing, do not review it again!

    Args:
        config: Agent runtime config (RunnableConfig).

    Returns:
        list[str]: Paths of files marked as reviewed.
    """
    store = get_store()  # get store

    task_id = config["configurable"].get("task_id")  # get task id from agent
    memories = store.get(("reviewed_files",), task_id)
    print("Memories:", memories)
    return memories if memories else "No files reviewed yet."
