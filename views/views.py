from datetime import datetime
from typing import Optional, List, Dict, Any

from langchain_core.messages import AIMessage
from pydantic import BaseModel, validator, Field
from pathlib import Path

from views.enums import AgentType, ReviewStatus


class CodeReviewRequest(BaseModel):
    code: str = Field(..., description="Code to be reviewed", min_length=1)
    language: str = Field(..., description="Programming language")
    project_id: Optional[str] = Field(None, description="Project identifier")
    branch_name: Optional[str] = Field(None, description="Git branch name")
    file_path: Optional[Path] = Field(None, description="File path in repository")

    @validator('language')
    def validate_language(cls, v):
        supported_languages = ['python', 'javascript', 'java', 'typescript', 'go']
        if v.lower() not in supported_languages:
            raise ValueError(f'Language must be one of: {supported_languages}')
        return v.lower()

class AgentFeedback(BaseModel):
    agent_type: AgentType
    status: str
    data: AIMessage
    timestamp: datetime
    execution_time: float
    errors: List[str] = []


class CodeReviewResponse(BaseModel):
    task_id: str
    status: ReviewStatus
    message: str
    estimated_completion_time: Optional[int] = None


class ReviewResult(BaseModel):
    task_id: str
    status: ReviewStatus
    original_code: str
    fixed_code: Optional[str] = None
    agent_feedback: Dict[str, Any]
    summary: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
