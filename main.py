import asyncio
import os
import sys
import uuid
from pathlib import Path

import pyfiglet
from loguru import logger as log

from config import Config
from utils.errors import ValidationError
from services.code_diff_analyzer import CodeDiffAnalyzer
from services.input_validator import InputValidator
from utils.parser import create_parser

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
            parser.error(
                "project_path, source_branch, target_branch, and output_file are required for direct diff analysis mode.")

        log.info("Validating inputs...")
        project_path = InputValidator.validate_project_path(args.project_path)
        output_file = InputValidator.validate_output_file(args.output_file)
        source_branch = InputValidator.validate_branch_name(args.source_branch)
        target_branch = InputValidator.validate_branch_name(args.target_branch)

        # Create configuration

        api_key = args.api_key
        if not api_key:
            env_key = os.getenv("OPENAI_API_KEY")
            if not env_key:
                raise ValidationError("API key is required. Set it using --api_key or the OPENAI_API_KEY environment variable.")

            api_key = env_key

        vector_db_path = Path('knowledge_db').resolve()
        if not vector_db_path.exists():
            raise ValidationError(f"Vector DB path does not exist: {vector_db_path}")

        config = Config(
            project_path=project_path,
            source_branch=source_branch,
            target_branch=target_branch,
            output_file=output_file,
            task_id=str(uuid.uuid4()),
            thread_id=str(uuid.uuid4()),
            model_name=args.model,
            embedding_model=args.embedding_model,
            api_key=api_key,
            vector_db_path=str(vector_db_path),
            vector_db_collection_name="knowledge_base"
        )

        # Run the summarizer
        summarizer = CodeDiffAnalyzer(config)
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
