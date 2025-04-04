Troubleshooting
----------------


Triangles
^^^^^^^^^^^^
When creating a triangle, you may receive the following error messages

.. code:: python

    HTTPError: 400: Bad request, {'error': 'Failed to validate triangle data: Bermuda triangles can only hold `Cell`s'}.

Be sure you're passing a bermuda triangle object to the ``data`` argument of the ``client.triangle.create`` method.

.. code:: python

    ValueError: No triangle found with name 'foo'.

This error indicates that the triangle you are trying to access does not exist. Run ``client.triangle.list()`` to see a list of triangles you have access to.  

Model Fit
^^^^^^^^^^^^^^^
When creating a model, you may receive the following error messages

.. code:: python

    HTTPError: 400: Bad request, ['Model type chainladder not found.'].

This error indicates that the model type you are trying to create does not exist. Run ``client.{model_category}.list()`` (where model_category is in ['development', 'tail', 'forecast']) to see a list of models you have access to. Pay attention to capitalization. 


.. code:: python

    HTTPError: 400: Bad request, ['Triangle Meyers_triangle not found.'].

This error indicates that the triangle you are trying to access does not exist. Run ``client.triangle.list()`` to see a list of triangles you have access to.

.. code:: python

    ValueError: Task failed: Error fitting development model ChainLadder: TypeError("'<=' not supported between instances of 'int' and 'str'")

Any error beginning with ``ValueError: Task failed:`` indicates a model failed at fit time. This could be due to bad model configuration or triangle data that doesn't fit the model's assumptions. Check the documentation for the individual model to ensure the configuration matches the spec, and be sure the triangle data satisfies the model's assumptions.

.. code:: python

    ValueError: Task failed: Error fitting forecast model TraditionalGcc: KeyError('Field `incurred_loss` does not exist in this `CumulativeCell`')

This error indicates that the model you are trying to fit is looking for a field that does not exist in the triangle. If you intended to fit the model to another loss metric instead, change the ``loss_definition`` in the config ``config = {"loss_definition": "paid"}``.

Model Prediction
^^^^^^^^^^^^^^^^^^^^
When predicting from a model, you may receive the following error messages

.. code:: python

    HTTPError: 400: Bad request, ['Triangle Meyers_triangle not found.'].

This error indicates that the triangle you are trying to access does not exist. Run ``client.triangle.list()`` to see a list of triangles you have access to.

.. code:: python

    ValueError: Task failed: Error predicting development model s3://dev-ledger-platform-api-files/model/1909f7a4-d300-4fc4-950c-9f5fd00dc245.pkl: IndexError('list index out of range')

Any error beginning with ``ValueError: Task failed:`` indicates a model failed at prediction time. This could be due to bad model configuration or triangle data that doesn't fit the model's assumptions. Check the documentation for the individual model to ensure the configuration matches the spec, and be sure the triangle data satisfies the model's assumptions.

In particular a ``list index out of range`` error typically indicates a development model is being asked to predict cells outside of the models development lag range.

.. code:: python

    ValueError: Task failed: Error predicting forecast model s3://dev-ledger-platform-api-files/model/3d2f662a-eccb-4e0c-9721-7d1b9a7316a4.pkl: TypeError("TraditionalGcc.predict() missing 1 required keyword-only argument: 'target_triangle'")

This error indicates that you need to pass in a target triangle, typically for a forecast prediction model. The target triangle is essential for passing in information about which future period to make predictions for, and providing an assumption about premium volume to scale the volatility appropriately. The easiest way to create a target triangle is to modify a cell from the fit triangle using some code like the following

.. code:: python

    from datetime import date

    target = tri.Triangle([
        meyers_tri[-1].replace(
            period_start=date(1998, 1, 1), 
            period_end=date(1998, 12, 31), 
            evaluation_date=date(1998, 12, 31), 
            values= {'earned_premium':5e6})
    ])
    client.triangle.create('target', target)

    gcc.predict('meyers', target_triangle='target')


.. code:: python

    ValueError: Task failed: Error predicting forecast model s3://dev-ledger-platform-api-files/model/3d2f662a-eccb-4e0c-9721-7d1b9a7316a4.pkl: ModelPredictError('This model cannot forecast loss ratios for the requested slice')

The error above indicates that the model the data was fit to has metadata that doesn't match the metadata of the target triangle. It could be the case that the data is actually materially different and you shouldn't be trying to make predictions on this data (e.g. predicting policy year data from a model fit to accident year data), or it could be that your metadata is just slightly different in an immaterial way. If you're sure the problem is due to the latter, you can modify the metadata of your target triangle to match the metadata of the triangle you fit the model to using something like the following


.. code:: python
   
    fit_metadata = fit_triangle.metadata[0]
    target = target.replace(metadata=fit_metadata)
    client.triangle.create('target', target)
