State Space Model (``SSM``)
------------------------------

State-space models are appealing for loss ratio forecasting because they allow separation of 
observation noise from the *true* latent variability in the underlying ultimate loss ratios. The 
distinction is important, particularly in cases where the premium volume of a program
changes significantly over time, or when extending the model to capture effects that
influence the latent (but not observation) process. 

Our State Space Model (``SSM``) can be viewed as a latent random walk with noise, with an AR(1) and 
optional MA(1) component. By default, the model is an latent ARMA(1, 1). The ``SSM`` is 
mathematically expressed as:

.. math:: 
    \begin{align*}
        \mathrm{LR}_{i} &\sim \mathrm{Gamma}(\exp(\eta_{i}), \sigma_{i}^2)\\
        \eta_{i} &= (1 - \phi_{\text{reversion}}) \mathrm{LR}_{\text{target}} + \phi_{\text{reversion}} \eta_{i - 1} + \zeta_{i-1} + z_{i} \sqrt{\epsilon_{\text{latent}}}\\
        \zeta_{i} &= \gamma_{\text{momentum}} (\zeta_{i-1} + z_{i} \sqrt{\epsilon_{\text{latent}}})\\
        \sigma_{i}^2 &= \exp(\sigma_{\text{base}})^2 + \exp(\sigma_{\text{obs}})^2 / \sqrt{\mathrm{UEP}_i} \\
        \phi_{\text{reversion}} &= \mathrm{logit}^{-1}(\phi_{\text{reversion}}^{*}) \cdot 2 - 1\\
        \phi_{\text{reversion}}^{*} &\sim \mathrm{Normal}(\phi_{\text{reversion}, \text{loc}}, \phi_{\text{reversion}, \text{scale}})\\
        \gamma_{\text{momentum}} &= \mathrm{logit}^{-1}(\gamma_{\text{momentum}}^{*})\\
        \gamma_{\text{momentum}}^{*} &\sim \mathrm{Normal}(\gamma_{\text{momentum}, \text{loc}}, \gamma_{\text{momentum}, \text{scale}})\\
        \mathrm{LR}_{\text{target}} &\sim \mathrm{Normal}(\mathrm{LR}_{\text{target}, \text{loc}}, \mathrm{LR}_{\text{target}, \text{scale}})\\
        z_i &\sim \mathrm{Normal}(0, 1)\\
        \log \epsilon_{\text{latent}} &\sim \mathrm{Normal}(\epsilon_{\text{latent}, \text{loc}}, \epsilon_{\text{latent}, \text{scale}})\\
        \sigma_{\text{base}} &\sim \mathrm{Normal}(\sigma_{\text{base}, \text{loc}}, \sigma_{\text{base}, \text{scale}})\\
        \sigma_{\text{obs}} &\sim \mathrm{Normal}(\sigma_{\text{obs}, \text{loc}}, \sigma_{\text{obs}, \text{scale}})\\
        \phi_{\text{reversion}, \text{loc}} &= 1.5\\
        \phi_{\text{reversion}, \text{scale}} &= 1.0\\
        \gamma_{\text{momentum}, \text{loc}} &= -1.0\\
        \gamma_{\text{momentum}, \text{scale}} &= 1.0\\
        \mathrm{LR}_{\text{target}, \text{loc}} &= -0.5\\
        \mathrm{LR}_{\text{target}, \text{scale}} &= 1.0\\
        \epsilon_{\text{latent}, \text{loc}} &= -2.0\\
        \epsilon_{\text{latent}, \text{scale}} &= 1.0\\
        \sigma_{\text{base}, \text{loc}} &= -5.0\\
        \sigma_{\text{base}, \text{scale}} &= 1.0\\
        \sigma_{\text{obs}, \text{loc}} &= -1.0\\
        \sigma_{\text{obs}, \text{scale}} &= 1.0\\
    \end{align*}

where :math:`\mathrm{LR}_i` indicates the observed loss ratio for accident period :math:`i`, 
:math:`\eta_i` is the latent log loss ratio for the same accident period, and :math:`\mathrm{UEP}_i` is the 
*used earned premium* for the same accident period (see details below). The state space component of 
the model captures how the latent log loss ratio (:math:`\eta_i`) evolves over time. The
evolution of :math:`\eta_i` is controlled by a reversion parameter (:math:`\phi_{\text{reversion}}`),
a momentum parameter (:math:`\gamma_{\text{momentum}}`), and a latent noise parameter 
(:math:`\epsilon_{\text{latent}}`). The reversion parameter controls how much the latent log loss
ratio reverts to a target loss ratio (:math:`\mathrm{LR}_{\text{target}}`) each period. The momentum
parameter controls how much the latent log loss ratio is influenced by the previous period's latent 
change, and the latent noise parameter controls how much latent change occurs each period. 

The ``SSM`` is specified such that :math:`\exp(\eta_i)` is the expected loss ratio for each 
accident period, and the observed loss ratios are then assumed to be Gamma distributed where 
:math:`\mathrm{Gamma(\exp(\eta_i), \sigma_{i}^2)}` is the mean-variance parameterization of the 
Gamma distribution.  

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``SSM`` model is fit using the following API call: 

.. code-block:: python

    model = client.forecast_model.create(
        triangle=...,
        name="example_name",
        model_type="SSM",
        config={ # default model_config
            "loss_definition": "reported",
            "loss_family": "gamma",
            "include_momentum": True,
            "use_cape_cod": True,
            "use_measurement_error": False,
            "period_years": 1.0,
            "line_of_business": None,
            "informed_priors_version": None,
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``SSM`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"reported"``.
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``include_momentum``: Whether to include a momentum parameter in the model. Defaults to ``True``, resulting in the ARMA(1, 1) model described above. If set to ``False``, the momentum parameter is set to 0 and the process drops out, leaving only the latent AR(1) process in the model.
- ``use_cape_cod``: Whether to use the Cape Cod method to account for down-weighting more recent, greener years based on the age-to-ultimate. Defaults to ``True``, which will estimate the used earned premium (UEP) by scaling the earned premium for each accident period by the percent of observed losses vs ultimate losses estimated for the given accident period. UEP is lower for more recent accident periods, which increases the :math:`\sigma_{i}^2` term for those observations, effecitvely down-weighting them in the likelihood. If set to ``False``, the model will assume that the UEP is equal to the input earned premium for each accident period.
- ``use_measurement_error``: Whether to include measurement error in the model. Defaults to ``False``, which assumes that the mean of the input ultimate loss ratios are the true loss ratios. If set to ``True``, for losses in the input triangle that have associated uncertainty (i.e. posterior predictive distributions from a loss development or tail model), "true" ultimates are estimated given the mean and standard deviation of the observed/predicted ultimates, and these true ultimates are used as the outcome variable in the model (i.e. :math:`LR_i`) as opposed to the observed ultimates. Note that ``use_cape_cod`` and ``use_measurement_error`` should not both be set to ``True``, as they are different ways to account for uncertainty in the ultimate loss ratios.
- ``period_years``: Number of years in each accident period. Defaults to ``1.0``, which means that each period is one year. If set to a value lesser than ``1.0``, the model will treat each period as a proportion of a year (i.e. ``period_years=0.25`` indicates that each :math:`i` is an accident quarter). It is critical that this parameter is set correctly, as it is used to scale priors in the model, all of which are scaled by default to accident years. 
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

- ``informed_priors_version``: Version of the industry-informed priors to use when fitting the model. Supported versions currently only include: ``"2022"``. Specify as ``"latest"`` to always use the most up-to-date priors available. Defaults to ``latest``.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "target_log_lr_loc": -0.5,
        "target_log_lr_scale": 1.0,
        "reversion_logit_loc": 1.5,
        "reversion_logit_scale": 1.0,
        "latent_log_noise_loc": -2.0,
        "latent_log_noise_scale": 1.0,
        "obs_log_noise_loc": -1.0,
        "obs_log_noise_scale": 1.0,
        "base_log_noise_loc": -5.0,
        "base_log_noise_scale": 1.0,
        "momentum_logit_loc": -1.0,
        "momentum_logit_scale": 1.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight older experience periods. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older experience periods will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.

Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``SSM`` model is used to predict future losses using the following API call:

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

The ``SSM`` prediction behavior can be further changed with configuration parameters in 
``config``:

- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation :math:`\exp(\eta_{i})` as predictions as oppposed to :math:`\mathrm{LR}_{i}`.