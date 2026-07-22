"""SQLAlchemy ORM models.

Tables:
    datasets       - metadata about every uploaded file
    analyses       - cached statistical profile for a dataset
    chat_messages  - AI Chat conversation history, per dataset
    reports        - saved reports (AI summary + accumulated sections)
    activity_log   - simple audit trail used by the History page
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import JSON

Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    row_count = Column(Integer, nullable=False, default=0)
    column_count = Column(Integer, nullable=False, default=0)
    columns_json = Column(JSON, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analyses = relationship("Analysis", back_populates="dataset", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Dataset id={self.id} filename={self.filename!r}>"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    overview_json = Column(JSON, nullable=True)
    summary_stats_json = Column(JSON, nullable=True)
    missing_values_json = Column(JSON, nullable=True)
    correlation_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("Dataset", back_populates="analyses")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Analysis id={self.id} dataset_id={self.dataset_id}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("Dataset", back_populates="chat_messages")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatMessage id={self.id} role={self.role}>"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    title = Column(String(255), nullable=False)
    model_used = Column(String(100), nullable=True)
    executive_summary = Column(Text, nullable=True)
    sections_json = Column(JSON, nullable=True)  # list[{"title","content"}]
    markdown_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("Dataset", back_populates="reports")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Report id={self.id} title={self.title!r}>"


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    dataset_id = Column(Integer, nullable=True)
    report_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog id={self.id} action={self.action!r}>"
