"""Reusable Streamlit UI building blocks.

Every page composes its layout from these functions so the whole app
looks and feels consistent. Business logic never lives here.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

_STYLE_PATH = Path(__file__).resolve().parent.parent / "assets" / "style.css"


def inject_global_styles() -> None:
    if _STYLE_PATH.exists():
        st.markdown(f"<style>{_STYLE_PATH.read_text()}</style>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Large gradient hero banner — used once per page, at the top."""
    st.markdown(
        f"""
        <div class="ais-hero">
            <div class="ais-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Smaller, non-gradient header used for secondary pages."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="ais-page-header">
            <div class="ais-eyebrow">{eyebrow}</div>
            <h2>{title}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start(title: str | None = None, icon: str = "") -> None:
    st.markdown('<div class="ais-card">', unsafe_allow_html=True)
    if title:
        prefix = f"{icon} " if icon else ""
        st.markdown(f'<div class="ais-card-title">{prefix}{title}</div>', unsafe_allow_html=True)


def card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def stat_row(stats: list[tuple[str, str | int]]) -> None:
    """Render a horizontal row of stat/metric tiles.

    `stats` is a list of (label, value) tuples.
    """
    html = ['<div class="ais-stat-row">']
    for label, value in stats:
        html.append(
            f'<div class="ais-stat"><div class="ais-stat-label">{label}</div>'
            f'<div class="ais-stat-value">{value}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def badge(text: str, kind: str = "neutral") -> str:
    """Return an inline HTML badge span. `kind` is success | danger | neutral."""
    return f'<span class="ais-badge ais-badge-{kind}">{text}</span>'


def empty_state(message: str, hint: str = "") -> None:
    st.info(message)
    if hint:
        st.caption(hint)


def chat_bubble(role: str, content: str) -> None:
    css_class = "ais-chat-user" if role == "user" else "ais-chat-assistant"
    label = "You" if role == "user" else "AI"
    safe_content = html.escape(content).replace("\n", "<br>")
    st.markdown(
        f'<div class="ais-chat-bubble {css_class}"><strong>{label}:</strong><br>{safe_content}</div>',
        unsafe_allow_html=True,
    )
