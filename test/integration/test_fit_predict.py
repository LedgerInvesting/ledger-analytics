from bermuda import meyers_tri

from ledger_analytics import AnalyticsClient


def test_fit_predict():
    with AnalyticsClient() as client:
        chain_ladder = client.development_model.fit(
            triangle_name="meyers",
            model_name="chain_ladder",
            model_type="ChainLadder",
            model_config={},
        )
        try:
            chain_ladder.predict()
        except:
            chain_ladder.delete()
            raise
