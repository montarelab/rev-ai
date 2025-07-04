import json
from datetime import datetime
from enum import Enum
from typing import TypedDict, List, Annotated, Optional, Dict, Any, Literal

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from loguru import logger as log
from pydantic import BaseModel, Field

from agents.prompts import *
# Import your tools
from views.views import AgentType, AgentStatus, AgentFeedback, SecurityAnalysisResponse, ArchitectureAnalysisResponse, \
    PerformanceAnalysisResponse, DocumentationAnalysisResponse, TechLeadDecision, EngineerResponse, CodeReviewState


def create_llm():
    """Create and configure LLM instance"""
    return ChatOllama(
        model="llama3.2",
        temperature=0,
        timeout=300,  # 5 minutes timeout
        num_predict=2048,
    )


def create_security_agent(prompt_dict: dict):
    """Create security analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="security_agent",
        response_format=SecurityAnalysisResponse,
        prompt=create_security_agent_prompt().invoke(prompt_dict).to_string(),
    )


def create_architecture_agent(prompt_dict: dict):
    """Create architecture analysis agent"""
    return create_react_agent(
        create_llm(),
        response_format=ArchitectureAnalysisResponse,
        tools=[],
        name="architecture_agent",
        prompt=create_architecture_agent_prompt().invoke(prompt_dict).to_string(),
    )


def create_performance_agent(prompt_dict: dict):
    """Create performance analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="performance_agent",
        response_format=PerformanceAnalysisResponse,
        prompt=create_performance_agent_prompt().invoke(prompt_dict).to_string(),
    )


def create_documentation_agent(prompt_dict: dict):
    """Create documentation analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="documentation_agent",
        response_format=DocumentationAnalysisResponse,
        prompt=create_documentation_agent_prompt().invoke(prompt_dict).to_string(),
    )


def create_tech_lead_agent(prompt_dict: dict):
    """Create tech lead decision agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        response_format=TechLeadDecision,
        prompt=create_tech_lead_agent_prompt().invoke(prompt_dict).to_string(),
    )


def create_engineer_agent(prompt_dict: dict):
    """Create software engineer fixing agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        response_format=EngineerResponse,
        prompt=create_engineer_agent_prompt().invoke(prompt_dict).to_string(),
    )


# =============================================================================
# NODE FUNCTIONS
# =============================================================================



async def security_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Security analysis node"""
    try:
        start_time = datetime.now()
        print("start")
        agent = create_security_agent({"git_diff": state['code']})
        print("agent created")

        # Create analysis message
        analysis_message = HumanMessage(
            content=f"Analyze this {state['language']} code for security issues:\n\n{state['code']}"
        )

        print('start')
        # Run security analysis

        result = await agent.ainvoke({
            "git_diff": state['code'],
            "messages": [analysis_message]
        })

        print("ready")
        print(f"Security analysis result: {result}")

        execution_time = (datetime.now() - start_time).total_seconds()

        # Update state
        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.SECURITY.value,
            status="completed",
            data=result['messages'][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        ))

        log.info(f"Security analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Security analysis failed: {e}")
        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.SECURITY.value,
            status="failed",
            data={},
            timestamp=datetime.now(),
            execution_time=0,
            errors=[str(e)]
        ))
        return state


async def performance_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Performance analysis node"""
    try:
        start_time = datetime.now()
        agent = create_performance_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this {state['language']} code for performance issues:\n\n{state['code']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
            "git_diff": state['code']
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.PERFORMANCE.value,
            status="completed",
            data=result["messages"][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        ))

        log.info(f"Performance analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Performance analysis failed: {e}")
        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.PERFORMANCE.value,
            status="failed",
            data={},
            timestamp=datetime.now(),
            execution_time=0,
            errors=[str(e)]
        ))
        return state


async def architecture_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Architecture analysis node"""
    try:
        start_time = datetime.now()
        agent = create_architecture_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this {state['language']} code for architectural improvements:\n\n{state['code']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
            "git_diff": state['code']
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.ARCHITECTURE.value,
            status="completed",
            data=result["messages"][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        ))

        log.info(f"Architecture analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Architecture analysis failed: {e}")
        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.ARCHITECTURE.value,
            status="failed",
            data={},
            timestamp=datetime.now(),
            execution_time=0,
            errors=[str(e)]
        ))
        return state


async def documentation_analysis_node(state: CodeReviewState) -> CodeReviewState:
    """Documentation analysis node"""
    try:
        start_time = datetime.now()
        agent = create_documentation_agent()

        analysis_message = HumanMessage(
            content=f"Analyze this {state['language']} code for documentation issues:\n\n{state['code']}"
        )

        result = await agent.ainvoke({
            "messages": [analysis_message],
            "git_diff": state['code']
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.DOCUMENTATION.value,
            status="completed",
            data=result["messages"][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        ))

        log.info(f"Documentation analysis completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Documentation analysis failed: {e}")
        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.DOCUMENTATION.value,
            status="failed",
            data={},
            timestamp=datetime.now(),
            execution_time=0,
            errors=[str(e)]
        ))
        return state


async def tech_lead_review_node(state: CodeReviewState) -> CodeReviewState:
    """Tech lead review and decision node"""
    try:
        start_time = datetime.now()
        agent = create_tech_lead_agent()

        # Prepare feedback summary
        feedback_summary = {
            agent_type: feedback.agent_type
            for agent_type, feedback in state["agent_feedback"].items()
            if feedback.status == "completed"
        }

        review_message = HumanMessage(
            content=f"Review this analysis and decide if changes should be approved or require fixes:\n\n"
                    f"Original Code:\n{state['code']}\n\n"
                    f"Expert Analysis:\n{json.dumps(feedback_summary, indent=2, default=str)}"
        )

        print("Tech lead. check state", state)

        result = await agent.ainvoke({
            "messages": [review_message],
            "git_diff": state['code'],
            # "security_analysis": state,
            # "architecture_analysis": state,
            # "performance_analysis": state,
            # "documentation_analysis": state,
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        # Simple decision logic - you can make this more sophisticated
        has_critical_issues = any(
            feedback.data and
            feedback.data.security_score and
            feedback.data.performance_score and
            feedback.data.security_score < 70 or
            feedback.data.performance_score < 70
            for feedback in state["agent_feedback"].values()
            if feedback.status == "completed"
        )

        if has_critical_issues:
            state["status"] = AgentStatus.REJECTED
            state["next_agent"] = "engineer"
        else:
            state["status"] = AgentStatus.APPROVED
            state["next_agent"] = None

        state["agent_feedback"].append(AgentFeedback(
            agent_type=AgentType.TECH_LEAD.value,
            status="completed",
            data=result["messages"][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        ))

        state["updated_at"] = datetime.now()
        log.info(f"Tech lead review completed in {execution_time:.2f}s - Status: {state['status']}")
        return state

    except Exception as e:
        log.error(f"Tech lead review failed: {e}")
        state["status"] = AgentStatus.FAILED
        state["updated_at"] = datetime.now()
        return state


# =============================================================================
# WORKFLOW DEFINITION
# =============================================================================

def create_code_review_workflow(prompt_dict: dict):
    """Create the code review workflow using LangGraph"""

    security_agent = create_security_agent(prompt_dict)
    performance_agent = create_performance_agent(prompt_dict)
    architecture_agent = create_architecture_agent(prompt_dict)
    documentation_agent = create_documentation_agent(prompt_dict)
    tech_lead_agent = create_supervisor(
        model=create_llm(),
        prompt=create_tech_lead_agent_prompt(),
        response_format=TechLeadDecision,
        parallel_tool_calls=True,
        state_schema=CodeReviewState,
        agents=[security_agent, performance_agent, architecture_agent, documentation_agent],
    )

    app = tech_lead_agent.compile()


    # Create the state graph
    # workflow = StateGraph(CodeReviewState)
    #
    # # Add nodes
    # workflow.add_node(AgentType.SECURITY, security_analysis_node)
    # workflow.add_node(AgentType.PERFORMANCE, performance_analysis_node)
    # workflow.add_node(AgentType.ARCHITECTURE, architecture_analysis_node)
    # workflow.add_node(AgentType.DOCUMENTATION, documentation_analysis_node)
    # workflow.add_node(AgentType.TECH_LEAD, tech_lead_review_node)
    # workflow.add_node(AgentType.SOFTWARE_ENGINEER, software_engineer_node)
    #
    # # Set entry point
    # workflow.set_entry_point(AgentType.SECURITY)
    #
    # # Add edges for parallel execution of analysis agents
    # workflow.add_edge(AgentType.SECURITY, AgentType.PERFORMANCE)
    # workflow.add_edge(AgentType.PERFORMANCE, AgentType.ARCHITECTURE)
    # workflow.add_edge(AgentType.ARCHITECTURE, AgentType.DOCUMENTATION)
    # workflow.add_edge(AgentType.DOCUMENTATION, AgentType.TECH_LEAD)
    #
    # # Add conditional edge from tech_lead
    # workflow.add_conditional_edges(
    #     AgentType.TECH_LEAD,
    #     should_continue_to_engineer,
    #     {
    #         AgentType.SOFTWARE_ENGINEER: AgentType.SOFTWARE_ENGINEER,
    #         END: END
    #     }
    # )
    #
    # # Engineer always ends the workflow
    # workflow.add_edge(AgentType.SOFTWARE_ENGINEER, END)

    # Compile the workflow
    # memory = MemorySaver()
    # app = workflow.compile(checkpointer=memory)

    return app
