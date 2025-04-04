Classical Power Transform Model (``ClassicalPowerTransform``)
----------------------------------------------------------------------

The Classical Power Transform model (Shoun, in prep [1]_) is a parametric tail model akin to the 
:doc:`GeneralizedBondy <./generalized-bondy>` and :doc:`Sherman <./sherman>` models that is designed 
to arbitrate between an exponential decay model, Clark's square root model [2]_, and Sherman's 
inverse power model [3]_ in a data-driven way. Our ``ClassicalPowerTransform`` model is 
mathematically expressed as:

.. math::

    \begin{align}
        \log ATA_{j} &\sim \mathrm{Normal(\mu_{j}, \sigma^2)}\\
        \mu_{j} &= \beta_{\text{int}} + \beta_{j} \text{L}_j\\
        \beta_{j} &= \lambda - 1 - \beta_{\text{slope}}\\
        \text{L}_j &= j^{\lambda-1} / \lambda\\
        \beta_{\text{int}} &\sim \mathrm{Normal}(\beta_{\text{int}, \text{loc}}, \beta_{\text{int}, \text{scale}})\\
        \beta_{\text{slope}} &\sim \mathrm{Normal}(\beta_{\text{slope}, \text{loc}}, \beta_{\text{slope}, \text{scale}})\\
        \log \sigma^2 &\sim \mathrm{Normal}(\sigma^{2}_{\text{loc}}, \sigma^{2}_{\text{scale}})\\
        \beta_{\text{int}, \text{loc}} &= 0.0\\
        \beta_{\text{int}, \text{scale}} &= 100.0\\
        \beta_{\text{slope}, \text{loc}} &= 0.0\\
        \beta_{\text{slope}, \text{scale}} &= 10.0\\
        \sigma^{2}_{\text{loc}} &= -4.0\\
        \sigma^{2}_{\text{scale}} &= 5.0\\
        \lambda &= \text{user input} \in [0,1]
    \end{align}

where :math:`\bf{ATA}` is a vector of *age-to-age factors* that capture how losses change across
development. Unlike other loss development and tail models, the ``ClassicalPowerTransform``
model is fitted directly to age-to-age factors in a two-stage fashion. When fitting the model, we
first estimate :math:`\bf{ATA}` by fitting the :doc:`TraditionalChainLadder <./trad-chain-ladder>` 
model first (with ``use_volume_weighting=True``). The estimated :math:`\bf{ATA}` are then extracted 
and then fitted given the model specification above. 

In the ``ClassicalPowerTransform`` model, the parameter :math:`\lambda` is a user-specified
parameter that determines the shape of the tail curve. When :math:`\lambda = 1`, the model is 
equivalent to an exponential decay model on the age-to-age factors. When :math:`\lambda = 0.5`, the 
model is equavalent to Clark's square root decay model on age-to-age factors. Finally, when 
:math:`\lambda = 0`, the model is equivalent to Sherman's inverse power decay model on the 
age-to-age factors. Therefore, by change the value of :math:`\lambda`, the user can change how 
heavy the implied tails are in the model. 

Typically, tail models like above model are fitted to only the window of development lags 
:math:`j \in [\rho_1, \rho_2]`, where :math:`(\rho_1, \rho_2) \in {2,...,M}, \rho_1 < \rho_2`, are 
chosen by an analyst based on where the tail process is assumed to begin and end. In practice, this 
can be accomplished my mutating/clipping the triangle as a preprocessing step before fitting.

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``ClassicalPowerTransform`` model above is fit using the following API call:

.. code-block:: python

    model = client.tail_model.create(
        triangle=...,
        name="example_name",
        model_type="ClassicalPowerTransform",
        config={ # default model_config
            "loss_definition": "paid",
            "lambda_": 1.0, # defaults to exponential decay shape
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``ClassicalPowerTransform`` model accepts the following configuration parameters in 
``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"paid"``.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "dev_slope_offset__loc": 0.0,
        "dev_slope_offset__scale": 10.0,
        "sigma__loc": -4.0,
        "sigma__scale": 5.0,
        "dev_intercept__loc": 0.0,
        "dev_intercept__scale": 100.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight data from older evaluation dates. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older evaludation dates will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.

Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``ClassicalPowerTransform`` model is used to predict future losses using the following API 
call:

.. code-block:: python

    predictions = model.tail_model.predict(
        triangle=...,
        config={ # default config
            "max_dev_lag": None,
            "include_process_noise": True,
        }
        target_triangle=None,
    )

Note that although the ``ClassicalPowerTransform`` model is specified with age-to-age factors
as the target variable, predictions are generated and returned to the user as losses. 

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle that was used in model fitting, and setting ``target_triangle=None`` will create a squared version of the modeled triangle. However, decoupling ``triangle`` and ``target_triangle`` means users could train the model on one triangle, and then make predictions starting from and/or on a different triangle. By default, predictions will be made out to the maximum development lag in ``triangle``, but users can also set ``max_dev_lag`` in the configuration directly. 

The ``ClassicalPowerTransform`` prediction behavior can be further changed with configuration 
parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag in ``triangle``. Note that ``GeneralizedBondy`` can be used to make predictions for development lags beyond the last development lag available in the training triangle, as there is a mechanism in the model to extrapolate out age-to-age beyond the training data.
- ``eval_resolution``: the resolution of the evaluation dates in the tail. Defaults to the evaluation date resolution in ``triangle``. If ``triangle`` is from a single evaluation date, falls back to the resolution of the training data.
- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation given :math:`\mu_{ij}` while not including the observation error :math:`\sigma^2`.

.. [1] Shoun, J. M. (2025). A power transform generalization of parametric tail factor methods. *In Prep*

.. [2] Clark, D. (2017). Estimation of inverse power parameters via GLM. Actuarial Review, pages 52-53.

.. [3] Sherman, R. E. (1984). Extrapolating, smoothing, and interpolating development factors. Proceedings of the Casaulty Actuarial Society, 71:122-155.