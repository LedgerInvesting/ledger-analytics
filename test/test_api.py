import pytest
from bermuda import meyers_tri, Triangle
import requests

from ledger_analytics import LedgerAnalytics, TriangleResponse, DevelopmentModel, TailModel, ForecastModel


def test_ledger_analytics_creation():
    assert isinstance(LedgerAnalytics(), LedgerAnalytics)

    client = LedgerAnalytics()
    assert client.host == "http://localhost:8000/analytics/"


def test_ledger_analytics_models():
    client = LedgerAnalytics()
    assert isinstance(client.triangle, TriangleResponse)
    assert isinstance(client.development_model, DevelopmentModel)
    assert isinstance(client.tail_model, TailModel)
    assert isinstance(client.forecast_model, ForecastModel)

def test_ledger_analytics_triangle_crud():
    client = LedgerAnalytics()
    triangle_create = client.triangle.create(
        config=dict(
            triangle_name="test_meyers_triangle",
            triangle_data=meyers_tri.to_dict(),
        )
    )
    triangle_get = client.triangle.get(triangle_id=triangle_create.triangle_id)
    assert triangle_create.triangle_id is not None
    assert isinstance(triangle_get, Triangle)

    triangle_delete = client.triangle.delete(triangle_id=triangle_create.triangle_id)

    with pytest.raises(requests.HTTPError):
        client.triangle.get(triangle_id=triangle_create.triangle_id)
