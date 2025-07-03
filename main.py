import argparse
import asyncio
import os
import sys

import pyfiglet
from loguru import logger as log

from config import Config
from errors import ValidationError
from services.git_diff_summarizer import GitDiffSummarizer
from services.input_validator import InputValidator
from services.git_chat import GitDiffChat
from dotenv import load_dotenv

load_dotenv()

log.remove()

logs_dir = os.getenv("LOGS_DIR")
os.makedirs(logs_dir, exist_ok=True)
log.add(f"{logs_dir}/app.log", rotation="1 MB", retention="10 days", level="DEBUG")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="AI-powered Git diff analysis with direct and interactive modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Direct Git Diff Analysis:
  %(prog)s /path/to/project feature-branch main output.md
  %(prog)s ./my-project develop master summary.txt --model llama3.2
  %(prog)s ~/projects/app feature origin/main report.md --ollama-url http://localhost:11434

  # Interactive Chat Mode:
  %(prog)s --interactive
  %(prog)s --interactive --model llama3.2 --ollama-url http://localhost:11434
        """
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive mode for guided git diff analysis"
    )

    parser.add_argument(
        "project_path",
        nargs='?',
        help="Path to the Git project directory (required for direct diff analysis)"
    )

    parser.add_argument(
        "local_branch",
        nargs='?',
        help="Name of the local/feature branch to compare (required for diff analysis)"
    )

    parser.add_argument(
        "master_branch",
        nargs='?',
        help="Name of the master/base branch to compare against (required for diff analysis)",
    )

    parser.add_argument(
        "output_file",
        nargs='?',
        help="Path to the output file for the summary (required for diff analysis)"
    )

    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model to use for summarization (default: llama3.2)"
    )

    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser



async def main():
    """Main entry point of the application."""
    await print_banner()

    parser = create_parser()
    args = parser.parse_args()

    # Verbose mode
    if args.verbose:
        print("Verbose mode enabled")
        log.add(sys.stderr, level="INFO",
                   format="<green>{time:HH:mm:ss}</green> | <level>{level}</level>: <level>{message}</level>")

    try:
        # Check if interactive mode is requested
        if args.interactive:
            log.info("Starting interactive chat mode...")
            chat = GitDiffChat(model=args.model, ollama_url=args.ollama_url)
            await chat.start_interactive_session()
            return

        # Validate required arguments for diff analysis mode
        if not all([args.project_path, args.local_branch, args.master_branch, args.output_file]):
            parser.error("project_path, local_branch, master_branch, and output_file are required for direct diff analysis mode. Use --interactive for guided mode.")

        # Validate inputs for diff analysis
        log.info("Validating inputs...")
        InputValidator.check_git_availability()
        InputValidator.check_ollama_availability(args.ollama_url)

        project_path = InputValidator.validate_project_path(args.project_path)
        output_file = InputValidator.validate_output_file(args.output_file)
        local_branch = InputValidator.validate_branch_name(args.local_branch)
        master_branch = InputValidator.validate_branch_name(args.master_branch)

        # Create configuration
        config = Config(
            project_path=project_path,
            local_branch=local_branch,
            master_branch=master_branch,
            output_file=output_file,
            ollama_model=args.model,
            ollama_url=args.ollama_url
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