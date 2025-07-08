from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration for the Git diff summarizer."""
    project_path: Path
    source_branch: str
    target_branch: str
    output_file: Path
    thread_id: str
    task_id: str
    model_name: str
    embedding_model: str
    api_key: str
    vector_db_path: str
    vector_db_collection_name: str


