# ledger-analytics

`ledger-analytics` is the Python interface to Ledger Investing's remote
analytics infrastructure.

To use with a local app (which should be running on `localhost:8000`),
set your `LEDGER_ANALYTICS_API_KEY` environment variable.

The typical Python workflow is, then:

```python
from ledger_analytics import AnalyticsClient
from bermuda import meyers_tri

client = AnalyticsClient()

# Post a new triangle object
triangle = client.triangle.create(
    config=dict(
        triangle_name="test_meyers_triangle",
        triangle_data=meyers_tri.to_dict(),
    )
)

# Get the Bermuda Triangle object
bermuda_triangle = triangle.get()

# Fit a development model
dev_model = client.development_model.fit(
   config={
       "triangle_name": "test_meyers_triangle",
       "model_name": "chain_ladder",
       "model_type": "ChainLadder",
       "model_config": {},
    )
)

# delete triangle
triangle.delete()
```

The `LegderAnalytics` class can also be used as a simple context manager:

```python
from ledger_analytics import LedgerAnalytics

with AnalyticsClient() as client:
    triangle = client.triangle.create(
        config={
            "triangle_name": "test_meyers_triangle",
            "triangle_data": meyers_tri.to_dict(),
        )
    )
    triangle.delete()
```
