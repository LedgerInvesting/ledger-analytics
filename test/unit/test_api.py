from test.unit.mock_requester import (
    TriangleMockRequester,
    TriangleMockRequesterAfterDeletion,
)

import pytest
import requests
from bermuda import Triangle as BermudaTriangle
from bermuda import meyers_tri

from ledger_analytics import (
    AnalyticsClient,
    DevelopmentModel,
    ForecastModel,
    TailModel,
    Triangle,
)

API_KEY = "abc.123"
TEST_HOST = "http://test.com/analytics/"


def test_ledger_analytics_creation():
    assert isinstance(AnalyticsClient(API_KEY), AnalyticsClient)

    client = AnalyticsClient(API_KEY)
    assert client.host == "http://localhost:8000/analytics/"
    assert AnalyticsClient(API_KEY, host=TEST_HOST[:-1]).host == TEST_HOST


def test_ledger_analytics_models():
    client = AnalyticsClient(API_KEY)
    assert isinstance(client.triangle, Triangle)
    assert isinstance(client.development_model, DevelopmentModel)
    assert isinstance(client.tail_model, TailModel)
    assert isinstance(client.forecast_model, ForecastModel)


def test_ledger_analytics_triangle_crud():
    client = AnalyticsClient(API_KEY, host=TEST_HOST)
    client._requester = TriangleMockRequester(API_KEY)
    triangle_create = client.triangle.create(
        triangle_name="test_meyers_triangle",
        triangle_data=meyers_tri.to_dict(),
    )
    assert triangle_create.post_response.status_code == 201
    name, triangle_get = client.triangle.get(triangle_id=triangle_create.triangle_id)
    assert triangle_create.triangle_id is not None
    assert isinstance(triangle_get, BermudaTriangle)
    assert name == "test_meyers_triangle"

    client._requester = TriangleMockRequesterAfterDeletion(API_KEY)
    client.triangle.delete(triangle_id=triangle_create.triangle_id)

    with pytest.raises(requests.HTTPError):
        client.triangle.get(triangle_id=triangle_create.triangle_id)


def test_ledger_analytics_model_crud():
    # TODO
    AnalyticsClient(API_KEY, host=TEST_HOST)
