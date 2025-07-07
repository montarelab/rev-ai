import sys
import traceback

from loguru import logger as log

from agents.orchestrator import CodeReviewOrchestrator
from config import Config
from errors import ValidationError, GitError, OllamaError
from services.file_writer import FileWriter
from services.git_manager import GitManager
from services.summarizer_client import DiffSummarizerClient
from views.views import CodeReviewRequest, ChangedFile
from tools.get_file_size import get_file_content

class GitDiffSummarizer:
    """Main application class that orchestrates the diff summarization process."""

    def __init__(self, config: Config):
        self.config = config
        self.git_manager = GitManager(config.project_path)
        self.ollama_client = DiffSummarizerClient(config.ollama_url, config.ollama_model)

    async def run(self):
        """Execute the complete diff summarization workflow."""
        try:
            log.info("Starting Git diff summarization...")

            # Validate branches
            self.git_manager.validate_branches(
                self.config.local_branch,
                self.config.master_branch
            )

            log.info("Validated branches successfully.")

            log.info("Fetched Git diff successfully.")

            orchestrator = CodeReviewOrchestrator()

            request = self.create_request()

            response = await orchestrator.review_code(request)

            print(f"Response received with message: {response}")

            # Write output
            FileWriter.write_summary(self.config.output_file, response, self.config)

            log.info("Git diff summarization completed successfully!")

        except (ValidationError, GitError, OllamaError) as e:
            log.error(f"Operation failed: {e}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            log.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)

    def create_request(self):
        changed_files = []

        changed_file_paths = self.git_manager.get_diff_names_only(
            self.config.local_branch, self.config.master_branch)

        for file_path in changed_file_paths:
            changes = self.git_manager.get_diff_for_file(
                file_path, self.config.local_branch, self.config.master_branch)

            content = get_file_content.invoke(file_path)

            changed_files.append(ChangedFile(
                content=content,
                file_path=file_path,
                changes=changes
            ))

        request = CodeReviewRequest(
            changed_files=changed_files
        )

        return request
