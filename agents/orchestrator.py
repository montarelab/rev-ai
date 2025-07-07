from loguru import logger as log

from agents.workflow import create_code_review_workflow
from utils.message import pretty_print_messages
from views.views import AgentStatus, CodeReviewResponse, CodeReviewRequest


class CodeReviewOrchestrator:
    """Main orchestrator for code review workflow"""

    DEFAULT_ESTIMATED_COMPLETION_TIME = 300 # 5 minutes


    async def start_review(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Start a new code review"""

        try:
            prompt = f"Analyze this code diff and provide feedback on potential issues, improvements, and recommendations.: {request.git_diffs}"
            workflow = create_code_review_workflow({"git_diffs": request.git_diffs})

            async for chunk in workflow.astream(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ]
                    },
            ):
                pass

                pretty_print_messages(chunk, last_message=True)

            final_message_history = chunk["supervisor"]["messages"]
            for message in final_message_history:
                message.pretty_print()


            print("Chunk: ", chunk)
            return CodeReviewResponse(
                status=AgentStatus.COMPLETED,
                message="Code review started successfully",
                estimated_completion_time=self.DEFAULT_ESTIMATED_COMPLETION_TIME,
                output=chunk["supervisor"]["structured_response"]
            )

        except Exception as e:
            log.error(f"Failed to start review: {e}")
            return CodeReviewResponse(
                status=AgentStatus.FAILED,
                message=f"Failed to start review: {str(e)}"
            )

