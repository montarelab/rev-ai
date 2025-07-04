import json
from datetime import datetime

from langchain_core.messages import HumanMessage
from loguru import logger as log

from agents.agents import create_documentation_agent, create_architecture_agent, create_performance_agent, \
    create_security_agent, create_tech_lead_agent
from views.views import AgentType, AgentStatus, AgentFeedback, CodeReviewState


async def security_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Security analysis node"""
    try:
        start_time = datetime.now()
        agent = create_security_agent({"git_diff": state['git_diffs']})

        analysis_message = HumanMessage(
            content=f"Analyze this Python code for security issues:\n\n{state['git_diffs']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message]
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        # Update state
        state["agent_feedbacks"][AgentType.SECURITY] = {
            "agent_type": AgentType.SECURITY.value,
            "status": "completed",
            "data": result['messages'][1],
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "errors": []
        }

        log.info(f"Security analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Security analysis failed: {e}")
        state["agent_feedbacks"][AgentType.SECURITY] = {
            "agent_type": AgentType.SECURITY.value,
            "status": "failed",
            "data": {},
            "timestamp": datetime.now(),
            "execution_time": 0,
            "errors": [str(e)]
        }
        return state


async def performance_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Performance analysis node"""
    try:
        start_time = datetime.now()
        agent = create_performance_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this Python code for performance issues:\n\n{state['git_diffs']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedbacks"][AgentType.PERFORMANCE] = {
            "agent_type": AgentType.PERFORMANCE.value,
            "status": "completed",
            "data": result["messages"][1],
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "errors": []
        }

        log.info(f"Performance analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Performance analysis failed: {e}")
        state["agent_feedbacks"][AgentType.PERFORMANCE] = {
            "agent_type": AgentType.PERFORMANCE.value,
            "status": "failed",
            "data": {},
            "timestamp": datetime.now(),
            "execution_time": 0,
            "errors": [str(e)]
        }
        return state


async def architecture_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Architecture analysis node"""
    try:
        start_time = datetime.now()
        agent = create_architecture_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this Python code for architectural improvements:\n\n{state['git_diffs']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedbacks"][AgentType.ARCHITECTURE] = {
            "agent_type": AgentType.ARCHITECTURE.value,
            "status": "completed",
            "data": result["messages"][1],
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "errors": []
        }

        log.info(f"Architecture analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Architecture analysis failed: {e}")
        state["agent_feedbacks"][AgentType.ARCHITECTURE] = {
            "agent_type": AgentType.ARCHITECTURE.value,
            "status": "failed",
            "data": {},
            "timestamp": datetime.now(),
            "execution_time": 0,
            "errors": [str(e)]
        }
        return state


async def documentation_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Documentation analysis node"""
    try:
        start_time = datetime.now()
        agent = create_documentation_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this Python code for documentation issues:\n\n{state['git_diff']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedbacks"][AgentType.DOCUMENTATION] = {
            "agent_type": AgentType.DOCUMENTATION.value,
            "status": "completed",
            "data": result["messages"][1],
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "errors": []
        }

        log.info(f"Documentation analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Documentation analysis failed: {e}")
        state["agent_feedbacks"][AgentType.DOCUMENTATION] = {
            "agent_type": AgentType.DOCUMENTATION.value,
            "status": "failed",
            "data": {},
            "timestamp": datetime.now(),
            "execution_time": 0,
            "errors": [str(e)]
        }
        return state


async def tech_lead_review_node(state: CodeReviewState) -> CodeReviewState:
    """Tech lead review and decision node"""
    try:
        start_time = datetime.now()
        agent = create_tech_lead_agent()

        # Prepare feedback summary
        feedback_summary = {
            agent_type.value: feedback
            for agent_type, feedback in state["agent_feedbacks"].items()
            if feedback["status"] == "completed"
        }

        review_message = HumanMessage(
            content=f"Review this analysis and decide if changes should be approved or require fixes:\n\n"
                    f"Original Code:\n{state['code']}\n\n"
                    f"Expert Analysis:\n{json.dumps(feedback_summary, indent=2, default=str)}"
        )

        print("Tech lead. check state", state)

        result = await agent.ainvoke({
            "messages": [review_message],
            # "security_analysis": state,
            # "architecture_analysis": state,
            # "performance_analysis": state,
            # "documentation_analysis": state,
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        # Simple decision logic - you can make this more sophisticated
        has_critical_issues = any(
            feedback.get("data") and
            feedback.get("data", {}).get("security_score", 100) < 70 or
            feedback.get("data", {}).get("performance_score", 100) < 70
            for feedback in state["agent_feedbacks"].values()
            if feedback.get("status") == "completed"
        )

        if has_critical_issues:
            state["status"] = AgentStatus.REJECTED
            state["next_agent"] = "engineer"
        else:
            state["status"] = AgentStatus.APPROVED
            state["next_agent"] = None

        state["agent_feedbacks"][AgentType.TECH_LEAD] = {
            "agent_type": AgentType.TECH_LEAD.value,
            "status": "completed",
            "data": result["messages"][1],
            "timestamp": datetime.now(),
            "execution_time": execution_time,
            "errors": []
        }

        state["updated_at"] = datetime.now()
        log.info(f"Tech lead review completed in {execution_time:.2f}s - Status: {state['status']}")
        return state

    except Exception as e:
        log.error(f"Tech lead review failed: {e}")
        state["status"] = AgentStatus.FAILED
        state["updated_at"] = datetime.now()
        return state
