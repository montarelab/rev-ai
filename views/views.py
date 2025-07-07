from dataclasses import dataclass
from typing import Optional, List, TypedDict

from pydantic import BaseModel


class ChangedFile(BaseModel):
    file_path: str
    content: str
    changes: Optional[str] = None

class CodeReviewRequest(BaseModel):
    changed_files: List[ChangedFile]


@dataclass
class CodeReviewOutput(TypedDict):
    issue_type: str
    severity: str
    file_path: str
    description: str
    recommendation: str
    reasoning: str