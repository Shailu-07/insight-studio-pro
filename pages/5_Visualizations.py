import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header
from config import settings
from core.session import get_dataset, get_dataset_name, has_dataset, init_session
from services import analytics_service, chart_service

st.set_page_config(page_title=f"Visualizations · {settings.app_name}", page_icon="📊", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 5", "Visualizations", "Pick columns to chart — no code needed.")

if not has_dataset():
    empty_state("No dataset loaded yet.", "Go to **Upload Dataset** first.")
    st.stop()

df = get_dataset()
st.markdown(f"**Active dataset:** `{get_dataset_name()}`")

numeric_cols = analytics_service.get_numeric_columns(df)
categorical_cols = analytics_service.get_categorical_columns(df)

tab_hist, tab_scatter, tab_cat = st.tabs(["Histogram", "Scatter Compare", "Category Breakdown"])

with tab_hist:
    card_start("Distribution of a numeric column", "📉")
    if not numeric_cols:
        empty_state("No numeric columns available.")
    else:
        col = st.selectbox("Column", numeric_cols, key="hist_col")
        st.plotly_chart(chart_service.histogram(df, col), use_container_width=True)
    card_end()

with tab_scatter:
    card_start("Compare two numeric columns", "🎯")
    if len(numeric_cols) < 2:
        empty_state("Need at least two numeric columns for a scatter plot.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            x_col = st.selectbox("X axis", numeric_cols, key="scatter_x")
        with col2:
            y_options = [c for c in numeric_cols if c != x_col] or numeric_cols
            y_col = st.selectbox("Y axis", y_options, key="scatter_y")
        with col3:
            color_options = ["(none)"] + categorical_cols
            color_choice = st.selectbox("Color by", color_options, key="scatter_color")
        color = None if color_choice == "(none)" else color_choice
        st.plotly_chart(chart_service.scatter(df, x_col, y_col, color), use_container_width=True)
    card_end()

with tab_cat:
    card_start("Top values in a categorical column", "🏷️")
    if not categorical_cols:
        empty_state("No categorical columns available.")
    else:
        col = st.selectbox("Column", categorical_cols, key="cat_col")
        top_n = st.slider("Show top N values", 3, 25, 10)
        counts = analytics_service.top_categories(df, col, top_n)
        st.plotly_chart(chart_service.category_bar(counts, col), use_container_width=True)
    card_end()
