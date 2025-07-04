import sys
import traceback

from loguru import logger as log

from agents.orchestrator import CodeReviewOrchestrator
from config import Config
from errors import ValidationError, GitError, OllamaError
from services.file_writer import FileWriter
from services.git_manager import GitManager
from services.summarizer_client import DiffSummarizerClient
from views.views import CodeReviewRequest


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

            # Get diff
            diff_content = self.git_manager.get_diff(
                self.config.local_branch,
                self.config.master_branch
            )

            log.info("Fetched Git diff successfully.")

            # Generate summary
            orchestrator = CodeReviewOrchestrator()

            request = CodeReviewRequest(
                git_diffs=diff_content
            )

            response = await orchestrator.start_review(request)
            print(f"Response received with message: {response.message}")

            # Write output
            FileWriter.write_summary(self.config.output_file, response.output, self.config)

            log.info("Git diff summarization completed successfully!")

        except (ValidationError, GitError, OllamaError) as e:
            log.error(f"Operation failed: {e}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            log.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
