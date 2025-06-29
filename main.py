import argparse
from loguru import logger as log
import sys

from config import Config
from errors import ValidationError
from services.git_diff_summarizer import GitDiffSummarizer
from services.input_validator import InputValidator

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate AI-powered summaries of Git branch differences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project feature-branch main output.md
  %(prog)s ./my-project develop master summary.txt --model llama3.2
  %(prog)s ~/projects/app feature origin/main report.md --ollama-url http://localhost:11434
        """
    )

    parser.add_argument(
        "project_path",
        help="Path to the Git project directory"
    )

    parser.add_argument(
        "local_branch",
        help="Name of the local/feature branch to compare"
    )

    parser.add_argument(
        "master_branch",
        help="Name of the master/base branch to compare against",
    )

    parser.add_argument(
        "output_file",
        help="Path to the output file for the summary"
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



def main():
    """Main entry point of the application."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate inputs
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
        summarizer.run()

    except ValidationError as e:
        log.error(f"Validation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()