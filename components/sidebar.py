"""Sidebar branding, navigation hints, and live connection status."""
from __future__ import annotations

import streamlit as st

from config import settings
from core.session import get_dataset_name, has_dataset
from db.engine import check_connection


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.2rem;">
                <span style="font-size:1.5rem;">✦</span>
                <span style="font-size:1.15rem;font-weight:800;">{settings.app_name}</span>
            </div>
            <div style="opacity:0.7;font-size:0.85rem;margin-bottom:0.9rem;">
                Upload → Preview → Ask AI → Analyze → Report
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        if has_dataset():
            st.markdown(f"**Active dataset**  \n{get_dataset_name()}")
        else:
            st.caption("No dataset loaded yet.")

        st.divider()

        db_ok = check_connection()
        ai_ok = settings.has_valid_api_key
        st.markdown(
            f"MySQL &nbsp; {'🟢 Connected' if db_ok else '🔴 Offline'}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"Claude AI &nbsp; {'🟢 Configured' if ai_ok else '🟡 No API key'}",
            unsafe_allow_html=True,
        )

        st.divider()
        st.caption(
            "Navigate using the pages above: Upload Dataset, Data Preview, "
            "AI Chat, Analysis, Visualizations, Reports, History, Settings."
        )
