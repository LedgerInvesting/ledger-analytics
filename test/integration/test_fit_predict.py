import pytest
from bermuda import meyers_tri
from requests import HTTPError

from ledger_analytics import AnalyticsClient, DevelopmentModel


def test_fit_predict():
    client = AnalyticsClient()
    clipped = meyers_tri.clip(max_eval=max(meyers_tri.periods)[-1])
    triangle = client.triangle.create(name="__test_tri", data=clipped)

    name = "__test_chain_ladder"
    chain_ladder = client.development_model.create(
        triangle=triangle,
        name="__test_chain_ladder",
        model_type="ChainLadder",
    )

    model_from_client = client.development_model.get(name=name)
    assert isinstance(model_from_client, DevelopmentModel)
    assert model_from_client.get_response.status_code == 200
    assert model_from_client.get_response.json()["name"] == name

    predictions = chain_ladder.predict(triangle=triangle)
    predictions2 = client.development_model.predict(
        triangle=triangle,
        name=name,
    )
    assert predictions.to_bermuda().extract("paid_loss").shape == (45, 10e3)
    assert predictions.to_bermuda() == predictions2.to_bermuda()

    chain_ladder.delete()
    with pytest.raises(ValueError):
        client.development_model.get(name=name)

    with pytest.raises(HTTPError):
        # Overwrote above, can't delete
        predictions.delete()

    predictions2.delete()
    with pytest.raises(ValueError):
        client.development_model.get(name=name)

    triangle.delete()
