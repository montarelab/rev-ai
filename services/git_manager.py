import subprocess
from pathlib import Path

from utils.errors import GitError
from loguru import logger as log


class GitManager:
    """Handles Git operations for branch comparison."""

    def __init__(self, project_path: Path):
        self.project_path = project_path


    def _run_git_command(self, args: list) -> str:
        """Run a Git command and return its output."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_path,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {e.stderr}")


    def validate_branches(self, source_branch: str, target_branch: str):
        """Validate that both branches exist."""
        try:
            # Check if branches exist
            branches = self._run_git_command(["branch", "-a"])

            local_exists = any(
                source_branch in line.strip().replace("* ", "")
                for line in branches.split('\n')
            )

            master_exists = any(
                target_branch in line.strip().replace("* ", "")
                for line in branches.split('\n')
            )

            if not local_exists:
                raise GitError(f"Local branch '{source_branch}' does not exist")

            if not master_exists:
                raise GitError(f"Master branch '{target_branch}' does not exist")

        except GitError:
            raise
        except Exception as e:
            raise GitError(f"Failed to validate branches: {e}")


    def get_diff_for_file(self, file_path, source_branch: str, target_branch: str) -> str:
        """Get only names of the diff between two branches."""

        full_file_path = self.project_path / file_path

        try:
            log.info("Fetching latest changes...")
            self._run_git_command(["fetch", "origin"])

            log.info(f"Getting diff in file {file_path} between {target_branch} and {source_branch}...")
            diff = self._run_git_command([
                "diff",
                f"{target_branch}...{source_branch}",
                '--',
                full_file_path,
                "--no-color",
            ])

            if not diff:
                log.warning(f"No difference for file {file_path} found")
                return f"No difference for file {file_path} found."

            return diff

        except GitError:
            raise
        except Exception as e:
            raise GitError(f"Failed to get diff: {e}")


    def get_diff_names_only(self, source_branch: str, target_branch: str) -> list[str]:
        """Get only names of the diff between two branches."""
        try:
            log.info("Fetching latest changes...")
            self._run_git_command(["fetch", "origin"])

            log.info(f"Getting changed files between {target_branch} and {source_branch}...")
            diff = self._run_git_command([
                "diff",
                f"{target_branch}...{source_branch}",
                "--name-only",
                "--no-color"
            ])

            if not diff:
                log.warning("No changed files")
                return "No changed files."

            return diff.strip().split('\n')


        except GitError:
            raise
        except Exception as e:
            raise GitError(f"Failed to get diff: {e}")



    def get_diff_full(self, source_branch: str, target_branch: str) -> str:
        """Get the diff between two branches."""
        try:
            log.info("Fetching latest changes...")
            self._run_git_command(["fetch", "origin"])

            log.info(f"Getting diff between {target_branch} and {source_branch}...")
            diff = self._run_git_command([
                "diff",
                f"{target_branch}...{source_branch}",
                "--no-color"
            ])

            if not diff:
                log.warning("No differences found between branches")
                return "No differences found between the specified branches."

            return diff

        except GitError:
            raise
        except Exception as e:
            raise GitError(f"Failed to get diff: {e}")

