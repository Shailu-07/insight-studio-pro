"""Report assembly, AI orchestration, persistence, and export (Markdown / CSV / PDF)."""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import pandas as pd

from db import crud


def build_markdown_report(dataset_name: str, overview: dict, sections: list[dict]) -> str:
    """Assemble a Markdown report from the dataset overview and accumulated sections."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# Data Insight Report — {dataset_name}",
        f"*Generated {generated_at}*",
        "",
        "## Dataset Overview",
        f"- Rows: {overview['rows']}",
        f"- Columns: {overview['columns']}",
        f"- Missing cells: {overview['missing_cells']} ({overview['missing_pct']}%)",
        f"- Duplicate rows: {overview['duplicate_rows']}",
        f"- Numeric columns: {overview['numeric_columns']}",
        f"- Categorical columns: {overview['categorical_columns']}",
        "",
    ]

    for section in sections:
        lines.append(f"## {section['title']}")
        lines.append(section["content"])
        lines.append("")

    if not sections:
        lines.append("_No additional sections added yet. Generate an AI summary first._")

    # return "\n".join(lines)
    return "\n".join(map(str, lines))


def save_report(
    dataset_id: int,
    title: str,
    model_used: str,
    executive_summary: str,
    sections: list[dict],
    markdown_content: str,
) -> int:
    """Persist a report to MySQL and return its id."""
    return crud.create_report(
        dataset_id=dataset_id,
        title=title,
        model_used=model_used,
        executive_summary=executive_summary,
        sections_json=sections,
        markdown_content=markdown_content,
    )


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buffer.getvalue()


def markdown_to_pdf_bytes(title: str, markdown_content: str) -> bytes | None:
    """Render a report as a simple PDF. Returns None if `reportlab` isn't installed."""
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story: list[Any] = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    for block in markdown_content.split("\n\n"):
        clean = block.strip()
        if not clean:
            continue
        if clean.startswith("## "):
            story.append(Paragraph(clean[3:], styles["Heading2"]))
        elif clean.startswith("# "):
            continue  # already used as the title
        else:
            story.append(Paragraph(clean.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()
