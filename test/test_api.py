from test.mock_requester import (
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


def test_ledger_analytics_creation():
    assert isinstance(AnalyticsClient(API_KEY), AnalyticsClient)

    client = AnalyticsClient(API_KEY)
    assert client.host == "http://localhost:8000/analytics/"
    assert (
        AnalyticsClient(API_KEY, host="http://test.com/analytics").host
        == "http://test.com/analytics/"
    )


def test_ledger_analytics_models():
    client = AnalyticsClient(API_KEY)
    assert isinstance(client.triangle, Triangle)
    assert isinstance(client.development_model, DevelopmentModel)
    assert isinstance(client.tail_model, TailModel)
    assert isinstance(client.forecast_model, ForecastModel)


def test_ledger_analytics_triangle_crud():
    client = AnalyticsClient(API_KEY, host="http://test.com/analytics/")
    client._requester = TriangleMockRequester(API_KEY)
    triangle_create = client.triangle.create(
        config={
            "triangle_name": "test_meyers_triangle",
            "triangle_data": meyers_tri.to_dict(),
        }
    )
    assert triangle_create.post_response.status_code == 201
    triangle_get = client.triangle.get(triangle_id=triangle_create.triangle_id)
    assert triangle_create.triangle_id is not None
    assert isinstance(triangle_get, BermudaTriangle)

    client._requester = TriangleMockRequesterAfterDeletion(API_KEY)
    client.triangle.delete(triangle_id=triangle_create.triangle_id)

    with pytest.raises(requests.HTTPError):
        client.triangle.get(triangle_id=triangle_create.triangle_id)
