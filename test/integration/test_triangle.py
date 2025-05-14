import os

import pytest
from bermuda import meyers_tri
from requests import HTTPError

from ledger_analytics import AnalyticsClient, Triangle


@pytest.fixture
def client():
    return AnalyticsClient()


def test_triangle_create_delete(client):
    name = "__test_tri_meyers"
    test_tri = client.triangle.get_or_create(name=name, data=meyers_tri.to_dict())

    assert test_tri.to_bermuda() == meyers_tri

    assert isinstance(client.triangle.get(name=name), Triangle)

    assert client.triangle.get(name=name).to_bermuda() == meyers_tri

    test_tri.delete()
    assert test_tri.delete_response.status_code == 204

    with pytest.raises(HTTPError):
        test_tri.delete()

    with pytest.raises(ValueError):
        client.triangle.delete(name)


def test_triangle_captured_output(client):
    os.environ["DISABLE_RICH_CONSOLE"] = "true"
    name = "__test_tri_meyers"
    test_tri = client.triangle.get_or_create(name=name, data=meyers_tri.to_dict())
    assert test_tri.captured_stdout
    test_tri.delete()

    os.environ["DISABLE_RICH_CONSOLE"] = "false"
    name = "__test_tri_meyers"
    test_tri = client.triangle.get_or_create(name=name, data=meyers_tri.to_dict())
    assert not test_tri.captured_stdout
    test_tri.delete()
