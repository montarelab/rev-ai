import sys
import traceback

from loguru import logger as log

from ai.orchestrator import CodeReviewOrchestrator
from config import Config
from utils.errors import ValidationError, GitError
from services.file_writer import FileWriter
from services.git_manager import GitManager
from ai.tools.get_file_content import get_file_content_with_project_oath
from views.views import CodeReviewRequest, ChangedFile


class CodeDiffAnalyzer:
    """Main application class that orchestrates the diff analyzing process."""

    def __init__(self, config: Config):
        self.config = config
        self.git_manager = GitManager(config.project_path)

    async def run(self):
        """Execute the complete diff analysis workflow."""
        try:
            log.info("Starting Git diff analyzing...")

            self.git_manager.validate_branches(
                self.config.source_branch,
                self.config.target_branch
            )
            log.info("Validated branches successfully.")

            orchestrator = CodeReviewOrchestrator(self.config)
            log.info("Created orchestrator.")

            request = self._create_request()
            log.info("Created request.")

            response = await orchestrator.review_code(request)
            log.info(f"Reviewed code successfully. Saving response to {self.config.output_file}...")

            FileWriter.write_summary(self.config.output_file, response, self.config)
            log.info("Git diff summarization completed successfully!")

        except (ValidationError, GitError) as e:
            log.error(f"Operation failed: {e}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            log.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)

    def _create_request(self):
        changed_files = []

        changed_file_paths = self.git_manager.get_diff_names_only(
            self.config.source_branch, self.config.target_branch)

        log.info(f"Received {len(changed_file_paths)} changed files")

        for file_path in changed_file_paths:

            log.info(f"Preprocessing file for analysis: {file_path}")
            changes = self.git_manager.get_diff_for_file(
                file_path, self.config.source_branch, self.config.target_branch)

            content = get_file_content_with_project_oath(file_path, self.config.project_path)

            changed_files.append(ChangedFile(
                content=content,
                file_path=file_path,
                changes=changes
            ))

            log.info(f"Preprocessed file for analysis: {file_path}")


        return CodeReviewRequest(
            changed_files=changed_files
        )
