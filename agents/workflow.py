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
from loguru import logger as log
from pydantic import BaseModel, Field

# Import your tools
from views.views import AgentType, ReviewStatus, AgentFeedback


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Issue(BaseModel):
    type: str
    severity: Severity
    file_path: str
    description: str
    recommendation: str


class AgentAnalysisResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    issues: List[Issue]
    merge_recommendation: Literal["approve", "reject", "conditional"]


class SecurityAnalysisResponse(AgentAnalysisResponse):
    pass


class ArchitectureAnalysisResponse(AgentAnalysisResponse):
    pass


class PerformanceAnalysisResponse(AgentAnalysisResponse):
    pass


class DocumentationAnalysisResponse(AgentAnalysisResponse):
    pass


class TechLeadDecision(BaseModel):
    final_decision: Literal["approve", "reject", "request_changes"]
    reasoning: str
    priority_issues: List[str]


class CodeFix(BaseModel):
    file_path: str
    fixed_code: str
    explanation: str


class EngineerResponse(BaseModel):
    fixes_implemented: List[CodeFix]
    summary: str


# Agent Prompt Templates

def create_security_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a security expert analyzing git diff for potential security vulnerabilities.

ANALYZE THE FOLLOWING GIT DIFF FOR:
1. Hardcoded secrets, passwords, API keys, or tokens
2. SQL injection vulnerabilities
3. XSS (Cross-Site Scripting) opportunities
4. Authentication and authorization issues
5. Input validation problems
6. Unsafe deserialization
7. Path traversal vulnerabilities
8. New dependencies and their security implications
9. Exposed sensitive endpoints
10. Insecure cryptographic practices

INSTRUCTIONS:
- Focus only on the changed lines (+ additions, - deletions)
- Consider the context of surrounding code
- Identify both obvious and subtle security issues
- Assess the severity based on exploitability and impact
- Provide specific line numbers when possible
- Give actionable recommendations for fixes

Git Diff:
{git_diff}

Provide a thorough security analysis following the SecurityAnalysisResponse model.""")


def create_architecture_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a software architect analyzing git diff for architectural quality and design patterns.

ANALYZE THE FOLLOWING GIT DIFF FOR:
1. Design pattern violations or improvements
2. Code duplication and DRY principle violations
3. Separation of concerns
4. Coupling and cohesion issues
5. SOLID principles adherence
6. Code organization and structure
7. Naming conventions
8. Class and method responsibilities
9. Interface design
10. Architectural layer violations

INSTRUCTIONS:
- Evaluate architectural impact of the changes
- Look for code smells and anti-patterns
- Assess maintainability and extensibility
- Consider the existing codebase context
- Identify opportunities for refactoring
- Rate the overall architectural quality

Git Diff:
{git_diff}

Provide a comprehensive architectural analysis following the ArchitectureAnalysisResponse model.""")


def create_performance_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a performance engineer analyzing git diff for performance implications.

ANALYZE THE FOLLOWING GIT DIFF FOR:
1. Algorithm complexity issues (time and space)
2. Database query optimization opportunities
3. Memory usage and potential leaks
4. I/O operations efficiency
5. Caching opportunities
6. Loop optimizations
7. Data structure choices
8. Lazy loading vs eager loading
9. Asynchronous operation opportunities
10. Resource management

INSTRUCTIONS:
- Focus on performance impact of changes
- Identify Big O complexity issues
- Look for N+1 query problems
- Assess scalability implications
- Consider both CPU and memory performance
- Provide optimization recommendations

Git Diff:
{git_diff}

Provide a detailed performance analysis following the PerformanceAnalysisResponse model.""")


def create_documentation_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a technical writer analyzing git diff for documentation quality.

ANALYZE THE FOLLOWING GIT DIFF FOR:
1. Missing or inadequate function/method documentation
2. Class and module docstring quality
3. Inline comment appropriateness
4. API documentation completeness
5. README updates needed
6. Code examples in documentation
7. Parameter and return value documentation
8. Error handling documentation
9. Configuration documentation
10. Architecture decision records

INSTRUCTIONS:
- Assess documentation coverage for new/changed code
- Evaluate clarity and usefulness of existing docs
- Identify missing documentation areas
- Check for outdated documentation
- Consider end-user and developer documentation needs

Git Diff:
{git_diff}

Provide a thorough documentation analysis following the DocumentationAnalysisResponse model.""")


def create_tech_lead_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a tech lead making the final decision on whether to approve this merge.

You have received analysis from your team:

SECURITY ANALYSIS:
{security_analysis}

ARCHITECTURE ANALYSIS:
{architecture_analysis}

PERFORMANCE ANALYSIS:
{performance_analysis}

DOCUMENTATION ANALYSIS:
{documentation_analysis}

ORIGINAL GIT DIFF:
{git_diff}

INSTRUCTIONS:
- Weigh all expert opinions and findings
- Consider the overall risk vs benefit
- Make a final decision: approve, reject, or request changes
- Prioritize the most critical issues
- Balance perfectionism with delivery needs
- Consider the team's current capacity and deadlines
- Provide clear reasoning for your decision

Make your final decision following the TechLeadDecision model.""")


def create_engineer_agent_prompt():
    return ChatPromptTemplate.from_template("""You are a software engineer tasked with implementing fixes based on expert feedback.

EXPERT FEEDBACK TO ADDRESS:
{expert_feedback}

ORIGINAL GIT DIFF:
{git_diff}

INSTRUCTIONS:
- Implement fixes for the identified issues where possible
- Provide corrected code snippets
- Explain what you fixed and why
- Identify issues that require manual intervention
- Suggest additional steps developers should take
- Focus on the most critical issues first
- Ensure fixes don't introduce new problems

Provide your fixes and recommendations following the EngineerResponse model.""")


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
            response_format=SecurityAnalysisResponse,
            prompt=create_security_agent_prompt().invoke(prompt_dict).to_string(),
        )


    def create_architecture_agent(prompt_dict: dict):
        """Create architecture analysis agent"""
        return create_react_agent(
            create_llm(),
            response_format=ArchitectureAnalysisResponse,
            tools=[],
            prompt=create_architecture_agent_prompt().invoke(prompt_dict).to_string(),
        )


    def create_performance_agent(prompt_dict: dict):
        """Create performance analysis agent"""
        return create_react_agent(
            create_llm(),
            tools=[],
            response_format=PerformanceAnalysisResponse,
            prompt=create_performance_agent_prompt().invoke(prompt_dict).to_string(),
        )


    def create_documentation_agent(prompt_dict: dict):
        """Create documentation analysis agent"""
        return create_react_agent(
            create_llm(),
            tools=[],
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

# LangGraph State - must be TypedDict with Annotated fields for proper message handling
class CodeReviewState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    task_id: str
    code: str
    language: str
    project_id: Optional[str]
    branch_name: Optional[str]
    file_path: Optional[str]
    status: ReviewStatus
    agent_feedback: List[AgentFeedback]
    final_result: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    retry_count: int
    next_agent: Optional[str]  # For routing between agents


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
            state["status"] = ReviewStatus.REJECTED
            state["next_agent"] = "engineer"
        else:
            state["status"] = ReviewStatus.APPROVED
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
        state["status"] = ReviewStatus.FAILED
        state["updated_at"] = datetime.now()
        return state


async def software_engineer_node(state: CodeReviewState) -> CodeReviewState:
    """Software engineer fixes node"""
    try:
        start_time = datetime.now()
        agent = create_engineer_agent()

        # Prepare expert feedback for software engineer
        expert_feedback = {
            agent_type: feedback.data
            for agent_type, feedback in state["agent_feedback"].items()
            if feedback.status == "completed" and agent_type != "tech_lead"
        }

        fix_message = HumanMessage(
            content=f"Fix the following code based on expert feedback:\n\n"
                    f"Original Code:\n{state['code']}\n\n"
                    f"Expert Feedback:\n{json.dumps(expert_feedback, indent=2, default=str)}"
        )

        result = await agent.ainvoke({
            "messages": [fix_message],
            "git_diff": state['code']
        })

        execution_time = (datetime.now() - start_time).total_seconds()

        state["final_result"] = result
        state["status"] = ReviewStatus.COMPLETED
        state["updated_at"] = datetime.now()
        state["next_agent"] = None

        state["agent_feedback"]["software_engineer"] = AgentFeedback(
            agent_type=AgentType.SOFTWARE_ENGINEER.value,
            status="completed",
            data=result["messages"][1],
            timestamp=datetime.now(),
            execution_time=execution_time,
            errors=[]
        )

        log.info(f"Software engineer fixes completed in {execution_time:.2f}s")
        return state

    except Exception as e:
        log.error(f"Software engineer fixes failed: {e}")
        state["status"] = ReviewStatus.FAILED
        state["updated_at"] = datetime.now()
        return state


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def should_continue_to_engineer(state: CodeReviewState) -> str:
    """Determine if we should route to software engineer or end"""
    log.info("Checking if we need to route to software engineer...")
    if state.get("next_agent") == "engineer":
        return "engineer"
    else:
        return END


# =============================================================================
# WORKFLOW DEFINITION
# =============================================================================

def create_code_review_workflow():
    """Create the code review workflow using LangGraph"""

    # Create the state graph
    workflow = StateGraph(CodeReviewState)

    # Add nodes
    workflow.add_node(AgentType.SECURITY, security_analysis_node)
    workflow.add_node(AgentType.PERFORMANCE, performance_analysis_node)
    workflow.add_node(AgentType.ARCHITECTURE, architecture_analysis_node)
    workflow.add_node(AgentType.DOCUMENTATION, documentation_analysis_node)
    workflow.add_node(AgentType.TECH_LEAD, tech_lead_review_node)
    workflow.add_node(AgentType.SOFTWARE_ENGINEER, software_engineer_node)

    # Set entry point
    workflow.set_entry_point(AgentType.SECURITY)

    # Add edges for parallel execution of analysis agents
    workflow.add_edge(AgentType.SECURITY, AgentType.PERFORMANCE)
    workflow.add_edge(AgentType.PERFORMANCE, AgentType.ARCHITECTURE)
    workflow.add_edge(AgentType.ARCHITECTURE, AgentType.DOCUMENTATION)
    workflow.add_edge(AgentType.DOCUMENTATION, AgentType.TECH_LEAD)

    # Add conditional edge from tech_lead
    workflow.add_conditional_edges(
        AgentType.TECH_LEAD,
        should_continue_to_engineer,
        {
            AgentType.SOFTWARE_ENGINEER: AgentType.SOFTWARE_ENGINEER,
            END: END
        }
    )

    # Engineer always ends the workflow
    workflow.add_edge(AgentType.SOFTWARE_ENGINEER, END)

    # Compile the workflow
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app
