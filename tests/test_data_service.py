import io

import pandas as pd
import pytest

from core.exceptions import EmptyDatasetError, FileValidationError, UnsupportedFormatError
from services import data_service


def test_validate_file_rejects_unsupported_extension():
    with pytest.raises(UnsupportedFormatError):
        data_service.validate_file("data.pdf", 100)


def test_validate_file_rejects_empty_file():
    with pytest.raises(FileValidationError):
        data_service.validate_file("data.csv", 0)


def test_validate_file_accepts_valid_csv():
    data_service.validate_file("data.csv", 100)  # should not raise


def test_load_dataframe_parses_csv():
    csv_bytes = b"a,b\n1,2\n3,4\n"
    df = data_service.load_dataframe(csv_bytes, "test.csv")
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_dataframe_raises_on_empty_result():
    csv_bytes = b"a,b\n"
    with pytest.raises(EmptyDatasetError):
        data_service.load_dataframe(csv_bytes, "empty.csv")


def test_load_dataframe_raises_on_corrupt_file():
    with pytest.raises(FileValidationError):
        data_service.load_dataframe(b"\x00\x01\x02not a real file", "broken.xlsx")


def test_get_column_summary_reports_missing_values():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
    summary = data_service.get_column_summary(df)
    a_summary = next(s for s in summary if s["column"] == "a")
    assert a_summary["missing_count"] == 1
    assert a_summary["missing_pct"] == pytest.approx(33.33, abs=0.01)


def test_file_hash_is_stable_and_content_sensitive():
    h1 = data_service.file_hash(b"hello")
    h2 = data_service.file_hash(b"hello")
    h3 = data_service.file_hash(b"world")
    assert h1 == h2
    assert h1 != h3


def test_infer_file_type():
    assert data_service.infer_file_type("report.CSV") == "csv"
    assert data_service.infer_file_type("book.xlsx") == "xlsx"
    assert data_service.infer_file_type("weird.pdf") == "unknown"
