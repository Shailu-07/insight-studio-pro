# AI Insight Studio

Upload a dataset, explore it visually, chat with Groq AI about it in plain
English, and save every dataset, analysis, chat, and report to your own
MySQL database — all in one polished Streamlit app.

This is a merged, upgraded build: clean layered architecture and a real
test suite, **plus** full MySQL persistence and Groq-powered AI, with
a redesigned, more attractive UI on top.

## Features

- **Upload Dataset** — CSV/TSV/Excel upload with format, size, and content validation.
- **Data Preview** — row preview, per-column type/missing-value summary, missing-values chart.
- **AI Chat** — ask questions about your data in natural language (powered by Groq AI). Conversations are saved per dataset, so you can pick up where you left off.
- **Analysis** — descriptive statistics and a correlation heatmap; save a snapshot to the database.
- **Visualizations** — histograms, scatter comparisons, and category breakdowns, all user-driven.
- **Reports** — generate an AI executive summary + trends/anomalies/recommendations, save it, and export as Markdown, PDF, or the cleaned CSV.
- **History** — every dataset, report, and activity event is stored in MySQL and browsable/reopenable anytime.
- **Settings** — live MySQL and Groq connection status, with a one-click retry.
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
├── components/
│   ├── sidebar.py
│   └── ui.py
├── core/
│   ├── session.py
│   └── exceptions.py
├── services/
│   ├── data_service.py
│   ├── analytics_service.py
│   ├── chart_service.py
│   ├── llm_service.py          # Groq AI integration
│   └── report_service.py
├── db/
│   ├── engine.py
│   ├── models.py
│   └── crud.py
├── config/
│   └── settings.py
├── utils/
│   └── helpers.py
├── tests/
├── assets/
│   └── style.css
├── .streamlit/config.toml
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
- A Groq API key (https://console.groq.com/keys)

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

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=insight_studio

GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
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
8. **Settings** — verify your MySQL and Groq connections at any time.

## Configuration Reference

| Variable | Description | Default |
|---|---|---|
| `MYSQL_HOST` | MySQL server host | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | *(empty)* |
| `MYSQL_DATABASE` | Database name (auto-created) | `insight_studio` |
| `GROQ_API_KEY` | Your Groq API key | *(required for AI features)* |
| `GROQ_MODEL` | Groq model to use | `llama-3.3-70b-versatile` |
| `GROQ_MAX_TOKENS` | Max tokens per AI response | `1500` |
| `GROQ_TIMEOUT_SECONDS` | AI request timeout | `60` |
| `MAX_CONTEXT_ROWS` | Rows of your dataset sent to the AI as context | `50` |
| `APP_NAME` | Display name in the UI | `AI Insight Studio` |
| `APP_ENV` | `development` or `production` | `development` |
| `MAX_UPLOAD_MB` | Max upload size (MB) | `50` |

## Testing

```bash
pip install pytest
pytest tests/ -v
```

Tests cover `services/` (file validation, parsing, statistics) and `db/`
(CRUD operations, run against an in-memory SQLite database so the suite
doesn't require a live MySQL server).

## Troubleshooting

- **"Could not connect to MySQL"** — double-check `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, and `MYSQL_PASSWORD` in `.env`, confirm MySQL is running, then use **Retry connection** on the Settings page.
- **"GROQ_API_KEY is not set"** — add your key to `.env` and restart the app (Streamlit doesn't hot-reload `.env` changes).
- **PDF download missing** — install `reportlab` (already in `requirements.txt`).
- **Large files fail to upload** — increase `MAX_UPLOAD_MB` in `.env` and `server.maxUploadSize` in `.streamlit/config.toml`.

## Notes

- Only dataset **metadata** (filename, row/column counts, column types) is stored in MySQL — not the raw file contents — so re-running analysis or chat on a past dataset requires re-uploading the original file. Reports and chat history are stored in full.
- The app degrades gracefully: if MySQL or Groq is unreachable, you still get statistical previews and charts locally, with clear inline errors instead of crashes.
- No API keys or credentials are ever hardcoded — everything is read from environment variables via `.env`.
