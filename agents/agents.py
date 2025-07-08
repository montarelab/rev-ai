import json
import os
from asyncio import Queue

from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from agents.mcp import mcp_client
from agents.memory import mark_file_reviewed, get_reviewed_files
from agents.prompts import create_code_review_prompt
from tools.get_file_content import get_file_content
from tools.regex_file_search import regex_file_search
from tools.retriever import retriever_tool
from views.views import CodeReviewOutput


DEBUG = False

store = InMemoryStore()

def create_llm():
    """Create and configure LLM instance"""


    # return ChatVertexAI(
    #     model='gemini-2.0-flash-lite', # todo add automatic fetching from config
    #     temperature=0
    # )

    return ChatOpenAI(
        model='gpt-4.1-mini', # todo add automatic fetching from config
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )


async def create_code_review_agent():

    mcp_tools = await mcp_client.get_tools()

    code_review_agent = create_react_agent(
        create_llm(),
        tools=[
            regex_file_search,
            get_file_content,
            retriever_tool,
            mark_file_reviewed,
            get_reviewed_files
        ] + mcp_tools, # todo: add mcp tools later

        store=store,
        response_format=CodeReviewOutput,
        name='code_reviewer',
        prompt=create_code_review_prompt()
    )

    return code_review_agent



async def summarize_review_result(
    structured_messages_queue: Queue,
    config: RunnableConfig
) -> str:

    local_structured_messages = []

    while not structured_messages_queue.empty():
        message = structured_messages_queue.get()
        local_structured_messages.append(message)

    messages_str = json.dumps(local_structured_messages)

    summarizer = create_llm()

    summary = await summarizer.ainvoke(
        input="Summarize the changes and give the output: " + messages_str,
        config=config
    )

    return summary.content