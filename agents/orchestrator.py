from datetime import datetime
from typing import Optional

from loguru import logger as log

# Import your tools
from agents.workflow import create_code_review_workflow, CodeReviewState
from services.state_manager import StateManager
from views.views import  ReviewStatus, CodeReviewResponse, CodeReviewRequest, ReviewResult

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
    # Extract info from the state object
    # Check if state is a dictionary
    if isinstance(state, dict):
        if 'task_id' in state:
            log.info(f"Task ID: {state['task_id']}")
        if 'status' in state:
            log.info(f"Status: {state['status']}")
        if 'agent_feedback' in state:
            feedback = state['agent_feedback']
            log.info(f"Agent feedback: {feedback}")
            # last_key = next(reversed(feedback.keys()), None) if feedback else None
            # log.info(f"Content: {feedback[last_key].data.content if last_key else 'No content'}")
        if 'next_agent' in state:
            log.info(f"Next agent: {state['next_agent']}")


class CodeReviewOrchestrator:
    """Main orchestrator for code review workflow"""

    def __init__(self, redis_client=None):
        self.workflow = create_code_review_workflow()
        self.state_manager = StateManager(redis_client) if redis_client else None

    async def start_review(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Start a new code review"""
        import uuid

        task_id = str(uuid.uuid4())

        # Initialize state
        initial_state: CodeReviewState = CodeReviewState(
            messages = [],
            task_id = task_id,
            code = request.code,
            language = request.language,
            project_id = request.project_id,
            branch_name = request.branch_name,
            file_path = request.file_path,
            status = ReviewStatus.IN_PROGRESS,
            agent_feedback = {},
            final_result = None,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            retry_count = 0,
            next_agent = None
        )

        try:
            # Save initial state
            if self.state_manager:
                await self.state_manager.save_state(task_id, initial_state)

            # Start the workflow (async)
            config = {"configurable": {"thread_id": task_id}}

            # This will run the workflow asynchronously
            async for event in self.workflow.astream(initial_state, config):
                log_event(event)

                # Save state after each event
                if self.state_manager and event:
                    for node_name, node_state in event.items():
                        await self.state_manager.save_state(task_id, node_state)

            return CodeReviewResponse(
                task_id=task_id,
                status=ReviewStatus.IN_PROGRESS,
                message="Code review started successfully",
                estimated_completion_time=300  # 5 minutes estimate
            )

        except Exception as e:
            log.error(f"Failed to start review: {e}")
            return CodeReviewResponse(
                task_id=task_id,
                status=ReviewStatus.FAILED,
                message=f"Failed to start review: {str(e)}"
            )

    async def get_review_status(self, task_id: str) -> Optional[CodeReviewState]:
        """Get current review status"""
        if self.state_manager:
            return await self.state_manager.get_state(task_id)
        return None

    async def get_review_result(self, task_id: str) -> Optional[ReviewResult]:
        """Get final review result"""
        state = await self.get_review_status(task_id)
        if not state:
            return None

        if state["status"] in [ReviewStatus.COMPLETED, ReviewStatus.APPROVED]:
            return ReviewResult(
                task_id=task_id,
                status=state["status"],
                original_code=state["code"],
                fixed_code=state.get("final_result", {}).get("fixed_code"),
                agent_feedback=state["agent_feedback"],
                summary=state.get("final_result", {}),
                created_at=state["created_at"],
                completed_at=state["updated_at"],
                execution_time=None  # Calculate if needed
            )

        return None
