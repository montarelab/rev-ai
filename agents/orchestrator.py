from datetime import datetime
from loguru import logger as log
from agents.workflow import create_code_review_workflow
from views.views import AgentStatus, CodeReviewResponse, CodeReviewRequest, CodeReviewState

from langchain_core.messages import convert_to_messages

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
            agent_feedbacks = {},
            final_result = None,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            next_agent = None,
        )

        try:
            prompt = f"Analyze this code diff and provide feedback on potential issues, improvements, and recommendations.: {request.git_diffs}"
            workflow = create_code_review_workflow({"git_diffs": request.git_diffs})

            # async for event in workflow.stream({
            #         "messages": [
            #             {
            #                 "role": "user",
            #                 "content": prompt,
            #             }
            #         ]
            #     },):
            #     log_event(event)

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
            # for chunk in workflow.stream(initial_state):
                # log_event(event)

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

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")