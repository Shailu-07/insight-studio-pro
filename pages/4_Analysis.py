import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header
from config import settings
from core.session import get_dataset, get_dataset_id, get_dataset_name, has_dataset, init_session
from db import crud
from services import analytics_service, chart_service

st.set_page_config(page_title=f"Analysis · {settings.app_name}", page_icon="📈", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 4", "Analysis", "Descriptive statistics and correlations.")

if not has_dataset():
    empty_state("No dataset loaded yet.", "Go to **Upload Dataset** first.")
    st.stop()

df = get_dataset()
st.markdown(f"**Active dataset:** `{get_dataset_name()}`")

card_start("Descriptive Statistics", "🧮")
numeric_stats = analytics_service.describe_numeric(df)
if not numeric_stats:
    empty_state("No numeric columns to summarize.")
else:
    st.dataframe(pd.DataFrame(numeric_stats), use_container_width=True)
card_end()

card_start("Correlation Matrix", "🔗")
corr = analytics_service.correlation_matrix(df)
if not corr:
    empty_state("Need at least two numeric columns for a correlation matrix.")
else:
    fig = chart_service.correlation_heatmap(corr)
    st.plotly_chart(fig, use_container_width=True)
card_end()

card_start("Category Breakdown", "🏷️")
cat_cols = analytics_service.get_categorical_columns(df)
if not cat_cols:
    empty_state("No categorical columns available.")
else:
    chosen = st.selectbox("Column", cat_cols)
    counts = analytics_service.top_categories(df, chosen)
    st.dataframe(
        pd.DataFrame({"value": list(counts.keys()), "count": list(counts.values())}),
        use_container_width=True,
        hide_index=True,
    )
card_end()

if st.session_state.get("db_ready") and get_dataset_id():
    if st.button("💾 Save this analysis snapshot to the database"):
        try:
            overview = analytics_service.dataset_overview(df)
            crud.create_analysis(
                dataset_id=get_dataset_id(),
                overview_json=overview,
                summary_stats_json=numeric_stats,
                missing_values_json=analytics_service.missing_values(df),
                correlation_json=corr,
            )
            st.success("Analysis snapshot saved.")
        except Exception as exc:
            st.error(f"Could not save analysis: {exc}")
