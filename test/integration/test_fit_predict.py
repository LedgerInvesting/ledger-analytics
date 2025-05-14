import time

import pytest
from bermuda import meyers_tri
from requests import HTTPError

from ledger_analytics import AnalyticsClient, DevelopmentModel


def test_chain_ladder_fit_predict():
    client = AnalyticsClient()
    clipped = meyers_tri.clip(max_eval=max(meyers_tri.periods)[-1])
    triangle = client.triangle.get_or_create(name="__test_tri_clipped", data=clipped)

    name = "__test_chain_ladder"
    try:
        old_test = client.development_model.get(name=name)
        old_test.delete()
    except ValueError:
        pass

    chain_ladder = client.development_model.create(  # noqa: F841
        triangle=triangle,
        name=name,
        model_type="ChainLadder",
        config={
            "loss_family": "gamma",
            "autofit_override": dict(
                samples_per_chain=10,
                max_samples_per_chain=10,
                adapt_delta=0.8,
                max_adapt_delta=0.8,
                max_treedepth=10,
                max_max_treedepth=10,
            ),
        },
    )

    # Recreating the same model should fail since it already exists with that name
    with pytest.raises(HTTPError):
        chain_ladder_bad = client.development_model.create(  # noqa: F841
            triangle=triangle,
            name=name,
            model_type="ChainLadder",
            config={
                "loss_family": "gamma",
                "autofit_override": dict(
                    samples_per_chain=11,
                    max_samples_per_chain=10,
                    adapt_delta=0.8,
                    max_adapt_delta=0.8,
                    max_treedepth=10,
                    max_max_treedepth=10,
                ),
            },
        )
    # Get or create should return the existing model
    chain_ladder_got = client.development_model.get_or_create(  # noqa: F841
        triangle=triangle,
        name=name,
        model_type="ChainLadder",
        config={
            "loss_family": "gamma",
            "autofit_override": dict(
                samples_per_chain=10,
                max_samples_per_chain=10,
                adapt_delta=0.8,
                max_adapt_delta=0.8,
                max_treedepth=10,
                max_max_treedepth=10,
            ),
        },
    )
    # Get or create should fail since args have changed
    with pytest.raises(ValueError):
        chain_ladder_break = client.development_model.get_or_create(  # noqa: F841
            triangle=triangle,
            name=name,
            model_type="ChainLadder",
            config={
                "loss_family": "gamma",
                "autofit_override": dict(
                    samples_per_chain=11,
                    max_samples_per_chain=10,
                    adapt_delta=0.8,
                    max_adapt_delta=0.8,
                    max_treedepth=10,
                    max_max_treedepth=10,
                ),
            },
        )
    # get or update should work and replace the model
    chain_ladder_update = client.development_model.get_or_update(
        triangle=triangle,
        name=name,
        model_type="ChainLadder",
        config={
            "loss_family": "gamma",
            "autofit_override": dict(
                samples_per_chain=10,
                max_samples_per_chain=10,
                adapt_delta=0.8,
                max_adapt_delta=0.8,
                max_treedepth=10,
                max_max_treedepth=10,
            ),
        },
    )

    model_from_client = client.development_model.get(name=name)
    assert isinstance(model_from_client, DevelopmentModel)
    assert model_from_client.get_response.status_code == 200
    assert model_from_client.get_response.json()["name"] == name

    try:
        client.triangle.delete(name="__test_chain_ladder___test_tri_clipped")
    except ValueError:
        pass
    try:
        client.triangle.delete(name="__test_chain_ladder___test_tri_clipped2")
    except ValueError:
        pass
    predictions = chain_ladder_update.predict(triangle=triangle)
    predictions2 = client.development_model.predict(
        triangle=triangle,
        name=name,
        prediction_name="__test_chain_ladder___test_tri_clipped2",
    )
    assert predictions.to_bermuda().extract("paid_loss").shape == (45, 40)
    assert predictions.to_bermuda() == predictions2.to_bermuda()

    assert chain_ladder_update.terminate() == chain_ladder_update

    chain_ladder_update.delete()
    with pytest.raises(ValueError):
        client.development_model.get(name=name)

    predictions.delete()
    predictions2.delete()
    with pytest.raises(ValueError):
        client.development_model.get(name=name)

    triangle.delete()


def test_fit_termination():
    client = AnalyticsClient(asynchronous=True)
    clipped = meyers_tri.clip(max_eval=max(meyers_tri.periods)[-1])
    triangle = client.triangle.get_or_create(name="__test_tri_clipped", data=clipped)

    name = "__test_chain_ladder"
    chain_ladder = client.development_model.create(
        triangle=triangle,
        name=name,
        model_type="ChainLadder",
        overwrite=True,
    )

    chain_ladder.terminate()

    assert chain_ladder.poll().get("status") == "TERMINATED"

    chain_ladder.delete()
    triangle.delete()
