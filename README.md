# AI Insight Studio

Upload a dataset, explore it visually, chat with Claude about it in plain
English, and save every dataset, analysis, chat, and report to your own
MySQL database — all in one polished Streamlit app.

This is a merged, upgraded build: clean layered architecture and a real
test suite, **plus** full MySQL persistence and Anthropic-powered AI, with
a redesigned, more attractive UI on top.

## Features

- **Upload Dataset** — CSV/TSV/Excel upload with format, size, and content validation.
- **Data Preview** — row preview, per-column type/missing-value summary, missing-values chart.
- **AI Chat** — ask questions about your data in natural language (powered by Claude). Conversations are saved per dataset, so you can pick up where you left off.
- **Analysis** — descriptive statistics and a correlation heatmap; save a snapshot to the database.
- **Visualizations** — histograms, scatter comparisons, and category breakdowns, all user-driven.
- **Reports** — generate an AI executive summary + trends/anomalies/recommendations, save it, and export as Markdown, PDF, or the cleaned CSV.
- **History** — every dataset, report, and activity event is stored in MySQL and browsable/reopenable anytime.
- **Settings** — live MySQL and Anthropic connection status, with a one-click retry.
- **Automatic MySQL setup** — the database and every table are created automatically on first run.
- **Real test suite** — `pytest` tests for the data, analytics, and database layers.
- **Premium UI** — gradient hero header, card-based layout, chat bubbles, and a consistent indigo/violet theme.

## Folder Structure

```
ai_insight_studio/
├── app.py                     # Entry point (streamlit run app.py) — Home screen only
├── run.py                     # Optional convenience launcher
├── pages/                     # One file per page — presentation only, no business logic
│   ├── 1_Upload_Dataset.py
│   ├── 2_Data_Preview.py
│   ├── 3_AI_Chat.py
│   ├── 4_Analysis.py
│   ├── 5_Visualizations.py
│   ├── 6_Reports.py
│   ├── 7_History.py
│   └── 8_Settings.py
├── components/                # Reusable UI building blocks
│   ├── sidebar.py
│   └── ui.py
├── core/                      # Session state + typed exceptions
│   ├── session.py
│   └── exceptions.py
├── services/                  # All business logic — framework-independent
│   ├── data_service.py         # File parsing/validation
│   ├── analytics_service.py    # Statistics, correlations, LLM context building
│   ├── chart_service.py        # Plotly chart construction
│   ├── llm_service.py          # Anthropic (Claude) integration
│   └── report_service.py       # Report assembly, persistence, export
├── db/                        # MySQL persistence layer
│   ├── engine.py                # Engine/session + automatic DB & table creation
│   ├── models.py                 # SQLAlchemy ORM models
│   └── crud.py                   # All database reads/writes
├── config/
│   └── settings.py             # Environment-based settings (no hardcoded values)
├── utils/
│   └── helpers.py              # Small framework-independent helpers
├── tests/                     # pytest suite for services + database layer
├── assets/
│   └── style.css               # The premium theme
├── .streamlit/config.toml     # Streamlit theme + server config
├── requirements.txt
├── .env.example
└── .gitignore
```

**Architecture rule:** pages never contain business logic. Every page
imports from `services/`, `db/`, and `components/` and does nothing but
call functions and render results. If you need to change *how* something
is calculated or stored, edit `services/` or `db/`, not `pages/`.

## Prerequisites

- Python 3.10+
- A running MySQL server you have credentials for
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

## Setup

### 1. Open a terminal in the project folder

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env            # Windows: copy .env.example .env
```

Edit `.env`:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=insight_studio

ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-5
```

You do **not** need to manually create the database or any tables — the
app creates them automatically on first run, as long as your MySQL user
can create databases (or pre-create an empty database and grant that user
access to it).

### 5. Run the app — one command

```bash
streamlit run app.py
```

or, using the convenience launcher (does a quick `.env` sanity check first):

```bash
python run.py
```

Opens at `http://localhost:8501`.

## Using the App

1. **Upload Dataset** — upload a file, preview it, then click **"Save to database & set as active dataset"**.
2. **Data Preview** — review row/column counts, types, and missing values.
3. **AI Chat** — ask things like *"What's the average of column X?"* or *"Any obvious outliers?"* — conversation history is saved automatically.
4. **Analysis** — review descriptive statistics and a correlation heatmap; optionally save a snapshot.
5. **Visualizations** — build histograms, scatter plots, and category charts.
6. **Reports** — generate an AI executive summary + trends/anomalies/recommendations, save it, and export.
7. **History** — reopen any saved report, browse past uploads, and view the full activity log.
8. **Settings** — verify your MySQL and Anthropic connections at any time.

## Configuration Reference

| Variable | Description | Default |
|---|---|---|
| `MYSQL_HOST` | MySQL server host | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | *(empty)* |
| `MYSQL_DATABASE` | Database name (auto-created) | `insight_studio` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | *(required for AI features)* |
| `ANTHROPIC_MODEL` | Claude model to use | `claude-sonnet-5` |
| `ANTHROPIC_MAX_TOKENS` | Max tokens per AI response | `1500` |
| `ANTHROPIC_TIMEOUT_SECONDS` | AI request timeout | `60` |
| `MAX_CONTEXT_ROWS` | Rows of your dataset sent to the AI as context | `50` |
| `APP_NAME` | Display name in the UI | `AI Insight Studio` |
| `APP_ENV` | `development` or `production` | `development` |
| `MAX_UPLOAD_MB` | Max upload size (MB) | `50` |

## Testing

```bash
pip install pytest   # already in requirements.txt
pytest tests/ -v
```

Tests cover `services/` (file validation, parsing, statistics) and `db/`
(CRUD operations, run against an in-memory SQLite database so the suite
doesn't require a live MySQL server).

## Troubleshooting

- **"Could not connect to MySQL"** — double-check `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, and `MYSQL_PASSWORD` in `.env`, confirm MySQL is running, then use **Retry connection** on the Settings page.
- **"ANTHROPIC_API_KEY is not set"** — add your key to `.env` and restart the app (Streamlit doesn't hot-reload `.env` changes).
- **PDF download missing** — install `reportlab` (already in `requirements.txt`).
- **Large files fail to upload** — increase `MAX_UPLOAD_MB` in `.env` and `server.maxUploadSize` in `.streamlit/config.toml`.

## Notes

- Only dataset **metadata** (filename, row/column counts, column types) is stored in MySQL — not the raw file contents — so re-running analysis or chat on a past dataset requires re-uploading the original file. Reports and chat history are stored in full.
- The app degrades gracefully: if MySQL or Anthropic is unreachable, you still get statistical previews and charts locally, with clear inline errors instead of crashes.
- No API keys or credentials are ever hardcoded — everything is read from environment variables via `.env`.
