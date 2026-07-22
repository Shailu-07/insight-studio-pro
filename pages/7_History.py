import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header
from config import settings
from core.session import init_session
from db import crud

st.set_page_config(page_title=f"History · {settings.app_name}", page_icon="🕘", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 7", "History", "Everything you've uploaded, analyzed, and generated — saved to MySQL.")

if not st.session_state.get("db_ready"):
    empty_state("Database is not connected.", "History requires MySQL to be reachable. Check **Settings**.")
    st.stop()

tab_datasets, tab_reports, tab_log = st.tabs(["Datasets", "Reports", "Activity Log"])

with tab_datasets:
    try:
        datasets = crud.list_datasets(limit=200)
    except Exception as exc:
        st.error(f"Could not load datasets: {exc}")
        datasets = []

    if not datasets:
        empty_state("No datasets saved yet.", "Upload and save one on the **Upload Dataset** page.")
    else:
        for ds in datasets:
            card_start()
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**#{ds.id} — {ds.filename}**")
                st.caption(
                    f"{ds.row_count:,} rows × {ds.column_count} columns · "
                    f"uploaded {ds.uploaded_at:%Y-%m-%d %H:%M}"
                )
            with col2:
                st.caption(f"Type: `{ds.file_type}`")
            with col3:
                if st.button("Delete", key=f"del_ds_{ds.id}"):
                    crud.delete_dataset(ds.id)
                    st.success("Dataset deleted.")
                    st.rerun()
            st.caption(
                "Note: re-upload the original file on **Upload Dataset** to re-run "
                "statistics or chat on its contents — only metadata is stored here."
            )
            card_end()

with tab_reports:
    try:
        reports = crud.list_reports(limit=200)
    except Exception as exc:
        st.error(f"Could not load reports: {exc}")
        reports = []

    if not reports:
        empty_state("No reports saved yet.", "Generate one from the **Reports** page.")
    else:
        titles = {r.id: f"#{r.id} — {r.title} ({r.created_at:%Y-%m-%d %H:%M})" for r in reports}
        selected_id = st.selectbox("Select a report to reopen", options=list(titles.keys()), format_func=lambda rid: titles[rid])

        if selected_id:
            report = crud.get_report(selected_id)
            card_start(report.title)
            st.caption(f"Generated {report.created_at:%Y-%m-%d %H:%M} · Model: {report.model_used}")
            for section in report.sections_json or []:
                st.markdown(f"**{section['title']}**")
                st.write(section["content"])
            card_end()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "⬇️ Markdown",
                    data=(report.markdown_content or "").encode("utf-8"),
                    file_name=f"report_{report.id}.md",
                    mime="text/markdown",
                    key=f"md_{selected_id}",
                )
            with col2:
                from services import report_service

                pdf_bytes = report_service.markdown_to_pdf_bytes(report.title, report.markdown_content or "")
                if pdf_bytes:
                    st.download_button(
                        "⬇️ PDF", data=pdf_bytes, file_name=f"report_{report.id}.pdf",
                        mime="application/pdf", key=f"pdf_{selected_id}",
                    )
                else:
                    st.caption("Install `reportlab` for PDF export.")
            with col3:
                if st.button("🗑️ Delete report", key=f"del_report_{selected_id}"):
                    crud.delete_report(selected_id)
                    st.success("Report deleted.")
                    st.rerun()

with tab_log:
    try:
        activity = crud.list_activity(limit=300)
    except Exception as exc:
        st.error(f"Could not load activity log: {exc}")
        activity = []

    if not activity:
        empty_state("No activity recorded yet.")
    else:
        for entry in activity:
            st.markdown(
                f"`{entry.created_at:%Y-%m-%d %H:%M}` **{entry.action.replace('_', ' ').title()}** — {entry.details or ''}"
            )
