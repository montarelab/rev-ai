from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration for the Git diff summarizer."""
    project_path: Path
    local_branch: str
    master_branch: str
    output_file: Path
    ollama_model: str = "llama3.2"
    ollama_url: str = "http://localhost:11434"

