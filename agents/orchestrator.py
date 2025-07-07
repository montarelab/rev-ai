import asyncio
import uuid
from queue import Queue

from agents.agents import create_code_review_agent, summarize_review_result
from views.views import CodeReviewResponse, CodeReviewRequest


class CodeReviewOrchestrator:
    """Main orchestrator for code review workflow"""

    DEFAULT_ESTIMATED_COMPLETION_TIME = 300 # 5 minutes

    def __init__(self):
        self.raw_messages = Queue()
        self.structured_messages = Queue()

    async def _start_analyzing(self, agent, content, task_id):
        messages = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": content,
                    }
                ],

                "config": {
                    "configurable": {  # config for memory
                        "task_id": task_id
                    }
                }

            }
        )

        structured_response = messages['structured_response']

        self.raw_messages.put(messages)
        self.structured_messages.put(structured_response)


    async def review_code(self, request: CodeReviewRequest) -> str:
        """Start a new code review"""

        task_id = uuid.uuid4()

        async with (
            asyncio.TaskGroup() as tg
        ):

            print("Created task group.")

            for changed_file in request.changed_files:

                code_review_agent = await create_code_review_agent()

                content = "Analyze this file. Changes: " + changed_file.changes + " File content: " + changed_file.content

                tg.create_task(self._start_analyzing(
                    agent=code_review_agent,
                    content=content,
                    task_id=task_id
                ))

                print(f"Task for file {changed_file.file_path} started")

        print('Agents finished the tasks!')

        return await summarize_review_result(self.structured_messages)
        # try:
        #     prompt = f"Analyze this code diff and provide feedback on potential issues, improvements, and recommendations.: {request.git_diffs}"
        #     workflow = create_code_review_workflow({"git_diffs": request.git_diffs})
        #
        #     async for chunk in workflow.astream(
        #             {
        #                 "messages": [
        #                     {
        #                         "role": "user",
        #                         "content": prompt,
        #                     }
        #                 ]
        #             },
        #     ):
        #         pass
        #
        #         pretty_print_messages(chunk, last_message=True)
        #
        #     final_message_history = chunk["supervisor"]["messages"]
        #     for message in final_message_history:
        #         message.pretty_print()
        #
        #
        #     print("Chunk: ", chunk)
        #     return CodeReviewResponse(
        #         status=AgentStatus.COMPLETED,
        #         message="Code review started successfully",
        #         estimated_completion_time=self.DEFAULT_ESTIMATED_COMPLETION_TIME,
        #         output=chunk["supervisor"]["structured_response"]
        #     )
        #
        # except Exception as e:
        #     log.error(f"Failed to start review: {e}")
        #     return CodeReviewResponse(
        #         status=AgentStatus.FAILED,
        #         message=f"Failed to start review: {str(e)}"
        #     )

