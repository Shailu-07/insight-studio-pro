"""Small, framework-independent helper functions used across the app."""
from __future__ import annotations


def format_bytes(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def format_number(value: int | float) -> str:
    return f"{value:,}"


def truncate(text: str, max_len: int = 120) -> str:
    text = text or ""
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"
