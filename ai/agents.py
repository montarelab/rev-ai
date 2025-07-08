import json
from asyncio import Queue

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import Tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from ai.prompts import create_code_review_prompt
from ai.tools.get_file_content import get_file_content
from ai.tools.memory import mark_file_reviewed, get_reviewed_files
from ai.tools.regex_file_search import regex_file_search
from config import Config
from views.views import CodeReviewOutput


def create_llm(config: Config):
    """Create and configure LLM instance"""
    return ChatOpenAI(
        model=config.model_name,
        openai_api_key=config.api_key,
        temperature=0
    )


async def create_code_review_agent(
        store: InMemoryStore,
        mcp_client: MultiServerMCPClient,
        config: Config,
        retriever_tool=Tool
):
    mcp_tools = await mcp_client.get_tools()

    code_review_agent = create_react_agent(
        create_llm(config),
        tools=[
              regex_file_search,
              get_file_content,
              retriever_tool,
              mark_file_reviewed,
              get_reviewed_files
        ] + mcp_tools,
        store=store,
        response_format=CodeReviewOutput,
        name='code_reviewer',
        prompt=create_code_review_prompt()
    )

    return code_review_agent


async def summarize_review_result(
        llm,
        structured_messages_queue: Queue,
        config: RunnableConfig
) -> str:
    local_structured_messages = []

    while not structured_messages_queue.empty():
        message = structured_messages_queue.get()
        local_structured_messages.append(message)

    messages_str = json.dumps(local_structured_messages)

    summary = await llm.ainvoke(
        input="Summarize the changes and give the output: " + messages_str,
        config=config
    )

    return summary.content
