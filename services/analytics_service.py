"""Statistics and analytics — pure pandas/numpy, no AI calls, no Streamlit.

Always available even if the database or the AI provider is unreachable.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from core.exceptions import MissingColumnError


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude=[np.number, "datetime64[ns]"]).columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()


def dataset_overview(df: pd.DataFrame) -> dict[str, Any]:
    missing_cells = int(df.isna().sum().sum())
    total_cells = df.shape[0] * df.shape[1] if df.shape[1] else 0
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_cells": missing_cells,
        "missing_pct": round(missing_cells / total_cells * 100, 2) if total_cells else 0.0,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": len(get_numeric_columns(df)),
        "categorical_columns": len(get_categorical_columns(df)),
    }


def describe_numeric(df: pd.DataFrame) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return {}
    return _clean_for_json(numeric_df.describe().to_dict())


def correlation_matrix(df: pd.DataFrame) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {}
    return _clean_for_json(numeric_df.corr(numeric_only=True).round(4).to_dict())


def top_categories(df: pd.DataFrame, column: str, top_n: int = 10) -> dict[str, int]:
    if column not in df.columns:
        raise MissingColumnError(f"Column '{column}' does not exist in the current dataset.")
    return df[column].astype(str).value_counts().head(top_n).to_dict()


def missing_values(df: pd.DataFrame) -> dict[str, int]:
    return {col: int(df[col].isna().sum()) for col in df.columns}


def dtypes_summary(df: pd.DataFrame) -> dict[str, str]:
    return {col: str(df[col].dtype) for col in df.columns}


def build_context_summary(df: pd.DataFrame, dataset_name: str, max_rows: int = 50) -> str:
    """A compact textual summary of the dataset for use as LLM context."""
    overview = dataset_overview(df)
    numeric_cols = get_numeric_columns(df)
    lines = [
        f"Dataset: {dataset_name}",
        f"Shape: {overview['rows']} rows x {overview['columns']} columns",
        f"Missing cells: {overview['missing_cells']} ({overview['missing_pct']}%)",
        f"Duplicate rows: {overview['duplicate_rows']}",
        "",
        "Columns (name: dtype, missing):",
    ]
    for col in df.columns:
        missing = int(df[col].isna().sum())
        lines.append(f"  - {col}: {df[col].dtype} ({missing} missing)")

    if numeric_cols:
        lines.append("")
        lines.append("Numeric summary (mean / std / min / max):")
        desc = df[numeric_cols].describe()
        for col in numeric_cols:
            lines.append(
                f"  - {col}: mean={desc.at['mean', col]:.2f}, std={desc.at['std', col]:.2f}, "
                f"min={desc.at['min', col]:.2f}, max={desc.at['max', col]:.2f}"
            )

    lines.append("")
    lines.append(f"Sample rows (first {min(5, len(df))}):")
    lines.append(df.head(5).to_csv(index=False))

    text = "\n".join(lines)
    row_cap = min(max_rows, len(df))
    if row_cap < len(df):
        text += f"\n(Context truncated to a {row_cap}-row sample of {len(df)} total rows.)"
    return text


def _clean_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _clean_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_for_json(v) for v in value]
    if isinstance(value, (np.floating, float)):
        f = float(value)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 4)
    if isinstance(value, np.integer):
        return int(value)
    return value
