Autoregressive Lag 1 Model (``AR1``)
------------------------------------

The autoregressive lag 1 (AR1) model is a standard autogression model that is meant to be used to 
model changes in (ultimate) loss ratios across accident periods. The AR1 model assumes that the 
current loss ratio is a function of the previous loss ratio (i.e. auto-regression), the degree to 
which is controlled by a reversion parameter. Our AR1 model is implemented in the by the ``AR1`` 
model type, which is expressed mathematically as:

.. math:: 
    \begin{align*}
        \mathrm{LR}_{i} &\sim \mathrm{Gamma}(\eta_{i}, \sigma_{i}^2)\\
        \eta_{i} &= (1 - \phi_{\text{reversion}}) \mathrm{LR}_{\text{target}} + \phi_{\text{reversion}} \mathrm{LR}_{i - 1}\\
        \sigma_{i}^2 &= \sigma_{\text{base}} + \sigma_{\text{obs}} / \mathrm{EP}_i\\
        \phi_{\text{reversion}} &= \mathrm{logit}^{-1}(\phi_{\text{reversion}}^{*}) \cdot 2 - 1\\
        \phi_{\text{reversion}}^{*} &\sim \mathrm{Normal}(\phi_{\text{reversion}, \text{loc}}, \phi_{\text{reversion}, \text{scale}})\\
        \log \mathrm{LR}_{\text{target}} &\sim \mathrm{Normal}(\mathrm{LR}_{\text{target}, \text{loc}}, \mathrm{LR}_{\text{target}, \text{scale}})\\
        \log \sigma_{\text{base}} &\sim \mathrm{Normal}(\sigma_{\text{base}, \text{loc}}, \sigma_{\text{base}, \text{scale}})\\
        \log \sigma_{\text{obs}} &\sim \mathrm{Normal}(\sigma_{\text{obs}, \text{loc}}, \sigma_{\text{obs}, \text{scale}})\\
        \phi_{\text{reversion}, \text{loc}} &= 0.0\\
        \phi_{\text{reversion}, \text{scale}} &= 1.0\\
        \mathrm{LR}_{\text{target}, \text{loc}} &= -0.5\\
        \mathrm{LR}_{\text{target}, \text{scale}} &= 1.0\\
        \sigma_{\text{base}, \text{loc}} &= -2.0\\
        \sigma_{\text{base}, \text{scale}} &= 1.0\\
        \sigma_{\text{obs}, \text{loc}} &= -2.0\\
        \sigma_{\text{obs}, \text{scale}} &= 1.0
    \end{align*}

where :math:`\mathrm{LR}_i` indicates the observed loss ratio for accidenty year :math:`i`, and 
:math:`mathrm{EP}_i` is the *earned premium* for the same accident period. The model is specified 
such that :math:`\eta_i` is the expected loss ratio for each accident period, and the observed loss 
ratios are then assumed to be Gamma distributed where :math:`\mathrm{Gamma(\eta_i, \sigma_{i}^2)}` 
is the mean-variance parameterization of the Gamma distribution.  

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``AR1`` model is fit using the following API call: 

.. code-block:: python

    model = client.forecast_model.create(
        triangle=...,
        name="example_name",
        model_type="AR1",
        config={ # default model_config
            "loss_definition": "reported",
            "loss_family": "gamma",
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``AR1`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"reported"``.
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "reversion__loc": 0.0,
        "reversion__scale": 1.0,
        "base_sigma__loc": -2.0,
        "base_sigma__scale": 1.0,
        "obs_sigma__loc": -2.0,
        "obs_sigma__scale": 1.0,
        "target_lr__loc": -0.5,
        "target_lr__scale": 1.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight older experience periods. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older experience periods will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.

Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``AR1`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.forecast_model.predict(
        triangle=...,
        config={ # default config
            "include_process_noise": True,
        }
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` 
is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle 
that was used in model fitting, and ``target_triangle`` should be specified to include future 
accident periods (including earned premium values) that forecasts should be made on.

The ``AR1`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation :math:`\eta_{i}` as predictions as oppposed to :math:`\mathrm{LR}_{i}`.