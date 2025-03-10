# ledger-analytics

`ledger-analytics` is the Python interface to Ledger Investing's remote
analytics infrastructure.

To use with a local app (which should be running on `localhost:8000`),
set your `LEDGER_ANALYTICS_API_KEY` environment variable.

The typical Python workflow is, then:

```python
from ledger_analytics import LedgerAnalytics
from bermuda import meyers_tri

client = LedgerAnalytics()

# Post a new triangle object
triangle_response = client.triangle.create(
    config=dict(
        triangle_name="test_meyers_triangle",
        triangle_data=meyers_tri.to_dict(),
    )
)

# Get the Bermuda Triangle object
triangle_response.get()

# Fit a development model
dev_model = client.development_model.fit(
   config=dict(
       triangle_name="test_meyers_triangle",
       model_name="chain_ladder",
       model_type="ChainLadder",
       model_config={},
    )
)

# check status
dev_model.status()

# delete triangle
triangle_response.delete()
```

The `LegderAnalytics` class can also be used as a simple context manager:

```python
from ledger_analytics import LedgerAnalytics

with LedgerAnalytics as client:
    triangle_response = client.triangle.create(
        config=dict(
            triangle_name="test_meyers_triangle",
            triangle_data=meyers_tri.to_dict(),
        )
    )
    triangle_response.delete()
```
        
