import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="AI-powered Git diff analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Direct Git Diff Analysis:
  %(prog)s /path/to/project feature-branch main output.md
  %(prog)s ./my-project develop master summary.txt --model llama3.2
  %(prog)s ~/projects/app feature origin/main report.md --ollama-url http://localhost:11434

        """
    )

    parser.add_argument(
        "project_path",
        nargs='?',
        help="Path to the Git project directory (required for direct diff analysis)"
    )

    parser.add_argument(
        "source_branch",
        nargs='?',
        help="Name of the local/feature branch to compare (required for diff analysis)"
    )

    parser.add_argument(
        "target_branch",
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

    return parser
