from pathlib import Path

from utils.errors import ValidationError


class InputValidator:
    """Handles validation of CLI arguments and system requirements."""

    @staticmethod
    def validate_project_path(path: str) -> Path:
        """Validate that the project path exists and is a Git repository."""
        project_path = Path(path).expanduser().resolve()

        if not project_path.exists():
            raise ValidationError(f"Project path does not exist: {path}")

        if not project_path.is_dir():
            raise ValidationError(f"Project path is not a directory: {path}")

        git_dir = project_path / ".git"
        if not git_dir.exists():
            raise ValidationError(f"Not a Git repository: {path}")

        return project_path

    @staticmethod
    def validate_output_file(path: str) -> Path:
        """Validate output file path and ensure parent directory exists."""
        output_path = Path(path).expanduser().resolve()

        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    @staticmethod
    def validate_branch_name(branch: str) -> str:
        """Validate branch name format."""
        if not branch or not branch.strip():
            raise ValidationError("Branch name cannot be empty")

        # Basic validation for Git branch names
        invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\']
        if any(char in branch for char in invalid_chars):
            raise ValidationError(f"Invalid branch name: {branch}")

        return branch.strip()
