import sys
import traceback

from loguru import logger as log

from config import Config
from errors import ValidationError, GitError, OllamaError
from services.file_writer import FileWriter
from services.git_manager import GitManager
from services.ollama_client import OllamaClient


class GitDiffSummarizer:
    """Main application class that orchestrates the diff summarization process."""

    def __init__(self, config: Config):
        self.config = config
        self.git_manager = GitManager(config.project_path)
        self.ollama_client = OllamaClient(config.ollama_url, config.ollama_model)

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

            # redis_client = Redis(
            #     host='localhost',
            #     port=6379,
            #     db=0,
            #     decode_responses=True,
            #     socket_timeout=5,
            #     socket_connect_timeout=5,
            #     retry_on_timeout=True,
            #     health_check_interval=30
            # )

            # orchestrator = CodeReviewOrchestrator()
            #
            # request = CodeReviewRequest(
            #     code=diff_content,
            #     language="python",
            #     file_path=self.config.project_path,
            #     project_id="TaskManager",
            #     branch_name=self.config.local_branch
            # )
            #
            # response = await orchestrator.start_review(request)
            # print(f"Review started with task_id: {response.task_id}")


            # while True:
            #     status = await orchestrator.get_review_status(response.task_id)
            #     if status['status'] is ReviewStatus.COMPLETED:
            #         log.info("Code review completed successfully!")
            #         break
            #     log.info(f"Current status: {status['status']}")
            #     await asyncio.sleep(5)  # Wait for 5 seconds before the next iteration

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
            log.error(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)


