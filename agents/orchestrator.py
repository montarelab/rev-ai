from datetime import datetime
from loguru import logger as log
from agents.workflow import create_code_review_workflow
from views.views import AgentStatus, CodeReviewResponse, CodeReviewRequest, CodeReviewState


def log_event(event: dict):
    """Log workflow event details"""
    if not event:
        log.info("Empty event detected")
        return
        
    # Get the first key's value from the event dict
    first_key = next(iter(event), None)
    if not first_key:
        log.info("Event detected but no keys found")
        return
        
    state = event[first_key]
    log.info(f"Event detected from {first_key}")

    if isinstance(state, dict):
        if 'task_id' in state:
            log.info(f"Task ID: {state['task_id']}")
        if 'status' in state:
            log.info(f"Status: {state['status']}")
        if 'agent_feedback' in state:
            feedback = state['agent_feedback']
            log.info(f"Agent feedback: {feedback}")
        if 'next_agent' in state:
            log.info(f"Next agent: {state['next_agent']}")


class CodeReviewOrchestrator:
    """Main orchestrator for code review workflow"""

    DEFAULT_ESTIMATED_COMPLETION_TIME = 300 # 5 minutes

    async def start_review(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Start a new code review"""

        initial_state: CodeReviewState = CodeReviewState(
            git_diffs = request.git_diffs,
            messages = [],
            status = AgentStatus.IN_PROGRESS,
            agent_feedbacks = [],
            final_result = None,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            next_agent = None
        )

        try:
            workflow = create_code_review_workflow({"git_diffs": request.git_diffs})

            async for event in workflow.astream(initial_state):
                log_event(event)

            return CodeReviewResponse(
                status=AgentStatus.IN_PROGRESS,
                message="Code review started successfully",
                estimated_completion_time=self.DEFAULT_ESTIMATED_COMPLETION_TIME
            )

        except Exception as e:
            log.error(f"Failed to start review: {e}")
            return CodeReviewResponse(
                status=AgentStatus.FAILED,
                message=f"Failed to start review: {str(e)}"
            )
