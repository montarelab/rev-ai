import json

import requests
from langchain_ollama import ChatOllama

from errors import OllamaError
from loguru import logger as log


class DiffSummarizerClient:
    """Handles communication with Ollama for AI summarization."""

    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    async def summarize_diff(self, diff_content: str) -> str:
        """Send diff to Ollama for summarization."""
        if not diff_content or diff_content.strip() == "No differences found between the specified branches.":
            return diff_content

        prompt = self._create_summary_prompt(diff_content)

        try:
            log.info(f"Requesting summary from Ollama using model: {self.model}")

            chat = ChatOllama(
                model=self.model,
                base_url=self.url,
                temperature=0.1,
                timeout=300,
                num_predict=2048,
                prompt=prompt
            )

            response = await chat.ainvoke(prompt)

            return response.content.strip()

        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Failed to communicate with Ollama: {e}")
        except json.JSONDecodeError as e:
            raise OllamaError(f"Failed to parse Ollama response: {e}")

    @staticmethod
    def _create_summary_prompt(diff_content: str) -> str:
        """Create a comprehensive prompt for diff summarization."""
        return f"""Please analyze the following Git diff and provide a comprehensive summary of the changes.

Focus on:
1. **Overview**: Brief description of what changed
2. **Files Modified**: List of files that were changed
3. **Key Changes**: Most important modifications
4. **Functionality Impact**: How these changes affect the codebase
5. **Potential Concerns**: Any issues or improvements to note

Please be concise but thorough, and format your response in a clear, readable manner.

Git Diff:
```
{diff_content}
```

Summary:"""


