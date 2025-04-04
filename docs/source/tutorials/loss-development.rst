Loss Development Modeling
================================

This tutorial walks through a typical loss development
workflow using LedgerAnalytics.

..  code:: python

    from ledger_analytics import AnalyticsClient

    # If you've set the LEDGER_ANALYTICS_API_KEY environment variable
    client = AnalyticsClient()

    # alternatively
    api_key = "..."
    client = AnalyticsClient(api_key)

The ``bermuda`` library comes equiped with a sample triangle with paid loss
and earned premium. It's a squared triangle, so we'll clip off the 
lower-right triangle leaving a typical triangle-shaped loss development
triangle, and load it into the API.

..  code:: python

    from datetime import date
    from bermuda import meyers_tri

    clipped_meyers = meyers_tri.clip(max_eval=date(1997, 12, 31)) 
    dev_triangle = client.triangle.create(name="meyers_triangle", data=clipped_meyers)

.. image:: clipped_meyers.png

Let's see which models are available to us for loss and tail development.

..  code:: python

    client.development_model.list_model_types()
    client.tail_model.list_model_types()

We'll start with body development models. We'll use the standard ``ChainLadder`` 
development model for now, but the data get's stale and thin after the 
first few years, so we'll switch to a tail model after a development 
lag of 84 months. We expect that new loss development is more predictive
of future loss development patterns, so we can add exponential recency decay
based on the evaluation date.

..  code:: python

    chain_ladder = client.development_model.create(
        triangle="meyers_triangle",
        name="paid_body_development",
        model_type="ChainLadder",
        model_config={
            "loss_definition": "paid",
            "recency_decay": 0.8
        }
    )

Now we'll need to fit a tail model to account for lags after 72 months. For this we'll
use a ``GeneralizedBondy`` model which is a generalization of the classic Bondy model.

..  code:: python

    bondy = client.tail_model.create(
        triangle="meyers_triangle",
        name="paid_bondy",
        model_type="GeneralizedBondy",
        model_config={
            "loss_definition": "paid",
        }
    )

Now we can square this triangle using a combination of body development via the ``chain_ladder`` model and
tail development using bondy. Note that by default the prediction triangle will be named ``"paid_body_meyers_triangle"`` based on the ``model_name`` and the triangle name. You have the option of passing in a different ``prediction_name`` to the ``predict`` method that will save the output triangle with a user-specified name.

.. code:: python

    chain_ladder_predictions = chain_ladder.predict(
        triangle="meyers_triangle",
        config={"max_dev_lag": 84},
    )

    chain_ladder_predictions.to_bermuda().plot_data_completeness()

.. image:: chain_ladder_prediction.png

From the data completeness plot you can see the predictions out to dev lag 84 months. Now
we can apply the bondy model to a combination of these predcitions and the original triangle.

.. image:: tail_prediction_base.png


.. code:: python

   tail_prediction_base = clipped_meyers + chain_ladder_predictions.to_bermuda()
   tail_prediction_base.plot_data_completeness()

   client.triangle.create(name="tail_prediction_base", data=tail_prediction_base)

   bondy_predictions = bondy.predict(
       triangle="tail_prediction_base",
       config={"max_dev_lag": 120}
   )

   squared_triangle = tail_prediction_base + bondy_predictions.to_bermuda()
   squared_triangle.plot_data_completeness()

The tail model predictions take us from lag 84 to lag 120.

.. image:: tail_predictions.png

This combined with the original triangle and chain ladder predictions gives the full squared triangle.

.. image:: squared_triangle.png

For each future cell in the triangle there is a posterior distribution off 10,000 samples of paid losses.These distributions can be fed directly into a forecast model to predict the ultimate loss ratios for a future accident year. Reserves can be set using a selected quantile from these ultimate loss distributions.


