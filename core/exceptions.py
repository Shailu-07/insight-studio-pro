"""Typed exceptions so callers can catch precisely what they expect,
instead of a bare `Exception`.
"""


class AppError(Exception):
    """Base class for all application-raised errors."""


# --- Data / upload errors -------------------------------------------------

class FileValidationError(AppError):
    """The uploaded file failed a basic validation check."""


class UnsupportedFormatError(FileValidationError):
    """The uploaded file's extension isn't supported."""


class EmptyDatasetError(FileValidationError):
    """The uploaded file parsed but contains no usable data."""


class MissingColumnError(AppError):
    """A requested column does not exist in the current dataset."""


# --- AI / LLM errors --------------------------------------------------------

class LLMConfigError(AppError):
    """The AI provider isn't configured correctly (e.g. missing API key)."""


class LLMRequestError(AppError):
    """The AI request failed (network, timeout, malformed response, etc.)."""


# --- Database errors ---------------------------------------------------------

class DatabaseConnectionError(AppError):
    """The app could not connect to MySQL."""
