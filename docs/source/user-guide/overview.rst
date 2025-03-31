Overview
==============

LedgerAnalytics offers easy access to Ledger Investing's
modeling API endpoints via Python. If you are fitting loss development models
and/or pricing insurance-linked securities, LedgerAnalytics provides
state-of-the-art insurance data science tools to make loss ratio
predictions, estimate uncertainty and securitize insurance programs. 

We are currently building the functionality of LedgerAnalytics and looking
for beta testers!

Below is a summary of the current endpoints of basic functionality. This User Guide
contains more specific details on model usage.

Endpoints and workflow
------------------------

At a high level, LedgerAnalytics provides three main category of endpoints:

* The triangle endpoint, which handles basic CRUD operations on triangle objects. LedgerAnalytics
  interacts nicely with our triangle Python library, `Bermuda <https://ledger-investing-bermuda-ledger.readthedocs-hosted.com/en/latest/?badge=latest>`_.
* Model fit endpoints, which allow fitting models to triangle data.
  The models include loss development, tail development and forecasting models.
* Model predict endpoints, which allow predicting from fitted models and retrieving the
  predicted triangle for any downstream computations.

The intended workflow for users of LedgerAnalytics is to load a triangle into Python,
ideally using the Bermuda package, creating that triangle in the database
using the triangle endpoints, fitting a model or models to that triangle,
and making predictions which can be used for downstream computations. 
Bermuda and our modelling endpoints accept data as 
both static point estimates (e.g. raw historical data) or samples from
distributions as standard.

Security and permissions
-------------------------

Accessing LedgerAnalytics requires requesting access via
analytics@ledgerinvesting.com and following the instructions
at the emailed sign-up link. From there, you can create API
keys used by LedgerAnalytics to authenticate HTTP requests.

Users are tied to organizations, and users can only access
triangles and models within their organization.

Generic usage & syntax
-----------------------

There are certain aspects of the LedgerAnalytics syntax 
that are useful to introduce at a high level.
First, the gateway to using the API is via the ``AnalyticsClient``
class, which can be instantiated using:

..  code:: python

    from ledger_analytics import AnalyticsClience

    client = AnalyticsClient(api_key="...")

Alternatively, users can set the ``LEDGER_ANALYTICS_API_KEY``
environment variable rather than passing the API key as a string
to the class constructor.

The client acts as an interface to triangle and model endpoints via
the specific ``ledger_analytics.Triange`` and ``ledger_analytics.LedgerModel``
classes.
Here are some common usage examples, along with their return values:

..  code:: python

    from bermuda import meyers_tri
    from bermuda import Triangle as BermudaTriangle

    from ledger_analytics import Triangle, DevelopmentModel

    triangle: Triangle = client.triangle.create(
        name="meyers_triangle", 
        data=meyers_tri.to_dict()
    )

    bermuda_triangle: BermudaTriangle = triangle.to_bermuda()

    development: DevelopmentModel = client.development_model.create(
        name="development",
        model_type="ChainLadder",
        triangle=triangle,
    )

    squared_triangle: Triangle = development.predict(triangle=triangle)

Fit & predict workflows
-------------------------

LedgerAnalytics opens access to a variety of model types, but the fit/predict
syntax is similar between all endpoints.

As shown in the previous section, models are fit using the ``create`` method,
which has the generic function signature:

..  code:: python

    client.<model_type>.create(
        name="...",
        model_type="...",
        triangle=...,
        config={...},
    )

where ``model_type`` can be ``development_model``, ``tail_model`` or ``forecast_model``.
The ``config`` dictionary varies by each model type, and is explained more in the model-specific
pages of this User Guide.

Similarly, the ``predict`` step has the generic signature:

..  code:: python

    model: LedgerModel = ...

    model.predict(triangle=..., config={...}, target_triangle=...)

where the ``config`` is a dictionary of model-specific configuration parameters,
and ``target_triangle`` is an optional triangle to make predictions on.
The latter allows a decoupling between the triangle used to fit the model,
and the triangle used to make predictions. For instance, the following 
example fits a (fake) model to one triangle and predicts on another:

..  code:: python

    model = client.development_model.create(
        name="development",
        model_type="ChainLadder",
        triangle=reference_triangle,
    )

    predictions = model.predict(
        triangle=initial_triangle,
        target_triangle=pred_triangle,
    )

where ``reference_triangle`` is some triangle to model,
``initial_triangle`` is a triangle to start the predictions
from (e.g. a typical upper-diagonal triangle used for loss
development modeling), 
and ``pred_triangle`` is the actual triangle we want to 
make predictions on. 
