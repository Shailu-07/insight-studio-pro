import pandas as pd
import pytest

from core.exceptions import MissingColumnError
from services import analytics_service


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "amount": [10, 20, 30, None, 50],
            "region": ["east", "west", "east", "east", "north"],
        }
    )


def test_get_numeric_columns(sample_df):
    assert analytics_service.get_numeric_columns(sample_df) == ["amount"]


def test_get_categorical_columns(sample_df):
    assert analytics_service.get_categorical_columns(sample_df) == ["region"]


def test_describe_numeric_not_empty(sample_df):
    result = analytics_service.describe_numeric(sample_df)
    assert "amount" in result
    assert result["amount"]["count"] == 4


def test_dataset_overview_counts_missing(sample_df):
    overview = analytics_service.dataset_overview(sample_df)
    assert overview["rows"] == 5
    assert overview["columns"] == 2
    assert overview["missing_cells"] == 1


def test_top_categories_raises_on_missing_column(sample_df):
    with pytest.raises(MissingColumnError):
        analytics_service.top_categories(sample_df, "nonexistent")


def test_top_categories_counts_correctly(sample_df):
    counts = analytics_service.top_categories(sample_df, "region")
    assert counts["east"] == 3
    assert counts["west"] == 1


def test_correlation_matrix_empty_for_single_numeric_column(sample_df):
    assert analytics_service.correlation_matrix(sample_df) == {}


def test_correlation_matrix_with_two_numeric_columns():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [4, 3, 2, 1]})
    corr = analytics_service.correlation_matrix(df)
    assert corr["a"]["b"] == -1.0


def test_build_context_summary_contains_key_facts(sample_df):
    summary = analytics_service.build_context_summary(sample_df, "sales.csv")
    assert "sales.csv" in summary
    assert "amount" in summary
    assert "region" in summary
