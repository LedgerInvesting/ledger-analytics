# LedgerAnalytics Python

`ledger-analytics` is the upcoming Python interface to [Ledger Investing](https://ledgerinvesting.com)'s remote
analytics infrastructure.

## Examples

```python
from ledger_analytics import AnalyticsClient

client = AnalyticsClient()

# development model types
client.development_model.list_model_types()

# your triangles
client.triangle.list()

# fit a model
model = client.development_model.fit(model_name="test_model", triangle_name="meyers_clipped", model_type="ChainLadder")
model.predict()
```
