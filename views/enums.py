from enum import Enum


class AgentStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    SECURITY = "security"
    ORCHESTRATOR = "orchestrator"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    TECH_LEAD = "tech_lead"
