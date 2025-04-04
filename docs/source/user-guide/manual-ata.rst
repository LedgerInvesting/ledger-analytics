Manual Age-To-Age Factor Model (``ManualATA``)
----------------------------------------------

The Manual age-to-age factor model is different from other loss development models in that it uses
hard-coded age-to-age factors passed in by the user, rather than estimating them from the data.
The model otherwise behaves the same as other loss development models.

The primary intended use case of this model is for supporting workflows where age-to-age factors are 
selected or adjusted by hand, or age-to-age factors are provided by a bureau or other external 
source without any supporting data behind them. Our implementation in the ``ManualATA`` model type is
expressed mathematically as:

.. math::
    \begin{align}
        y_{ij} &= \mu_{ij}\\
        \mu_{ij} &= ATA_{j - 1} y_{ij-1}\\
        \bf{ATA} &= \text{user input}\\
    \end{align}

where :math:`\bf{ATA}` is a vector of *age-to-age factors* that are hard-coded by the user.  

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

Although there are no parameters to estimate in the model, the API still follows the convention of
other development models. The ``ManualATA`` model is "fit" using the following API call: 

.. code-block:: python

    model = client.development_model.create(
        triangle=...,
        name="example_name",
        model_type="ManualATA",
        config={ # default model_config
            "ata_factors": [...],
            "loss_definition": "paid",
            "development_resolution": 12,
            "development_offset": 0
        }
    )

The ``ManualATA`` model accepts the following configuration parameters in ``config``:

- ``ata_factors``: A list of age-to-age development factors. If ``development_resolution`` is 3 and ``development_offset`` is 6, then the first factor in the list should be a 6-to-9 month ATA, the second factor should be a 9-to-12 month ATA, and so forth.
- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"paid"``.
- ``development_resolution``: The number of months between development lags of successive development factors.
- ``development_offset``: The development lag (in months) of the first development factor provided.


Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``ManualATA`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.development_model.predict(
        triangle=...,
        config={ # default config
            "max_dev_lag": None,
        }
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` 
is the triangle to make predictions on. Unlike other models, since that model is not initially 
fitted to a training triangle,  By default, predictions will be made out to the maximum development lag in ``triangle``, but users can also set ``max_dev_lag`` in the configuration directly.

The ``ManualATA`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag available per the ``triangle``, ``target_triangle``, and ``ata_factors`` specified.