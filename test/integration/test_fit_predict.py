import time

import pytest
from bermuda import meyers_tri
from requests import HTTPError

from ledger_analytics import AnalyticsClient


def test_fit_predict():
    client = AnalyticsClient()
    chain_ladder = client.development_model.create(
        triangle_name="meyers_clipped",
        model_name="chain_ladder",
        model_type="ChainLadder",
    )

    assert chain_ladder.get().status_code == 200
    assert chain_ladder.get().json()["name"] == "chain_ladder"
    chain_ladder.predict(triangle_name="meyers_clipped")
    prediction_id = chain_ladder.predict_response.json()["predictions"]
    time.sleep(20)
    predictions = client.triangle.get(triangle_id=prediction_id)
    assert predictions.to_bermuda().extract("paid_loss").shape == (36, 10e3)

    chain_ladder.delete()
    with pytest.raises(HTTPError):
        chain_ladder.get()
