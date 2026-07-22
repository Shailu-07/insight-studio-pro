"""Tests for the CRUD layer.

These run against an in-memory SQLite database instead of MySQL, so the
suite works in CI/local dev without a database server. This validates the
ORM models and query logic; MySQL-specific behavior (e.g. JSON column
storage) is exercised for real when the app runs against MySQL directly.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import crud, engine as db_engine, models


@pytest.fixture(autouse=True)
def sqlite_engine():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    db_engine._engine = engine
    db_engine._SessionLocal = session_factory
    yield engine
    db_engine._engine = None
    db_engine._SessionLocal = None


def test_create_and_get_dataset():
    dataset_id = crud.create_dataset("sales.csv", "csv", 100, 5, [{"name": "a", "dtype": "int64"}])
    dataset = crud.get_dataset(dataset_id)
    assert dataset is not None
    assert dataset.filename == "sales.csv"
    assert dataset.row_count == 100


def test_find_dataset_by_hash():
    crud.create_dataset("a.csv", "csv", 10, 2, [], file_hash="abc123")
    found = crud.find_dataset_by_hash("abc123")
    assert found is not None
    assert found.filename == "a.csv"
    assert crud.find_dataset_by_hash("does-not-exist") is None


def test_chat_messages_round_trip():
    dataset_id = crud.create_dataset("chat.csv", "csv", 10, 2, [])
    crud.add_chat_message(dataset_id, "user", "What's the average?")
    crud.add_chat_message(dataset_id, "assistant", "The average is 42.")
    messages = crud.list_chat_messages(dataset_id)
    assert [m.role for m in messages] == ["user", "assistant"]
    assert messages[1].content == "The average is 42."


def test_create_report_and_activity_log():
    dataset_id = crud.create_dataset("report.csv", "csv", 10, 2, [])
    report_id = crud.create_report(
        dataset_id=dataset_id,
        title="Test Report",
        model_used="claude-sonnet-5",
        executive_summary="summary",
        sections_json=[{"title": "Key Trends", "content": "up and to the right"}],
        markdown_content="# Test Report",
    )
    report = crud.get_report(report_id)
    assert report.title == "Test Report"

    actions = [a.action for a in crud.list_activity()]
    assert "upload" in actions
    assert "report_generated" in actions


def test_delete_report():
    dataset_id = crud.create_dataset("del.csv", "csv", 10, 2, [])
    report_id = crud.create_report(dataset_id, "R", "m", "s", [], "# R")
    crud.delete_report(report_id)
    assert crud.get_report(report_id) is None


def test_dashboard_counts():
    dataset_id = crud.create_dataset("counts.csv", "csv", 10, 2, [])
    crud.create_report(dataset_id, "R", "m", "s", [], "# R")
    crud.add_chat_message(dataset_id, "user", "hi")

    counts = crud.get_dashboard_counts()
    assert counts["datasets"] == 1
    assert counts["reports"] == 1
    assert counts["chat_messages"] == 1
