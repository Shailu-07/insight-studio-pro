import streamlit as st

from components.sidebar import render_sidebar
from components.ui import chat_bubble, empty_state, inject_global_styles, section_header
from config import settings
from core.exceptions import LLMConfigError, LLMRequestError
from core.session import append_chat_message, get_chat_history, get_dataset, get_dataset_name, has_dataset, init_session
from services import analytics_service, llm_service

st.set_page_config(page_title=f"AI Chat · {settings.app_name}", page_icon="💬", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 3", "AI Chat", "Ask questions about your dataset in plain English.")

if not has_dataset():
    empty_state("No dataset loaded yet.", "Go to **Upload Dataset** first.")
    st.stop()

df = get_dataset()
dataset_name = get_dataset_name()

if not settings.has_valid_api_key:
    st.warning(
        "⚠️ ANTHROPIC_API_KEY is not set. Add it to your `.env` file to enable "
        "AI Chat. See **Settings** for details."
    )

st.markdown(f"**Active dataset:** `{dataset_name}`")
if not st.session_state.get("dataset_id"):
    st.caption("This dataset isn't saved to the database, so chat history won't persist after this session.")

st.divider()

history = get_chat_history()
if not history:
    st.caption("No messages yet — ask something like *\"What's the average of column X?\"* or *\"Any obvious outliers?\"*")
else:
    for turn in history:
        chat_bubble(turn["role"], turn["content"])

question = st.chat_input("Ask a question about your data...", disabled=not settings.has_valid_api_key)

if question:
    append_chat_message("user", question)
    with st.spinner("Thinking..."):
        try:
            context = analytics_service.build_context_summary(df, dataset_name, settings.max_context_rows)
            answer = llm_service.ask(question, context, chat_history=get_chat_history()[:-1])
            append_chat_message("assistant", answer)
        except LLMConfigError as exc:
            append_chat_message("assistant", f"⚠️ {exc}", persist=False)
        except LLMRequestError as exc:
            append_chat_message("assistant", f"❌ {exc}", persist=False)
        except Exception as exc:
            append_chat_message("assistant", f"❌ Unexpected error: {exc}", persist=False)
    st.rerun()
