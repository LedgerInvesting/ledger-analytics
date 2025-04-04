Meyers Cross Classified Model (``MeyersCRC``)
---------------------------------------------

This model represents a generalization of the Cross Classified (CRC) Model presented in the 2019 
CAS monograph "Stochastic Loss Reserving Using Bayesian MCMC Models, 2nd Edition". The CRC model
breaks losses down into development and experience period components, where the loss for any 
given accident period at a given development lag is assumed to be a function of the unique factors 
associated with the period/lag combination. 

Our implementation in the ``MeyersCRC`` model type is expressed mathematically as:

.. math::
    \begin{align}
        \mathrm{LR}_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \quad{\forall j \in (1, \tau]}\\
        \mu_{ij} &= \exp(\mathrm{LR}_{\text{expected}} + \beta_{\text{lag},j} + \beta_{\text{year},i})\\
        \sigma_{ij}^2 &= \exp(\sigma_{\text{int}} + \sigma_{\text{slope}} j - \log(\mathrm{EP}_{i}))\\
        \mathrm{LR}_{\text{expected}} &\sim \mathrm{Normal}(\mathrm{LR}_{\text{expected}, \text{loc}}, \mathrm{LR}_{\text{expected}, \text{scale}})\\
        \log \boldsymbol{\beta_{\text{lag}}} &\sim \mathrm{Normal}(\beta_{\text{lag}, \text{loc}}, 
        \beta_{\text{lag}, \text{scale}})\\
        \log \boldsymbol{\beta_{\text{year}}} &\sim \mathrm{Normal}(\beta_{\text{year}, \text{loc}}, \beta_{\text{year}, \text{scale}})\\
        \sigma_{\text{int}} &\sim \mathrm{Normal}(\sigma_{\text{int}, \text{loc}}, \sigma_{\text{int}, \text{scale}})\\
        \sigma_{\text{slope}} &\sim \mathrm{Normal}(\sigma_{\text{slope}, \text{loc}}, \sigma_{\text{slope}, \text{scale}})\\
        \mathrm{LR}_{\text{expected}, \text{loc}} &= -0.4\\
        \mathrm{LR}_{\text{expected}, \text{scale}} &= \sqrt{10}\\
        \beta_{\text{lag}, \text{loc}} &= 0.0\\
        \beta_{\text{lag}, \text{scale}} &= \sqrt{10}\\
        \beta_{\text{year}, \text{loc}} &= 0.0\\
        \beta_{\text{year}, \text{scale}} &= \sqrt{10}\\
        \sigma_{\text{int}, \text{loc}} &= 0.0\\
        \sigma_{\text{int}, \text{scale}} &= 3.0\\
        \sigma_{\text{slope}, \text{loc}} &= 0.0\\
        \sigma_{\text{slope}, \text{scale}} &= 1.0
    \end{align}

Unlike other loss development models, the ``MeyersCRC`` model does not estimate age-to-age factors
directly, although implied factors can be derived post-hoc. Instead, expected losses are determined 
as the product of a general expected losses term, a development lag factor, and an accident period 
factor. :math:`\tau \in {2,...,M}` is an integer chosen by an analyst that indicates how many 
development lags should be used to fit the model to, and :math:`\mathrm{Gamma(\mu, \sigma^2)}` is 
the mean-variance parameterization of the Gamma distribution. In practice, :math:`\tau` is 
determined by preprocessing (i.e. clipping) the triangle before fitting. 

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``MeyersCRC`` model is fit using the following API call: 

.. code-block:: python

    model = client.development_model.create(
        triangle=...,
        name="example_name",
        model_type="MeyersCRC",
        config={ # default model_config
            "loss_definition": "paid",
            "loss_family": "gamma",
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``MeyersCRC`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"paid"``.
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
       "logelr__loc": -0.4, # expected log loss ratio
        "logelr__scale": np.sqrt(10),
        "lag_factor__loc": 0.0,
        "lag_factor__scale": np.sqrt(10),
        "year_factor__loc": 0.0,
        "year_factor__scale": np.sqrt(10),
        "sigma_intercept__loc": 0.0,
        "sigma_intercept__scale": 3.0,
        "sigma_slope__loc": 1.0,
        "sigma_slope__scale": 1.0
    }

- ``recency_decay``: Likelihood weight decay to down-weight data from older evaluation dates. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older evaluation dates will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.


Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``MeyersCRC`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.development_model.predict(
        triangle=...,
        config={ # default config
            "max_dev_lag": None,
            "include_process_noise": True,
        }
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle that was used in model fitting, and setting ``target_triangle=None`` will create a squared version of the modeled triangle. However, decoupling ``triangle`` and ``target_triangle`` means users could train the model on one triangle, and then make predictions starting from and/or on a different triangle. By default, predictions will be made out to the maximum development lag in ``triangle``, but users can also set ``max_dev_lag`` in the configuration directly.

The ``MeyersCRC`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag in ``triangle``. Note that ``MeyersCRC`` can only generative predictions out to the maximum development lag in the training triangle, as there is no mechanism in the model to extrapolate out age-to-age beyond the training data.
- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation :math:`\mu_{ij}` as predictions as oppposed to :math:`LR_{ij}`.
