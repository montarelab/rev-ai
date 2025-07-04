from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Literal, TypedDict, Annotated

from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel, validator, Field
from pathlib import Path

from views.enums import AgentType, AgentStatus


class CodeReviewRequest(BaseModel):
    git_diffs: str = Field(..., description="Differences of code", min_length=1)


class AgentFeedback(BaseModel):
    agent_type: AgentType
    status: AgentStatus
    data: AIMessage
    timestamp: datetime
    execution_time: float
    errors: List[str] = []


class CodeReviewResponse(BaseModel):
    status: AgentStatus
    message: str
    estimated_completion_time: Optional[int] = None


class ReviewResult(BaseModel):
    status: AgentStatus
    original_git_diffs: str
    agent_feedback: AgentFeedback
    summary: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None


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


# LangGraph State - must be TypedDict with Annotated fields for proper message handling
class CodeReviewState(TypedDict):
    git_diffs: str
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    status: AgentStatus
    agent_feedbacks: List[AgentFeedback]
    final_result: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    next_agent: Optional[str]  # For routing between agents
