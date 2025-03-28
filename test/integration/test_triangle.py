import time

import pytest
from bermuda import meyers_tri
from requests import HTTPError

from ledger_analytics import AnalyticsClient, Triangle


@pytest.fixture
def client():
    return AnalyticsClient()


def test_triangle_create_delete(client):
    name = "__test_tri"
    test_tri = client.triangle.create(name=name, data=meyers_tri.to_dict())

    assert test_tri.to_bermuda() == meyers_tri

    assert isinstance(client.triangle.get(name="__test_tri"), Triangle)

    test_tri.delete()
    assert test_tri.delete_response.status_code == 204

    with pytest.raises(HTTPError):
        test_tri.delete()

    with pytest.raises(ValueError):
        client.triangle.delete(name)


def test_triangle_get(client):
    meyers = client.triangle.get(name="meyers")
    assert meyers.data == meyers_tri.to_dict()
