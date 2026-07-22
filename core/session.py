"""Centralized Streamlit session_state management.

All reads/writes to `st.session_state` go through here so key names and
defaults live in one place. Unlike a purely in-memory app, this module
also mirrors chat messages to MySQL (via `db.crud`) so a dataset's chat
history survives a page refresh or a later revisit from History.
"""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

_DEFAULTS = {
    "dataset": None,           # pd.DataFrame | None
    "dataset_name": None,      # str | None
    "dataset_id": None,        # int | None — primary key in `datasets` table
    "chat_history": [],        # list[dict] — mirrored to DB per dataset
    "analysis_cache": {},      # dict, keyed by cache key
    "report_sections": [],     # list[dict] accumulated for the Reports page
    "db_ready": False,
    "db_error": None,
}


def init_session() -> None:
    """Populate any missing session_state keys with their defaults. Call once per run."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default() if callable(default) else default


def set_dataset(df: pd.DataFrame, name: str, dataset_id: Optional[int] = None) -> None:
    st.session_state["dataset"] = df
    st.session_state["dataset_name"] = name
    st.session_state["dataset_id"] = dataset_id
    # A new dataset invalidates any cached analysis and prior chat context.
    st.session_state["analysis_cache"] = {}
    st.session_state["report_sections"] = []
    st.session_state["chat_history"] = []
    if dataset_id is not None:
        _load_chat_history(dataset_id)


def get_dataset() -> Optional[pd.DataFrame]:
    return st.session_state.get("dataset")


def has_dataset() -> bool:
    df = get_dataset()
    return df is not None and not df.empty


def get_dataset_name() -> str:
    return st.session_state.get("dataset_name") or "Untitled dataset"


def get_dataset_id() -> Optional[int]:
    return st.session_state.get("dataset_id")


def append_chat_message(role: str, content: str, persist: bool = True) -> None:
    st.session_state["chat_history"].append({"role": role, "content": content})
    dataset_id = get_dataset_id()
    if persist and dataset_id is not None and st.session_state.get("db_ready"):
        from db import crud  # local import avoids a hard dependency at module load time

        try:
            crud.add_chat_message(dataset_id, role, content)
        except Exception:
            # Chat still works even if a single message fails to persist.
            pass


def get_chat_history() -> list[dict]:
    return st.session_state.get("chat_history", [])


def _load_chat_history(dataset_id: int) -> None:
    if not st.session_state.get("db_ready"):
        return
    from db import crud

    try:
        messages = crud.list_chat_messages(dataset_id)
        st.session_state["chat_history"] = [
            {"role": m.role, "content": m.content} for m in messages
        ]
    except Exception:
        st.session_state["chat_history"] = []


def cache_analysis(key: str, value: Any) -> None:
    st.session_state["analysis_cache"][key] = value


def get_cached_analysis(key: str) -> Any:
    return st.session_state.get("analysis_cache", {}).get(key)


def add_report_section(title: str, content: str) -> None:
    st.session_state["report_sections"].append({"title": title, "content": content})


def get_report_sections() -> list[dict]:
    return st.session_state.get("report_sections", [])


def clear_report_sections() -> None:
    st.session_state["report_sections"] = []
