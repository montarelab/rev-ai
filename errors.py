class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class GitError(Exception):
    """Raised when Git operations fail."""
    pass


class OllamaError(Exception):
    """Raised when Ollama operations fail."""
    pass
