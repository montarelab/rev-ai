import os
import subprocess
from typing import Dict, Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field


# =============================================================================
# TECH LEAD TOOLS
# =============================================================================

class MergeToolInput(BaseModel):
    source_branch: str = Field(description="Source branch name")
    target_branch: str = Field(description="Target branch name")
    repository_path: str = Field(description="Path to git repository")


@tool("merge_tool", args_schema=MergeToolInput)
def merge_tool(source_branch: str, target_branch: str, repository_path: str) -> Dict[str, Any]:
    """Handle git merges and basic conflict detection."""

    try:
        # Change to repository directory
        original_dir = os.getcwd()
        os.chdir(repository_path)

        # Check if branches exist
        result = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True)
        branches = result.stdout

        if source_branch not in branches or target_branch not in branches:
            return {
                "status": "error",
                "error": "One or both branches do not exist"
            }

        # Check for potential conflicts (simplified)
        result = subprocess.run(
            ['git', 'merge-tree', f'origin/{target_branch}', f'origin/{source_branch}'],
            capture_output=True, text=True
        )

        has_conflicts = '<<<<<<< ' in result.stdout

        merge_info = {
            "status": "success",
            "source_branch": source_branch,
            "target_branch": target_branch,
            "has_conflicts": has_conflicts,
            "can_auto_merge": not has_conflicts
        }

        if has_conflicts:
            merge_info["conflict_files"] = []
            # Parse conflict files (simplified)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('+++') or line.startswith('---'):
                    if 'b/' in line:
                        file_path = line.split('b/', 1)[1]
                        if file_path not in merge_info["conflict_files"]:
                            merge_info["conflict_files"].append(file_path)

        return merge_info

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        # Return to original directory
        os.chdir(original_dir)
