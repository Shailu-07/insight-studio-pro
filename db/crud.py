"""Data access layer (CRUD operations) — the only module that touches
raw ORM objects directly. Everything else goes through these functions.
"""
from __future__ import annotations

from typing import Any, Optional

from db.engine import get_session
from db.models import ActivityLog, Analysis, ChatMessage, Dataset, Report


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

def create_dataset(
    filename: str,
    file_type: str,
    row_count: int,
    column_count: int,
    columns_json: list[dict[str, Any]],
    file_hash: Optional[str] = None,
) -> int:
    with get_session() as session:
        dataset = Dataset(
            filename=filename,
            file_type=file_type,
            row_count=row_count,
            column_count=column_count,
            columns_json=columns_json,
            file_hash=file_hash,
        )
        session.add(dataset)
        session.flush()
        dataset_id = dataset.id
    log_action("upload", f"Uploaded {filename} ({row_count} rows, {column_count} cols)", dataset_id=dataset_id)
    return dataset_id


def get_dataset(dataset_id: int) -> Optional[Dataset]:
    with get_session() as session:
        return session.get(Dataset, dataset_id)


def find_dataset_by_hash(file_hash: str) -> Optional[Dataset]:
    with get_session() as session:
        return (
            session.query(Dataset)
            .filter(Dataset.file_hash == file_hash)
            .order_by(Dataset.uploaded_at.desc())
            .first()
        )


def list_datasets(limit: int = 100) -> list[Dataset]:
    with get_session() as session:
        return session.query(Dataset).order_by(Dataset.uploaded_at.desc()).limit(limit).all()


def delete_dataset(dataset_id: int) -> None:
    with get_session() as session:
        dataset = session.get(Dataset, dataset_id)
        if dataset is not None:
            session.delete(dataset)


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------

def create_analysis(
    dataset_id: int,
    overview_json: dict[str, Any],
    summary_stats_json: dict[str, Any],
    missing_values_json: dict[str, Any],
    correlation_json: dict[str, Any],
) -> int:
    with get_session() as session:
        analysis = Analysis(
            dataset_id=dataset_id,
            overview_json=overview_json,
            summary_stats_json=summary_stats_json,
            missing_values_json=missing_values_json,
            correlation_json=correlation_json,
        )
        session.add(analysis)
        session.flush()
        analysis_id = analysis.id
    return analysis_id


def get_latest_analysis(dataset_id: int) -> Optional[Analysis]:
    with get_session() as session:
        return (
            session.query(Analysis)
            .filter(Analysis.dataset_id == dataset_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------

def add_chat_message(dataset_id: int, role: str, content: str) -> int:
    with get_session() as session:
        msg = ChatMessage(dataset_id=dataset_id, role=role, content=content)
        session.add(msg)
        session.flush()
        return msg.id


def list_chat_messages(dataset_id: int, limit: int = 200) -> list[ChatMessage]:
    with get_session() as session:
        return (
            session.query(ChatMessage)
            .filter(ChatMessage.dataset_id == dataset_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def create_report(
    dataset_id: int,
    title: str,
    model_used: str,
    executive_summary: str,
    sections_json: list[dict[str, str]],
    markdown_content: str,
) -> int:
    with get_session() as session:
        report = Report(
            dataset_id=dataset_id,
            title=title,
            model_used=model_used,
            executive_summary=executive_summary,
            sections_json=sections_json,
            markdown_content=markdown_content,
        )
        session.add(report)
        session.flush()
        report_id = report.id
    log_action("report_generated", f"Generated report '{title}'", dataset_id=dataset_id, report_id=report_id)
    return report_id


def get_report(report_id: int) -> Optional[Report]:
    with get_session() as session:
        return session.get(Report, report_id)


def list_reports(limit: int = 100) -> list[Report]:
    with get_session() as session:
        return session.query(Report).order_by(Report.created_at.desc()).limit(limit).all()


def delete_report(report_id: int) -> None:
    with get_session() as session:
        report = session.get(Report, report_id)
        if report is not None:
            session.delete(report)


# ---------------------------------------------------------------------------
# Activity log
# ---------------------------------------------------------------------------

def log_action(
    action: str,
    details: str = "",
    dataset_id: Optional[int] = None,
    report_id: Optional[int] = None,
) -> None:
    with get_session() as session:
        session.add(ActivityLog(action=action, details=details, dataset_id=dataset_id, report_id=report_id))


def list_activity(limit: int = 200) -> list[ActivityLog]:
    with get_session() as session:
        return session.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------------------------

def get_dashboard_counts() -> dict[str, int]:
    with get_session() as session:
        return {
            "datasets": session.query(Dataset).count(),
            "analyses": session.query(Analysis).count(),
            "reports": session.query(Report).count(),
            "chat_messages": session.query(ChatMessage).count(),
        }
