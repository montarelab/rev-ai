from langgraph.constants import END, START
from langgraph.graph import StateGraph, MessagesState

from agents.agents import create_documentation_agent, create_architecture_agent, create_performance_agent, \
    create_security_agent, create_tech_lead_agent
# Import your tools
from views.views import CodeReviewState


def create_code_review_workflow(prompt_dict: dict):
    """Create the code review workflow using LangGraph"""

    print("init agents")
    security_agent = create_security_agent(prompt_dict)
    performance_agent = create_performance_agent(prompt_dict)
    architecture_agent = create_architecture_agent(prompt_dict)
    documentation_agent = create_documentation_agent(prompt_dict)
    tech_lead_agent = create_tech_lead_agent(prompt_dict)

    print('created tech lead')

    supervisor = (
        StateGraph(CodeReviewState)

        .add_node(tech_lead_agent, destinations=(
            "security_agent", "performance_agent",
            "architecture_agent", "documentation_agent", END))

        .add_node(security_agent)
        .add_node(performance_agent)
        .add_node(architecture_agent)
        .add_node(documentation_agent)

        .add_edge(START, "security_agent")
        .add_edge(START, "performance_agent")
        .add_edge(START, "architecture_agent")
        .add_edge(START, "documentation_agent")


        .add_edge("security_agent", "supervisor")
        .add_edge("performance_agent", "supervisor")
        .add_edge("architecture_agent", "supervisor")
        .add_edge("documentation_agent", "supervisor")

        .add_edge("supervisor", END)

        .compile()
    )


    print('compiled app')
    return supervisor
