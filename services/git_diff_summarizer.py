import argparse
import sys

from config import Config
from errors import ValidationError, GitError, OllamaError
from loguru import logger as log
from services.file_writer import FileWriter
from services.git_manager import GitManager
from services.ollama_client import OllamaClient


class GitDiffSummarizer:
    """Main application class that orchestrates the diff summarization process."""

    def __init__(self, config: Config):
        self.config = config
        self.git_manager = GitManager(config.project_path)
        self.ollama_client = OllamaClient(config.ollama_url, config.ollama_model)

    def run(self):
        """Execute the complete diff summarization workflow."""
        try:
            log.info("Starting Git diff summarization...")

            # Validate branches
            self.git_manager.validate_branches(
                self.config.local_branch,
                self.config.master_branch
            )

            # Get diff
            diff_content = self.git_manager.get_diff(
                self.config.local_branch,
                self.config.master_branch
            )

            # Generate summary
            summary = self.ollama_client.summarize_diff(diff_content)

            # Write output
            FileWriter.write_summary(self.config.output_file, summary, self.config)

            log.info("Git diff summarization completed successfully!")

        except (ValidationError, GitError, OllamaError) as e:
            log.error(f"Operation failed: {e}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            sys.exit(1)

