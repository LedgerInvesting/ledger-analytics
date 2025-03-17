from bermuda import meyers_tri

from ledger_analytics import AnalyticsClient


def test_fit_predict():
    client = AnalyticsClient()
    chain_ladder = client.development_model.fit(
        triangle_name="meyers_clipped",
        model_name="chain_ladder",
        model_type="ChainLadder",
        model_config={},
    )
    chain_ladder.predict()
    chain_ladder.delete()
