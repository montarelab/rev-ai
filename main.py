import asyncio
import os
import sys
import uuid

import pyfiglet
# from dotenv import load_dotenv
from loguru import logger as log

from config import Config
from errors import ValidationError
from services.git_diff_summarizer import GitDiffSummarizer
from services.input_validator import InputValidator
from utils.parser import create_parser

# load_dotenv()


logs_dir = os.getenv("LOGS_DIR")
os.makedirs(logs_dir, exist_ok=True)
log.add(f"{logs_dir}/app.log", rotation="1 MB", retention="10 days", level="DEBUG")




async def main():
    """Main entry point of the application."""
    await print_banner()

    parser = create_parser()
    args = parser.parse_args()

    try:
        if not all([args.project_path, args.source_branch, args.target_branch, args.output_file]):
            parser.error("project_path, source_branch, target_branch, and output_file are required for direct diff analysis mode.")

        # Validate inputs for diff analysis
        log.info("Validating inputs...")
        InputValidator.check_git_availability()
        # InputValidator.check_ollama_availability(args.ollama_url)

        project_path = InputValidator.validate_project_path(args.project_path)
        output_file = InputValidator.validate_output_file(args.output_file)
        source_branch = InputValidator.validate_branch_name(args.source_branch)
        target_branch = InputValidator.validate_branch_name(args.target_branch)

        # Create configuration
        config = Config(
            project_path=project_path,
            source_branch=source_branch,
            target_branch=target_branch,
            output_file=output_file,
            ollama_model=args.model,
            ollama_url=args.ollama_url,
            task_id=str(uuid.uuid4()),
            thread_id=str(uuid.uuid4())
        )

        # Run the summarizer
        summarizer = GitDiffSummarizer(config)
        await summarizer.run()

    except ValidationError as e:
        log.error(f"Validation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)


async def print_banner():
    cols = os.get_terminal_size().columns
    banner = pyfiglet.figlet_format("RevAI", font="slant")
    for line in banner.splitlines():
        print(line.center(cols))


if __name__ == "__main__":
    asyncio.run(main())