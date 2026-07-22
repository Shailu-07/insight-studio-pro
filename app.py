"""AI Insight Studio — entry point.

Run with:
    streamlit run app.py

This file wires up page config, global init (DB + session state), and the
Home screen. All business logic lives in `services/` and `db/`; all
page-specific UI lives in `pages/`. This file should never grow business
logic of its own.
"""
import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, inject_global_styles, page_header, stat_row
from config import settings
from core.session import has_dataset, init_session
from db.engine import DatabaseConnectionError, init_db

st.set_page_config(
    page_title=settings.app_name,
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
inject_global_styles()


def _ensure_database() -> None:
    if st.session_state.get("db_ready"):
        return
    try:
        init_db()
        st.session_state["db_ready"] = True
        st.session_state["db_error"] = None
    except DatabaseConnectionError as exc:
        st.session_state["db_ready"] = False
        st.session_state["db_error"] = str(exc)


_ensure_database()
render_sidebar()

page_header(
    eyebrow="Overview",
    title="AI Insight Studio",
    subtitle="Upload a dataset, explore it, ask questions in plain English, "
    "and save everything to your own database.",
)

if st.session_state.get("db_error"):
    st.error("⚠️ Could not connect to MySQL. Datasets and reports won't be saved until this is fixed.")
    st.code(st.session_state["db_error"])
    st.caption("Open **Settings** for connection details, or check your `.env` file's MYSQL_* variables.")

if st.session_state.get("db_ready"):
    from db import crud

    try:
        counts = crud.get_dashboard_counts()
        card_start("At a glance", "📊")
        stat_row(
            [
                ("Datasets", counts["datasets"]),
                ("Analyses", counts["analyses"]),
                ("Reports", counts["reports"]),
                ("Chat Messages", counts["chat_messages"]),
            ]
        )
        card_end()
    except Exception as exc:
        st.warning(f"Could not load dashboard metrics: {exc}")

card_start("How it works", "🧭")
stat_row(
    [
        ("Step 1", "Upload"),
        ("Step 2", "Preview"),
        ("Step 3", "Ask AI"),
        ("Step 4", "Report"),
    ]
)
st.markdown(
    "Use the sidebar to move through the workflow: **Upload Dataset** to bring in a "
    "CSV or Excel file, **Data Preview** to inspect it, **AI Chat** to ask questions "
    "about it in plain language, **Analysis** and **Visualizations** to explore it "
    "statistically, **Reports** to save and export what you've found, and **History** "
    "to revisit anything you've generated before — everything is saved to MySQL."
)
card_end()

if not has_dataset():
    card_start("Get started", "🚀")
    st.markdown("You don't have a dataset loaded yet. Head to **Upload Dataset** in the sidebar to get started.")
    if st.button("Go to Upload Dataset →", type="primary"):
        st.switch_page("pages/1_Upload_Dataset.py")
    card_end()
else:
    card_start("Ready to go", "✅")
    st.markdown("Your dataset is loaded. Jump straight to **AI Chat** to start asking questions, or **Analysis** for statistics and charts.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Open AI Chat →", type="primary"):
            st.switch_page("pages/3_AI_Chat.py")
    with col2:
        if st.button("Open Analysis →"):
            st.switch_page("pages/4_Analysis.py")
    card_end()
