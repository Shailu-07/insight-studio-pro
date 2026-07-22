from datetime import datetime

import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header
from config import settings
from core.exceptions import LLMConfigError, LLMRequestError
from core.session import (
    add_report_section,
    clear_report_sections,
    get_dataset,
    get_dataset_id,
    get_dataset_name,
    get_report_sections,
    has_dataset,
    init_session,
)
from services import analytics_service, llm_service, report_service

st.set_page_config(page_title=f"Reports · {settings.app_name}", page_icon="🧾", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 6", "Report Generator", "Generate AI insights and save a shareable report.")

if not has_dataset():
    empty_state("No dataset loaded yet.", "Go to **Upload Dataset** first.")
    st.stop()

df = get_dataset()
dataset_name = get_dataset_name()
dataset_id = get_dataset_id()

if not dataset_id:
    st.info(
        "This dataset isn't saved to the database, so the report can be "
        "generated and downloaded, but won't be saved to History. Go back "
        "to **Upload Dataset** and save it first if you want that."
    )

card_start("Generate AI Insights", "✨")
if not settings.has_valid_api_key:
    st.caption("⚠️ Set ANTHROPIC_API_KEY in your .env to enable AI generation.")

if st.button("Generate executive summary & insights", type="primary", disabled=not settings.has_valid_api_key):
   with st.spinner(f"Asking {settings.groq_model} to analyze your data..."):
        try:
            context = analytics_service.build_context_summary(df, dataset_name, settings.max_context_rows)
            insights = llm_service.generate_full_insights(context)
            clear_report_sections()
            add_report_section("Executive Summary", insights["executive_summary"])
            add_report_section("Key Trends", insights["key_trends"])
            add_report_section("Anomalies", insights["anomalies"])
            add_report_section("Recommendations", insights["recommendations"])
            st.session_state["last_executive_summary"] = insights["executive_summary"]
            st.success("Insights generated. Scroll down to review, save, and export.")
        except LLMConfigError as exc:
            st.error(f"❌ {exc}")
        except LLMRequestError as exc:
            st.error(f"❌ AI generation failed: {exc}")
        except Exception as exc:
            st.error(f"❌ Unexpected error: {exc}")
card_end()

sections = get_report_sections()
if sections:
    st.divider()
    st.markdown("### Report Preview")
    for section in sections:
        card_start(section["title"])
        st.write(section["content"])
        card_end()

    st.divider()
    title = st.text_input("Report title", value=f"{dataset_name} — Insight Report ({datetime.now():%Y-%m-%d})")

    overview = analytics_service.dataset_overview(df)
    markdown_content = report_service.build_markdown_report(dataset_name, overview, sections)

    col_save, col_export1, col_export2, col_export3 = st.columns(4)
    with col_save:
        if st.button("💾 Save report", disabled=not (dataset_id and st.session_state.get("db_ready"))):
            try:
                report_id = report_service.save_report(
                    dataset_id=dataset_id,
                    title=title,
                    model_used=settings.groq_model,
                    executive_summary=st.session_state.get("last_executive_summary", ""),
                    sections=sections,
                    markdown_content=markdown_content,
                )
                st.success(f"Saved as report #{report_id}. Find it anytime in **History**.")
            except Exception as exc:
                st.error(f"Could not save the report: {exc}")
    with col_export1:
        st.download_button(
            "⬇️ Markdown",
            data=markdown_content.encode("utf-8"),
            file_name=f"{title.replace(' ', '_')}.md",
            mime="text/markdown",
        )
    with col_export2:
        st.download_button(
            "⬇️ Cleaned CSV",
            data=report_service.dataframe_to_csv_bytes(df),
            file_name=f"{dataset_name.rsplit('.', 1)[0]}_cleaned.csv",
            mime="text/csv",
        )
    with col_export3:
        pdf_bytes = report_service.markdown_to_pdf_bytes(title, markdown_content)
        if pdf_bytes:
            st.download_button(
                "⬇️ PDF",
                data=pdf_bytes,
                file_name=f"{title.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )
        else:
            st.caption("Install `reportlab` for PDF export.")
else:
    empty_state(
        "No report generated yet.",
        "Click **Generate executive summary & insights** above to get started.",
    )
