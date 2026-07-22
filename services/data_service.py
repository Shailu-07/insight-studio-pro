"""File loading and validation logic.

Kept fully independent of Streamlit so it can be unit tested without a
running app, and reused from any future entry point (CLI, API, etc.).
"""
from __future__ import annotations

import hashlib
import io

import pandas as pd

from config import settings
from core.exceptions import EmptyDatasetError, FileValidationError, UnsupportedFormatError


def validate_file(filename: str, size_bytes: int) -> None:
    """Raise a descriptive error if the file fails basic checks."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in settings.supported_file_types:
        supported = ", ".join(settings.supported_file_types)
        raise UnsupportedFormatError(
            f"'.{extension}' files aren't supported. Please upload one of: {supported}."
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileValidationError(
            f"File is too large ({size_bytes / (1024 * 1024):.1f} MB). "
            f"Max allowed is {settings.max_upload_size_mb} MB."
        )

    if size_bytes == 0:
        raise FileValidationError("The uploaded file is empty.")


def load_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse raw file bytes into a DataFrame based on the file extension."""
    lower_name = filename.lower()
    buffer = io.BytesIO(file_bytes)

    try:
        if lower_name.endswith(".csv"):
            df = pd.read_csv(buffer)
        elif lower_name.endswith(".tsv"):
            df = pd.read_csv(buffer, sep="\t")
        elif lower_name.endswith((".xlsx", ".xlsm")):
            df = pd.read_excel(buffer, engine="openpyxl")
        elif lower_name.endswith(".xls"):
            df = pd.read_excel(buffer)
        else:
            raise UnsupportedFormatError(f"Unsupported file type for '{filename}'.")
    except UnsupportedFormatError:
        raise
    except Exception as exc:
        raise FileValidationError(f"Could not parse '{filename}': {exc}") from exc

    if df.empty or df.shape[1] == 0:
        raise EmptyDatasetError(f"'{filename}' was parsed but contains no usable rows or columns.")

    df.columns = [str(c).strip() for c in df.columns]
    return df


def file_hash(file_bytes: bytes) -> str:
    """A stable hash used to detect re-uploads of the same file content."""
    return hashlib.sha256(file_bytes).hexdigest()


def infer_file_type(filename: str) -> str:
    lower_name = filename.lower()
    for ext in settings.supported_file_types:
        if lower_name.endswith(f".{ext}"):
            return ext
    return "unknown"


def get_column_summary(df: pd.DataFrame) -> list[dict]:
    """Per-column type + missing-value summary used by Data Preview."""
    total_rows = len(df)
    summary = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        summary.append(
            {
                "column": col,
                "dtype": str(df[col].dtype),
                "missing_count": missing,
                "missing_pct": round(missing / total_rows * 100, 2) if total_rows else 0.0,
                "unique_values": int(df[col].nunique()),
            }
        )
    return summary
