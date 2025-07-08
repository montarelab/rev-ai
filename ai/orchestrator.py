import asyncio
from datetime import datetime
from queue import Queue

from langgraph.store.memory import InMemoryStore
from loguru import logger as log

from ai.agents import create_code_review_agent, summarize_review_result, create_llm
from ai.mcp import create_mcp_client
from ai.tools.retriever import get_retriever_tool
from config import Config
from views.views import CodeReviewRequest


class CodeReviewOrchestrator:
    """Main orchestrator for code review workflow"""

    def __init__(self, config: Config):
        self.raw_messages = Queue()
        self.structured_messages = Queue()
        self.config = config
        self.task_id = config.task_id
        self.thread_id = config.thread_id
        self.default_config = {
            "configurable": {
                "thread_id": self.thread_id,
            }
        }

        self.store = InMemoryStore()
        log.info("Created memory store.")

        self.mcp_client = create_mcp_client()
        log.info("MCP client created.")

        self.retriever_tool  = get_retriever_tool(self.config)
        log.info("Init vector db with tools.")


    async def _start_analyzing(self, agent, file_name, request_content):
        config = {
            **self.default_config,
            "task_id": self.task_id,
            "project_path": self.config.project_path
        }

        start_time = datetime.now()
        messages = await agent.ainvoke(
            input={
                "messages": {
                    "role": "user",
                    "content": request_content,
                }
            },
            config=config
        )

        structured_response = messages['structured_response']

        self.raw_messages.put(messages)
        self.structured_messages.put(structured_response)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        log.info(f"File {file_name} was analyzed for {duration}s")

    async def review_code(self, request: CodeReviewRequest) -> str:
        """Start a new code review"""

        async with (
            asyncio.TaskGroup() as tg
        ):
            log.info("Created task group.")

            for changed_file in request.changed_files:
                code_review_agent = await create_code_review_agent(
                    store=self.store,
                    mcp_client=self.mcp_client,
                    config=self.config,
                    retriever_tool=self.retriever_tool
                )

                content = "Analyze this file. Changes: " + changed_file.changes + " File content: " + changed_file.content

                tg.create_task(self._start_analyzing(
                    agent=code_review_agent,
                    file_name=changed_file.file_path,
                    request_content=content
                ))

                log.info(f"Task for file {changed_file.file_path} started")

        log.info('Agents finished the tasks!')

        return await summarize_review_result(
            llm=create_llm(self.config),
            structured_messages_queue=self.structured_messages,
            config=self.default_config)
