Quick Start
============================

Once you've received your API key and installed ``ledger-analytics``
you are ready to start using our models and triangle
data structures.

``AnalyticsClient`` class
---------------------------

Users interact with our endpoints via the ``AnalyticsClient`` class.
This class either accepts your API key directly as a ``str`` on
instantiation, or looks for the ``LEDGER_ANALYTICS_API_KEY``
environment variable. Generally, we'd prefer setting the latter.

..  code:: python

    from ledger_analytics import AnalyticsClient

    client = AnalyticsClient()

    # alternatively
    api_key = "..."
    client = AnalyticsClient(api_key)

You can test the API key is authorized by using:

..  code:: python

    >>> client.test_endpoint()
    'Endpoint working!'

If you receive a ``HTTPError``, the API key is likely not correct.
See the debugging tips on the `Requesting API Keys <apikeys.rst>`_
page for more information.


Triangles
--------------

We'll start by creating a new
triangle object from the ``meyers_tri`` available
in the `Bermuda <https://github.com/LedgerInvesting/bermuda-ledger>`_
library.

..  code:: python

    from bermuda import meyers_tri
    from datetime import date

    meyers_tri.plot_data_completeness()
    clipped_meyers = meyers_tri.clip(max_eval=date(1997, 12, 31)) 
    clipped_meyers.plot_data_completeness()

We split the 10x10 triangle into a typical 55-cell loss
development triangle using Bermuda's ``Triangle.clip`` method.

We can now use the ``client`` instance above to create the
triangle in the remote database.

..  important::

    Your API key is unique to you within your organization,
    and so you will only be able to access triangles and models
    created by your organization. Created triangles and models
    are unique to your organization. Other users within your 
    organization have the ability to overwrite your triangles
    and models.

..  code:: python

    triangle = client.triangle.create(name="meyers_triangle", data=clipped_meyers)

Alternatively, we could have passed a dictionary of data to the ``triangle_data``
argument of the Bermuda JSON format returned by ``bermuda.Triangle.to_dict``,
e.g. ``clipped_meyers.to_dict()``. Thus, Bermuda is not required to use our
endpoints, although makes integration much easier.

The ``triangle`` object is now an instance of ``ledger_analytics.Triangle``,
and holds attributes such as it's unique ID (``triangle.triangle_id``),
name (``triangle.triangle_name``), data (``triangle.triangle_data``)
or API endpoint (``triangle.endpoint``).

If you wanted to retrieve a triangle that is already present in the database,
you can use the following GET request:

..  code:: python

    >>> triangle_get = client.triangle.get(name="meyers_triangle")
    [08:42:03] Getting triangle 'meyers_triangle' with ID 'triangle2ucSk7MTN5QNjzjleT0TZ8uWCWu'              triangle.py:48

Note, the triangle ID above will not match your triangle ID.

LedgerAnalytics ``Triangle`` instances can be converted to Bermuda's ``Triangle`` classes using
the convenient ``ledger_analytics.Triangle.to_bermuda`` method:

..  code:: python

    >>> triangle.to_bermuda()
           Cumulative Triangle 

     Number of slices:  1 
     Number of cells:  55 
     Triangle category:  Regular 
     Experience range:  1988-01-01/1997-12-31 
     Experience resolution:  12 
     Evaluation range:  1988-12-31/1997-12-31 
     Evaluation resolution:  12 
     Dev Lag range:  0.0 - 108.0 months 
     Fields: 
       earned_premium
       paid_loss
       reported_loss
     Common Metadata: 
       currency  USD 
       country  US 
       risk_basis  Accident 
       reinsurance_basis  Net 
       loss_definition  Loss+DCC

You can see all triangles that you can access using the ``list`` method:

..  code:: python

    client.triangle.list()

Fitting models
---------------------

The ``AnalyticsClient`` class allows us to easily fit, and predict from,
development, tail and forecast models. Here's how to fit a simple Bayesian chain
ladder model to the triangle we created above.

..  danger::

    Note, the following code will fit a remote model to a triangle and use compute credits.

..  code:: python

    chain_ladder = client.development_model.create(
        triangle="meyers_triangle",
        name="development",
        model_type="ChainLadder",
    )
    [08:43:50] Fitting model 'development' on triangle 'meyers_triangle': PENDING                             model.py:171
    [ ===] Working...
    ...
    [08:44:46] Fitting model 'development' on triangle 'meyers_triangle': FINISHED

You will see a convenient status bar keeping you up-to-date with the model
fitting progress, which is currently in three stages: ``CREATED``, ``PENDING``
and ``FINISHED``. The latter stage could be ``FAILURE``, ``TERMINATED`` or ``TIMEOUT``
if errors occur. When running a model in a new session, it will take a small bit of time to 
instantiate the computing service and compile the model. 
If you are running multiple models, however,
our remote compute service will become more efficient.

Cancelling fits
^^^^^^^^^^^^^^^^^^^^

If you need to terminate a fit, you can use the ``LedgerModel.terminate``
method:

.. code:: python

   chain_ladder.terminate()

   # alternatively 
   client.development_model.terminate(name="development")

Model types
^^^^^^^^^^^^^

In addition to listing fitted models, you can inspect our available library of models
using the ``list_model_types`` method:

..  code:: python

    client.development_model.list_model_types()
    client.tail_model.list_model_types()
    client.forecast_model.list_model_types()

Predictions
^^^^^^^^^^^^^
Once the model has been created and fit, you can make predictions.

..  code:: python

   predictions = chain_ladder.predict(triangle="meyers_triangle")

The ``chain_ladder`` model object will now contain a ``predict_response``
attribute, which is a raw ``requests.Response`` instance. The ``predict`` method
returns a ``ledger_analytics.Triangle`` object, which can be converted to a Bermuda
triangle object using the ``to_bermuda`` method. It can be saved out in various formats
including a binary file or as a wide CSV file.

..  code:: python

    >>> predictions.to_bermuda()

           Cumulative Triangle 


     Number of slices:  1 
     Number of cells:  45 
     Triangle category:  Regular 
     Experience range:  1989-01-01/1997-12-31 
     Experience resolution:  12 
     Evaluation range:  1998-12-31/2006-12-31 
     Evaluation resolution:  12 
     Dev Lag range:  12.0 - 108.0 months 
     Fields: 
       earned_premium
       paid_loss
     Common Metadata: 
       currency  USD 
       country  US 
       risk_basis  Accident 
       reinsurance_basis  Net 
       loss_definition  Loss+DCC

    >>> predictions.to_binary('predictions.trib')
    >>> predictions.to_wide_csv('predictions.csv')

Our predicted triangle holds, by default, 10,000 samples from the posterior predictive
distribution of ``paid_loss``.

`See our bermuda documention for more information on bermuda triangle objects. <https://ledger-investing-bermuda-ledger.readthedocs-hosted.com/en/latest/?badge=latest>`_

Like triangles above, we can inspect available models you've fit and have access to
using the ``list`` method:

..  code:: python

    client.development_model.list()
    client.tail_model.list()
    client.forecast_model.list()

