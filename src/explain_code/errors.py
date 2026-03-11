"""Custom error types for explain-code."""


class ExplainCodeError(Exception):
    """Base error for explain-code."""


class ConfigurationError(ExplainCodeError):
    """Raised when configuration is invalid."""


class ExtractionError(ExplainCodeError):
    """Raised when source code extraction fails."""


class FunctionNotFoundError(ExtractionError):
    """Raised when no matching function is found."""


class MultipleFunctionsFoundError(ExtractionError):
    """Raised when more than one matching function is found."""

    def __init__(self, function_name: str, candidates: list[str]) -> None:
        message = (
            f"Function '{function_name}' is ambiguous. "
            f"Found multiple matches: {', '.join(candidates)}"
        )
        super().__init__(message)
        self.function_name = function_name
        self.candidates = candidates


class OpenAIResponseError(ExplainCodeError):
    """Raised when OpenAI response cannot be parsed or is invalid."""

