Generalized Bondy Model (``GeneralizedBondy``)
----------------------------------------------

Our Generalized Bondy model is a generalization of the Bondy method used by actuaries to
estimate ultimate losses given histoic development patterns. Whereas the Bondy method is
typically performed given age-to-age factors as input, our Generalized Bondy model is fitted
directly to the triangle of interest. The Generalized Bondy model is implemented by the
``GeneralizedBondy`` model type, and is expressed mathematically as:

.. math::

    \begin{align}
        \begin{split}
            \mathrm{LR}_{ij} &\sim \mathrm{Gamma(\mu_{ij}, \sigma_{ij}^2)}\\
            \mu_{ij} &= ATA_{j} y_{ij - 1}\\
            ATA_{j} &= \exp( ATA_{\text{init}} \beta^{j} )\\
            \sigma_{ij}^2 &= \exp(\sigma_{\text{int}} + \sigma_{\text{slope}} j - \log(\mathrm{EP}_{i})), \quad{\forall j \in [\rho_1, \rho_2]}\\
            \log ATA_{\text{init}} &\sim \mathrm{Normal}(ATA_{\text{init}, \text{loc}}, ATA_{\text{init}, \text{scale}})\\
            \log \frac{\beta}{1 - \beta} &\sim \mathrm{Normal}(\beta_{\text{loc}}, \beta_{\text{scale}})\\
            \sigma_{\text{int}} &\sim \mathrm{Normal}(\sigma_{\text{int}, \text{loc}}, \sigma_{\text{int}, \text{scale}})\\
            \sigma_{\text{slope}} &\sim \mathrm{Normal}(\sigma_{\text{slope}, \text{loc}}, \sigma_{\text{slope}, \text{scale}})\\
            ATA_{\text{init}, \text{loc}} &= 0\\
            ATA_{\text{init}, \text{scale}} &= 1\\
            \beta_{\text{loc}} &= 0\\
            \beta_{\text{scale}} &= .3\\
            \sigma_{\text{int}, \text{loc}} &= 0\\
            \sigma_{\text{int}, \text{scale}} &= 3\\
            \sigma_{\text{slope}, \text{loc}} &= -.6\\
            \sigma_{\text{slope}, \text{scale}} &= .3
        \end{split}
    \end{align}

where :math:`\bf{ATA}` is a vector of *age-to-age factors* that capture how losses change across
development and :math:`\mathrm{EP}_{i}` is the total earned premium for the given accident period. 
Instead of being estimated as independent parameters as in the ``ChainLadder`` model, here the 
age-to-age factors are modeled as a function of two parameters, :math:`ATA_{\text{init}}` and 
:math:`\beta`. The parameter :math:`ATA_{\text{init}}` can be interpreted as the *initial* 
age-to-age factor, and :math:`\beta` as the *rate of decay* in the age-to-age factors across 
development. Because :math:`\log ATA_{\text{init}}` is constrained to be positive, as development 
increases, the lowest value an age-to-age factor can take on is 1 (at which point development has reached an asymptote). 

Typically, the Generalized Bondy model is fitted to only the window of development lags 
:math:`j \in [\rho_1, \rho_2]`, where :math:`(\rho_1, \rho_2) \in {2,...,M}, \rho_1 < \rho_2`, are 
chosen by an analyst based on where the tail process is assumed to begin and end. In practice, this 
can be accomplished my mutating/clipping the triangle as a preprocessing step before fitting.

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``GeneralizedBondy`` model above is fit using the following API call:

.. code-block:: python

    model = client.tail_model.create(
        triangle=...,
        name="example_name",
        model_type="GeneralizedBondy",
        config={ # default model_config
            "loss_definition": "reported",
            "loss_family": "gamma",
            "line_of_business": None,
            "informed_priors_version": None,
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``GeneralizedBondy`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"reported"``.
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``line_of_business``: Line of business that the input triangle belongs to. If specified, backtest-informed priors leveraging industry data are used to fit the model. Must be preovided if ``informed_priors_version`` is specified. Otherwise, defaults to ``None`` and the default priors below are used. Supported lines include: ``["CA", "MC", "MO", "OO", "PC", "PO", "PP", "SL", "WC"]``. Abbreviations map to the following lines: 

.. code-block:: python

    {
        "CA": "Commercial Auto Liability",
        "MC": "Medical Liability: Claims Made",
        "MO": "Medical Liability: Occurrence",
        "OO": "Other Liability: Occurrence",
        "PC": "Product Liability: Claims Made",
        "PO": "Product Liability: Occurrence",
        "PP": "Private Passenger Auto",
        "SL": "Special Liability",
        "WC": "Workers' Compensation"
    }

- ``informed_priors_version``: Version of the industry-informed priors to use when fitting the model. Supported versions currently only include: ``"2022"``. Specify as ``"latest"`` to always use the most up-to-date priors available. Defaults to ``None``.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "init_log_ata__loc": 0.0,
        "init_log_ata__scale": 1.0,
        "bondy_exp__loc": 0.0,   # beta location above
        "bondy_exp__scale": 0.3, # beta scale above
        "sigma_slope__loc": -0.6,
        "sigma_slope__scale": 0.3,
        "sigma_intercept__loc": 0.0,
        "sigma_intercept__scale": 3.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight data from older evaluation dates. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older evaludation dates will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.

Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``GeneralizedBondy`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.tail_model.predict(
        triangle=...,
        config={ # default config
            "max_dev_lag": None,
            "include_process_noise": True,
        }
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle that was used in model fitting, and setting ``target_triangle=None`` will create a squared version of the modeled triangle. However, decoupling ``triangle`` and ``target_triangle`` means users could train the model on one triangle, and then make predictions starting from and/or on a different triangle. By default, predictions will be made out to the maximum development lag in ``triangle``, but users can also set ``max_dev_lag`` in the configuration directly. 

The ``GeneralizedBondy`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag in ``triangle``. Note that ``GeneralizedBondy`` can be used to make predictions for development lags beyond the last development lag available in the training triangle, as there is a mechanism in the model to extrapolate out age-to-age beyond the training data.
- ``eval_resolution``: the resolution of the evaluation dates in the tail. Defaults to the evaluation date resolution in ``triangle``. If ``triangle`` is from a single evaluation date, falls back to the resolution of the training data.
- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation :math:`\mu_{ij}` as predictions as oppposed to :math:`\mathrm{LR}_{ij}`.
