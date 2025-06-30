from enum import Enum


class ReviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentType(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    TECH_LEAD = "tech_lead"
    SOFTWARE_ENGINEER = "software_engineer"
