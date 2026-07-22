import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header, stat_row
from config import settings
from core.session import get_dataset, get_dataset_name, has_dataset, init_session
from services import analytics_service, chart_service, data_service

st.set_page_config(page_title=f"Data Preview · {settings.app_name}", page_icon="🔍", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 2", "Data Preview", "Inspect columns, types, and missing values.")

if not has_dataset():
    empty_state("No dataset loaded yet.", "Go to **Upload Dataset** first.")
    st.stop()

df = get_dataset()
overview = analytics_service.dataset_overview(df)

st.markdown(f"**Active dataset:** `{get_dataset_name()}`")

card_start("Overview", "📐")
stat_row(
    [
        ("Rows", f"{overview['rows']:,}"),
        ("Columns", overview["columns"]),
        ("Missing Cells", f"{overview['missing_cells']:,} ({overview['missing_pct']}%)"),
        ("Duplicate Rows", f"{overview['duplicate_rows']:,}"),
    ]
)
card_end()

st.dataframe(df.head(100), use_container_width=True)

tab_cols, tab_missing, tab_raw = st.tabs(["Columns & Types", "Missing Values", "Raw Sample"])

with tab_cols:
    summary = data_service.get_column_summary(df)
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

with tab_missing:
    missing = analytics_service.missing_values(df)
    total_missing = sum(missing.values())
    if total_missing == 0:
        st.success("No missing values detected. 🎉")
    else:
        fig = chart_service.missing_values_bar(missing)
        st.plotly_chart(fig, use_container_width=True)

with tab_raw:
    st.dataframe(df.tail(50), use_container_width=True)
