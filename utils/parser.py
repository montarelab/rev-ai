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
  %(prog)s ./my-project develop master summary.txt --model gpt-4.1-mini
  %(prog)s ~/projects/app feature origin/main report.md 

        """
    )

    parser.add_argument(
        "--project_path", "-p",
        dest="project_path",
        nargs='?',
        help="Path to the Git project directory (required for direct diff analysis)"
    )

    parser.add_argument(
        "--source_branch", "-s",
        dest="source_branch",
        nargs='?',
        help="Name of the local/feature branch to compare (required for diff analysis)"
    )

    parser.add_argument(
        "--target_branch", "-t",
        dest="target_branch",
        nargs='?',
        help="Name of the master/base branch to compare against (required for diff analysis)",
    )

    parser.add_argument(
        "--output_file", "-o",
        dest="output_file",
        nargs='?',
        help="Path to the output file for the summary (required for diff analysis)"
    )

    parser.add_argument(
        "--model", "-m",
        dest="model",
        default="gpt-4.1-mini",
        nargs="?",
        help="AI model to use for summarization and analysis (default: gpt-4.1-mini)"
    )

    parser.add_argument(
        "--embedding_model", "-e",
        dest="embedding_model",
        default="text-embedding-3-small",
        nargs="?",
        help="AI model to embedd strings (default: text-embedding-3-small)"
    )

    parser.add_argument(
        "--api_key", "-k",
        dest="api_key",
        default="",
        nargs="?",
        help="API key for OpenAI model (default: None)"
    )

    return parser
