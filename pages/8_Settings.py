import streamlit as st

from components.sidebar import render_sidebar
from components.ui import card_end, card_start, inject_global_styles, section_header
from config import settings
from core.exceptions import DatabaseConnectionError
from core.session import init_session
from db.engine import check_connection, init_db

st.set_page_config(page_title=f"Settings · {settings.app_name}", page_icon="⚙️", layout="wide")
init_session()
inject_global_styles()
render_sidebar()
section_header("Step 8", "Settings", "Review your current configuration and connection status.")

card_start("Database (MySQL)", "🗄️")
st.write(f"**Host:** `{settings.mysql_host}`")
st.write(f"**Port:** `{settings.mysql_port}`")
st.write(f"**Database name:** `{settings.mysql_database}`")
st.write(f"**User:** `{settings.mysql_user}`")

if check_connection():
    st.success("✅ Connected to MySQL")
else:
    st.error("❌ Not connected to MySQL")
    st.caption(
        "Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD and "
        "MYSQL_DATABASE in your `.env` file, then retry below."
    )

if st.button("🔄 Retry connection / initialize tables"):
    try:
        init_db()
        st.session_state["db_ready"] = True
        st.session_state["db_error"] = None
        st.success("Database connected and tables verified.")
    except DatabaseConnectionError as exc:
        st.session_state["db_ready"] = False
        st.session_state["db_error"] = str(exc)
        st.error(str(exc))
card_end()

# card_start("Anthropic AI", "🤖")
# st.write(f"**Model:** `{settings.groq_model}`")
# # st.write(f"**Model:** `{settings.anthropic_model}`")
# # st.write(f"**Max tokens per response:** `{settings.anthropic_max_tokens}`")

# st.write(f"**Timeout (seconds):** `{settings.anthropic_timeout_seconds}`")
# st.write(f"**Max context rows sent to AI:** `{settings.max_context_rows}`")
# if settings.has_valid_api_key:
#     masked = settings.anthropic_api_key[:6] + "…" + settings.anthropic_api_key[-4:]
#     st.success(f"✅ API key detected ({masked})")
# else:
#     st.error("❌ ANTHROPIC_API_KEY is not set")
#     st.caption("Add ANTHROPIC_API_KEY=sk-ant-... to your `.env` file and restart the app.")
# card_end()

# card_start("App", "⚙️")
# st.write(f"**App name:** `{settings.app_name}`")
# st.write(f"**Environment:** `{settings.app_env}`")
# st.write(f"**Max upload size:** `{settings.max_upload_size_mb} MB`")
# st.write(f"**Supported file types:** `{', '.join(settings.supported_file_types)}`")
# card_end()
card_start("Groq AI", "🤖")

st.write(f"**Model:** `{settings.groq_model}`")

# Remove this if it no longer exists in settings.py
# st.write(f"**Timeout (seconds):** `{settings.anthropic_timeout_seconds}`")

st.write(f"**Max context rows sent to AI:** `{settings.max_context_rows}`")

if settings.has_valid_api_key:
    masked = settings.groq_api_key[:6] + "…" + settings.groq_api_key[-4:]
    st.success(f"✅ API key detected ({masked})")
else:
    st.error("❌ GROQ_API_KEY is not set")
    st.caption("Add GROQ_API_KEY=gsk_... to your `.env` file and restart the app.")

card_end()

st.markdown("### How to change settings")
st.markdown(
    """
All settings are environment-variable driven (copy `.env.example` to `.env`
if you haven't already). Restart the app after changing `.env`:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=insight_studio

# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-sonnet-5
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```
    """
)
