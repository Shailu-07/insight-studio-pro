# """Anthropic (Claude) integration, isolated behind a small interface.

# Everything that talks to the Anthropic SDK lives here. Swapping providers
# means editing this file only — nothing else in the app imports `anthropic`
# directly.
# """
# from __future__ import annotations

# import json

# import anthropic

# from config import settings
# from core.exceptions import LLMConfigError, LLMRequestError

# CHAT_SYSTEM_PROMPT = (
#     "You are a precise, no-nonsense data analyst assistant embedded in a "
#     "Streamlit application. You are given a compact textual summary of a "
#     "user's dataset (shape, column types, statistics, a row sample). "
#     "Answer questions about the dataset directly and concretely. "
#     "If something can't be determined from the summary provided, say so "
#     "plainly instead of guessing. Keep answers concise and skip filler."
# )

# REPORT_KEYS = ["executive_summary", "key_trends", "anomalies", "recommendations"]


# def _get_client() -> anthropic.Anthropic:
#     if not settings.has_valid_api_key:
#         raise LLMConfigError(
#             "No Anthropic API key configured. Add ANTHROPIC_API_KEY to your "
#             ".env file (see .env.example) and restart the app."
#         )
#     return anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=settings.anthropic_timeout_seconds)


# def _call(messages: list[dict], max_tokens: int | None = None, system: str | None = None) -> str:
#     client = _get_client()
#     try:
#         response = client.messages.create(
#             model=settings.anthropic_model,
#             max_tokens=max_tokens or settings.anthropic_max_tokens,
#             system=system,
#             messages=messages,
#         )
#     except anthropic.APITimeoutError as exc:
#         raise LLMRequestError("The AI request timed out. Please try again.") from exc
#     except anthropic.APIConnectionError as exc:
#         raise LLMRequestError("Couldn't reach the Anthropic API. Check your connection.") from exc
#     except anthropic.AuthenticationError as exc:
#         raise LLMRequestError("Anthropic authentication failed. Check your ANTHROPIC_API_KEY.") from exc
#     except anthropic.RateLimitError as exc:
#         raise LLMRequestError("The Anthropic API rate limit was reached. Please wait and try again.") from exc
#     except anthropic.APIStatusError as exc:
#         raise LLMRequestError(f"The Anthropic API returned an error (status {exc.status_code}).") from exc

#     parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
#     text = "\n".join(parts).strip()
#     if not text:
#         raise LLMRequestError("The AI returned an empty response.")
#     return text


# def ask(question: str, dataset_context: str, chat_history: list[dict] | None = None) -> str:
#     """Send a question plus dataset context to Claude and return its reply.

#     Raises:
#         LLMConfigError: API key missing/invalid.
#         LLMRequestError: network failure, timeout, or API-side error.
#     """
#     messages = []
#     for turn in (chat_history or [])[-6:]:  # bounded context window
#         messages.append({"role": turn["role"], "content": turn["content"]})
#     messages.append({"role": "user", "content": question})

#     system = f"{CHAT_SYSTEM_PROMPT}\n\nDataset summary:\n{dataset_context}"
#     return _call(messages, system=system)


# def generate_report_summary(dataset_context: str) -> str:
#     """One-shot call used by the Reports page to produce a narrative summary."""
#     prompt = (
#         "Write a short executive summary (4-6 sentences) covering: what the "
#         "data looks like, any notable patterns or data quality issues, and "
#         "one suggested next step for analysis.\n\nDataset summary:\n" + dataset_context
#     )
#     return _call([{"role": "user", "content": prompt}])


# def generate_full_insights(dataset_context: str) -> dict[str, str]:
#     """Structured insights (trends/anomalies/recommendations) for the Reports page."""
#     prompt = f"""You are a senior business data analyst. Based on the dataset summary \
# below, produce a business-style report.

# Dataset summary:
# {dataset_context}

# Respond with ONLY a single valid JSON object (no markdown fences, no preamble) \
# using exactly these keys:
# - "executive_summary": 3-5 sentence overview of what this dataset shows.
# - "key_trends": bullet-style findings (use "- " prefix per line).
# - "anomalies": bullet-style findings about outliers or data quality issues. \
# If none, say so explicitly.
# - "recommendations": bullet-style, actionable business recommendations.

# Return raw JSON only."""

#     text = _call([{"role": "user", "content": prompt}])
#     return _parse_json(text)


# def _parse_json(text: str) -> dict[str, str]:
#     cleaned = text.strip()
#     if cleaned.startswith("```"):
#         cleaned = cleaned.strip("`")
#         if cleaned.lower().startswith("json"):
#             cleaned = cleaned[4:]
#         cleaned = cleaned.strip()

#     try:
#         data = json.loads(cleaned)
#     except json.JSONDecodeError as exc:
#         start, end = cleaned.find("{"), cleaned.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             try:
#                 data = json.loads(cleaned[start : end + 1])
#             except json.JSONDecodeError:
#                 raise LLMRequestError(f"The AI response was not valid JSON: {exc}") from exc
#         else:
#             raise LLMRequestError(f"The AI response was not valid JSON: {exc}") from exc

#     missing = [key for key in REPORT_KEYS if key not in data]
#     if missing:
#         raise LLMRequestError(f"The AI response was missing expected fields: {', '.join(missing)}")
#     return data

"""Groq integration, isolated behind a small interface.

Everything that talks to the Groq SDK lives here. Swapping providers
means editing this file only — nothing else in the app imports `groq`
directly.
"""
from __future__ import annotations

import json

import groq

from config import settings
from core.exceptions import LLMConfigError, LLMRequestError

CHAT_SYSTEM_PROMPT = (
    "You are a precise, no-nonsense data analyst assistant embedded in a "
    "Streamlit application. You are given a compact textual summary of a "
    "user's dataset (shape, column types, statistics, a row sample). "
    "Answer questions about the dataset directly and concretely. "
    "If something can't be determined from the summary provided, say so "
    "plainly instead of guessing. Keep answers concise and skip filler."
)

REPORT_KEYS = ["executive_summary", "key_trends", "anomalies", "recommendations"]


def _get_client() -> groq.Groq:
    if not settings.has_valid_api_key:
        raise LLMConfigError(
            "No Groq API key configured. Add GROQ_API_KEY to your "
            ".env file (see .env.example) and restart the app."
        )
    return groq.Groq(api_key=settings.groq_api_key, timeout=settings.groq_timeout_seconds)


def _call(messages: list[dict], max_tokens: int | None = None, system: str | None = None) -> str:
    client = _get_client()

    # Groq (OpenAI-style API) expects the system prompt as a message in the
    # list, not as a separate top-level parameter like Anthropic's API.
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    try:
        # response = client.chat.completions.create(
        #     model=settings.groq_model,
        #     max_tokens=max_tokens or settings.groq_max_tokens,
        #     messages=full_messages,
        # )
        response = client.chat.completions.create(
        model=settings.groq_model,
        max_tokens=max_tokens or settings.groq_max_tokens,
        messages=full_messages,
        response_format={"type": "json_object"},
        )
    
    except groq.APITimeoutError as exc:
        raise LLMRequestError("The AI request timed out. Please try again.") from exc
    except groq.APIConnectionError as exc:
        raise LLMRequestError("Couldn't reach the Groq API. Check your connection.") from exc
    except groq.AuthenticationError as exc:
        raise LLMRequestError("Groq authentication failed. Check your GROQ_API_KEY.") from exc
    except groq.RateLimitError as exc:
        raise LLMRequestError(
            "The Groq API rate limit was reached. Please wait a moment and try again."
        ) from exc
    except groq.APIStatusError as exc:
        raise LLMRequestError(f"The Groq API returned an error (status {exc.status_code}).") from exc

    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise LLMRequestError("The AI returned an empty response.")
    return text


def ask(question: str, dataset_context: str, chat_history: list[dict] | None = None) -> str:
    """Send a question plus dataset context to Groq and return its reply.

    Raises:
        LLMConfigError: API key missing/invalid.
        LLMRequestError: network failure, timeout, or API-side error.
    """
    messages = []
    for turn in (chat_history or [])[-6:]:  # bounded context window
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})

    system = f"{CHAT_SYSTEM_PROMPT}\n\nDataset summary:\n{dataset_context}"
    return _call(messages, system=system)


def generate_report_summary(dataset_context: str) -> str:
    """One-shot call used by the Reports page to produce a narrative summary."""
    prompt = (
        "Write a short executive summary (4-6 sentences) covering: what the "
        "data looks like, any notable patterns or data quality issues, and "
        "one suggested next step for analysis.\n\nDataset summary:\n" + dataset_context
    )
    return _call([{"role": "user", "content": prompt}])


def generate_full_insights(dataset_context: str) -> dict[str, str]:
    """Structured insights (trends/anomalies/recommendations) for the Reports page."""
    prompt = f"""You are a senior business data analyst. Based on the dataset summary \
below, produce a business-style report.

Dataset summary:
{dataset_context}

Respond with ONLY a single valid JSON object (no markdown fences, no preamble) \
using exactly these keys:
- "executive_summary": 3-5 sentence overview of what this dataset shows.
- "key_trends": bullet-style findings (use "- " prefix per line).
- "anomalies": bullet-style findings about outliers or data quality issues. \
If none, say so explicitly.
- "recommendations": bullet-style, actionable business recommendations.

Return raw JSON only."""

    text = _call([{"role": "user", "content": prompt}])
    return _parse_json(text)


def _parse_json(text: str) -> dict[str, str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                raise LLMRequestError(f"The AI response was not valid JSON: {exc}") from exc
        else:
            raise LLMRequestError(f"The AI response was not valid JSON: {exc}") from exc

    missing = [key for key in REPORT_KEYS if key not in data]
    if missing:
        raise LLMRequestError(f"The AI response was missing expected fields: {', '.join(missing)}")
    return data