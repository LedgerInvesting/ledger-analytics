Generalized Cape Cod Model (``TraditionalGCC``)
-----------------------------------------------

The Cape Cod method is a popoular deterministic method for forecasting ultimate losses use by 
actuaries when estimating loss reserves. Our Generalized Cape Cod model is based on the Cape Cod 
method, which assumes that the latent loss ratio for a given accident period is taken to be a 
weighted mean of all other loss ratios (both past and future). The weight is determined by earned 
premium volume, leverage on ATA factors, and temporal distance from accident period in question. Our 
``TraditionalGCC`` model type implements the model, which is expressed mathematically as:

.. math:: 
    \begin{align*}
        \widehat{\mathrm{LR}}_i &= \frac{\sum_{k=1}^N \mathrm{LR}_k \cdot \mathrm{UEP}_k \cdot \beta^{\lvert k - i\rvert}}{\sum_{k=1}^N \mathrm{UEP}_k \cdot \beta^{\lvert k - i\rvert}}\\
        \mathrm{UEP}_i &= \mathrm{EP}_i \frac{\mathrm{LR}_{\text{obs},i}}{\mathrm{LR}_{i}}\\
        \beta &= \text{user input} \in (0, 1]
    \end{align*}

where :math:`\widehat{\mathbf{LR}}` is the model predicted loss ratio, :math:`\mathrm{LR}_i` is the 
estimated ultimate loss ratio for each accident period :math:`i` (which serves as input to the 
model), :math:`\mathrm{LR}_{\text{obs},i}` is the latest *observed* loss ratio for accident period 
:math:`i`, and :math:`\mathrm{UEP}_i` is the *used earned premium* for accident period :math:`i`. 
The used earned premium is calculated as the earned premium for the accident period multiplied by 
the ratio of observed to estimated ultimate losses. Therefore, used earned premium is lower for more 
recent accident periods. 

The recency decay parameter :math:`\beta` is a user-specified parameter that determines how steeply 
decay should occur across accident periods. A value of :math:`\beta = 1` indicates no decay such that
the predicted losses are simply the average of all accident period loss ratios. A value close to 
:math:`\beta \approx 0` will put all the weight on the most recent accident period.

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``TraditionalGCC`` model is fit using the following API call: 

.. code-block:: python

    model = client.forecast_model.create(
        triangle=...,
        name="example_name",
        model_type="TraditionalGCC",
        config={ # default model_config
            "loss_definition": "incurred",
            "recency_decay": 0.9, # beta parameter above
        }
    )

The ``TraditionalGCC`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"incurred"``.
- ``recency_decay``: For the ``TraditionalGCC`` model, ``recency_decay`` corresponds directly to the :math:`\beta` parameter in the mathematical expression above. Defaults to ``0.9``, which indicates that periods 1 year away get 90% weight, periods two years away would get 81% weight, and so forth.

Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``TraditionalGCC`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.forecast_model.predict(
        triangle=...,
        config={}, # no extra config options
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` 
is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle 
that was used in model fitting, and ``target_triangle`` should be specified to include future 
accident periods (including earned premium values) that forecasts should be made on.