import asyncio
from queue import Queue

from loguru import logger as log

from agents.agents import create_code_review_agent, summarize_review_result
from config import Config
from utils.message import pretty_print_message
from views.views import CodeReviewRequest


def print_whole_queue(queue: Queue):
    """Print all items in the queue"""
    while not queue.empty():
        item = queue.get()
        pretty_print_message(item, indent=True)
        print(item)

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

    async def _start_analyzing(self, agent, content):

        config = self.default_config.copy()
        config["task_id"] = self.task_id
        config["app_config"] = self.config
        config["project_path"] = self.config.project_path

        messages = await agent.ainvoke(
            input={
                "messages": {
                    "role": "user",
                    "content": content,
                }
            },
            config=config
        )

        structured_response = messages['structured_response']

        self.raw_messages.put(messages)
        self.structured_messages.put(structured_response)


    async def review_code(self, request: CodeReviewRequest) -> str:
        """Start a new code review"""

        async with (
            asyncio.TaskGroup() as tg
        ):

            log.info("Created task group.")

            for changed_file in request.changed_files:

                code_review_agent = await create_code_review_agent()

                content = "Analyze this file. Changes: " + changed_file.changes + " File content: " + changed_file.content

                tg.create_task(self._start_analyzing(
                    agent=code_review_agent,
                    content=content
                ))

                log.info(f"Task for file {changed_file.file_path} started")

        log.info('Agents finished the tasks!')


        return await summarize_review_result(self.structured_messages, self.default_config)
