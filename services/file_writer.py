from pathlib import Path

from config import Config
from loguru import logger as log


class FileWriter:
    """Handles writing output to files."""

    @staticmethod
    def write_summary(output_path: Path, summary: str, config: Config):
        """Write the summary to the output file with metadata."""
        try:
            content = FileWriter._format_output(summary, config)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            log.info(f"Summary was saved to: {output_path}")

        except IOError as e:
            raise Exception(f"Failed to write output file: {e}")

    @staticmethod
    def _format_output(summary: str, config: Config) -> str:
        """Format the output with metadata."""
        separator = "=" * 80

        return f"""# Git Branch Diff Summary

{separator}
## Configuration
{separator}

- **Project Path**: {config.project_path}
- **Local Branch**: {config.source_branch}
- **Master Branch**: {config.target_branch}
- **AI Model**: {config.model_name}
- **Generated**: {__import__('datetime').datetime.now().isoformat()}

{separator}
## Summary
{separator}

{summary}

{separator}
"""

