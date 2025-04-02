from time import sleep

from pytest import fixture

from ledger_analytics import AnalyticsClient


@fixture(scope="module")
def client():
    yield AnalyticsClient(asynchronous=True)


def test_every_dev_model(client):
    model_types = client.development_model.list_model_types()
    responses = [
        client.development_model.create(
            name=f"test_{model_type['name']}",
            triangle="meyers_clipped",
            model_type=model_type["name"],
            config={"loss_definition": "paid"},
        )
        for model_type in model_types["results"]
    ]
    statuses = [response.fit_status() for response in responses]
    while statuses.count("pending") > 0:
        statuses = [response.fit_status() for response in responses]
        sleep(2)
    assert all(status == "success" for status in statuses)
