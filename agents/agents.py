from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_handoff_tool

from agents.prompts import *
# Import your tools
from views.views import TechLeadDecision

DEBUG = False


def create_llm():
    """Create and configure LLM instance"""
    return ChatOllama(
        model="llama3.2",
        temperature=0,
        timeout=300,  # 5 minutes timeout
        num_predict=2048,
        debug=DEBUG
    )


def create_security_agent(prompt_dict: dict):
    """Create security analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="security_agent",
        # response_format=SecurityAnalysisResponse,
        prompt=create_security_agent_prompt().invoke(prompt_dict).to_string(),
        debug=DEBUG,
    )


def create_architecture_agent(prompt_dict: dict):
    """Create architecture analysis agent"""
    return create_react_agent(
        create_llm(),
        # response_format=ArchitectureAnalysisResponse,
        tools=[],
        name="architecture_agent",
        prompt=create_architecture_agent_prompt().invoke(prompt_dict).to_string(),
        debug=DEBUG,
    )


def create_performance_agent(prompt_dict: dict):
    """Create performance analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="performance_agent",
        # response_format=PerformanceAnalysisResponse,
        prompt=create_performance_agent_prompt().invoke(prompt_dict).to_string(),
        debug=DEBUG,
    )


def create_documentation_agent(prompt_dict: dict):
    """Create documentation analysis agent"""
    return create_react_agent(
        create_llm(),
        tools=[],
        name="documentation_agent",
        # response_format=DocumentationAnalysisResponse,
        prompt=create_documentation_agent_prompt().invoke(prompt_dict).to_string(),
        debug=DEBUG,
    )


assign_to_security_agent = create_handoff_tool(
    agent_name="security_agent",
    description="Assign task to a security agent.",
)

assign_to_performance_agent = create_handoff_tool(
    agent_name="performance_agent",
    description="Assign task to a performance agent.",
)

assign_to_architecture_agent = create_handoff_tool(
    agent_name="architecture_agent",
    description="Assign task to a architecture agent.",
)

assign_to_documentation_agent = create_handoff_tool(
    agent_name="documentation_agent",
    description="Assign task to a documentation agent.",
)


def create_tech_lead_agent(prompt_dict: dict):
    """Create tech lead decision agent"""
    tech_lead_prompt = create_tech_lead_decision_prompt().invoke(prompt_dict).to_string()
    agent = create_react_agent(
        create_llm(),
        tools=[],
        response_format=TechLeadDecision,
        name="supervisor",
        prompt=tech_lead_prompt,

        debug=DEBUG,
    )

    return agent
