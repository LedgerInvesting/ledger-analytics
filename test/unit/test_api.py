from test.unit.mock_requester import (
    ModelMockRequester,
    ModelMockRequesterAfterDeletion,
    TriangleMockRequester,
    TriangleMockRequesterAfterDeletion,
)

import pydantic_core
import pytest
import requests
from bermuda import Triangle as BermudaTriangle
from bermuda import meyers_tri

from ledger_analytics import (
    AnalyticsClient,
    CashflowInterface,
    CashflowModel,
    DevelopmentModel,
    ForecastModel,
    ModelInterface,
    TailModel,
    TriangleInterface,
)
from ledger_analytics.api import ENV

API_KEY = "abc.123"
TEST_HOST = "http://test.com/analytics/"


def test_ledger_analytics_creation():
    assert isinstance(AnalyticsClient(API_KEY), AnalyticsClient)

    client = AnalyticsClient(API_KEY)
    assert client.host == ENV.host


def test_ledger_analytics_models():
    client = AnalyticsClient(API_KEY)
    assert isinstance(client.triangle, TriangleInterface)
    assert isinstance(client.development_model, ModelInterface)
    assert isinstance(client.tail_model, ModelInterface)
    assert isinstance(client.forecast_model, ModelInterface)
    assert isinstance(client.cashflow_model, CashflowInterface)


def test_ledger_analytics_triangle_crud():
    client = AnalyticsClient(API_KEY)
    client.host = TEST_HOST
    client._requester = TriangleMockRequester(API_KEY)
    triangle = client.triangle.create(
        name="test_meyers_triangle",
        data=meyers_tri.to_dict(),
    )
    assert triangle.id == "abc"
    assert isinstance(triangle.to_bermuda(), BermudaTriangle)
    assert triangle.data == meyers_tri.to_dict()
    assert triangle.name == "test_meyers_triangle"

    triangle.delete()
    client._requester = TriangleMockRequesterAfterDeletion(API_KEY)

    with pytest.raises(requests.HTTPError):
        client.triangle.get(id=triangle.id)


def test_ledger_analytics_model_crud():
    client = AnalyticsClient(API_KEY, asynchronous=True)
    client.host = TEST_HOST
    client._requester = ModelMockRequester(API_KEY)

    development_model = client.development_model.create(
        triangle="test_meyers_triangle",
        name="test_chain_ladder",
        model_type="ChainLadder",
        config={
            "loss_family": "gamma",
            "autofit_override": {"samples_per_chain": 1000},
        },
    )
    development_model.predict("test_meyers_triangle")
    client.development_model.predict("test_meyers_triangle", name="test_chain_ladder")

    tail_model = client.tail_model.create(
        triangle="test_meyers_triangle",
        name="test_bondy",
        model_type="GeneralizedBondy",
    )
    forecast_model = client.forecast_model.create(
        triangle="test_meyers_triangle",
        name="test_ar1",
        model_type="AR1",
    )
    cashflow_model = client.cashflow_model.create(
        dev_model="test_chain_ladder",
        tail_model="test_bondy",
        name="test_cashflows",
    )

    assert isinstance(development_model, DevelopmentModel)
    assert isinstance(tail_model, TailModel)
    assert isinstance(forecast_model, ForecastModel)
    assert isinstance(cashflow_model, CashflowModel)

    assert development_model.fit_response.status_code == 201
    assert development_model.fit_response.json()["model"]["id"] == "model_abc"

    development_model.predict("test_meyers_triangle")
    assert development_model.predict_response.status_code == 201
    assert development_model.predict_response.json()["predictions"] == "triangle_abc"

    development_model.delete()

    client._requester = ModelMockRequesterAfterDeletion(API_KEY)
    with pytest.raises(requests.HTTPError):
        client.development_model.delete(name="test_chain_ladder")


def test_ledger_analytics_model_configs():
    client = AnalyticsClient(API_KEY, asynchronous=True)
    client.host = TEST_HOST
    client._requester = ModelMockRequester(API_KEY)

    with pytest.raises(pydantic_core.ValidationError):
        client.development_model.create(
            triangle="test_meyers_triangle",
            name="test_chain_ladder",
            model_type="ChainLadder",
            config={"foo": True},
        )

    with pytest.raises(pydantic_core.ValidationError):
        client.development_model.create(
            triangle="test_meyers_triangle",
            name="meyers_crc",
            model_type="MeyersCRC",
            config={"foo": True},
        )

    with pytest.raises(pydantic_core.ValidationError):
        cash_model = client.cashflow_model.create(
            dev_model="test_chain_ladder",
            tail_model="test_bondy",
            name="test_cashflows",
        )
        cash_model.predict(
            triangle="test_meyers_triangle",
            config={"foo": True},
        )
