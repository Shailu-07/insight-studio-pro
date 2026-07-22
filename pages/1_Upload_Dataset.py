import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, empty_state, inject_global_styles, section_header
from config import settings
from core.exceptions import FileValidationError
from core.session import init_session, set_dataset
from db import crud
from services import data_service

st.set_page_config(page_title=f"Upload Dataset · {settings.app_name}", page_icon="📤", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 1", "Upload Dataset", "Bring in a CSV or Excel file to begin.")

if not st.session_state.get("db_ready"):
    st.warning(
        "Database is not connected — you can still preview a file, but it "
        "won't be saved. Check the **Settings** page."
    )

uploaded_file = st.file_uploader(
    "Choose a CSV, TSV, or Excel file",
    type=list(settings.supported_file_types),
    help=f"Maximum file size: {settings.max_upload_size_mb} MB",
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()

    try:
        data_service.validate_file(uploaded_file.name, len(file_bytes))
        df = data_service.load_dataframe(file_bytes, uploaded_file.name)
    except FileValidationError as exc:
        st.error(f"❌ {exc}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected error while reading the file: {exc}")
        st.stop()

    st.success(f"✅ Parsed **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")

    card_start("Preview", "👀")
    st.dataframe(df.head(20), use_container_width=True)
    card_end()

    save_disabled = not st.session_state.get("db_ready")
    if st.button("💾 Save to database & set as active dataset", type="primary", disabled=save_disabled):
        with st.spinner("Saving..."):
            try:
                file_hash = data_service.file_hash(file_bytes)
                existing = crud.find_dataset_by_hash(file_hash)

                columns_json = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
                dataset_id = crud.create_dataset(
                    filename=uploaded_file.name,
                    file_type=data_service.infer_file_type(uploaded_file.name),
                    row_count=int(df.shape[0]),
                    column_count=int(df.shape[1]),
                    columns_json=columns_json,
                    file_hash=file_hash,
                )
                set_dataset(df, uploaded_file.name, dataset_id)

                if existing:
                    st.info(
                        f"Note: identical content was previously uploaded as "
                        f"'{existing.filename}' (dataset #{existing.id}). A new "
                        f"entry (#{dataset_id}) was still created for this upload."
                    )
                st.success(f"Saved as dataset #{dataset_id}. It's now your active dataset.")
            except Exception as exc:
                st.error(f"Could not save the dataset: {exc}")
    elif save_disabled:
        # Even without a DB, let the user work with the file in-session.
        if st.button("Use this dataset without saving"):
            set_dataset(df, uploaded_file.name, None)
            st.success("Dataset is active for this session (not saved to the database).")

else:
    empty_state(
        "No file uploaded yet.",
        f"Supported formats: {', '.join(settings.supported_file_types)}. "
        f"Max size: {settings.max_upload_size_mb} MB.",
    )
