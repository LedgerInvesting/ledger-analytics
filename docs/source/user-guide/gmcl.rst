General Multivariate Chain Ladder (``GMCL``)
------------------------------------

The GMCL extends the univariate chain ladder model to multiple, potentially related, triangles,
such as triangles of paid and reported losses, by estimating the correlation in residuals between
triangles. The original implementation of GMCL (Zhang, 2010 [1]_) shares information on development 
factors between triangles via a multivariable regression, which is generally over-parameterized and 
requires strict constraints on the coefficients representing how development information in one 
triangle predicts development in another.

In our implementation, the ``GMCL`` model type takes a simpler approach by estimating the 
log-scale ATAs as multivariate normal between triangles. This specification esitmates correlations 
across age-to-age factors (ATAs) between triangles such that development factors from one triangle 
can influence development factors in other triangles. Mathematically, the ``GMCL`` model is 
expressed as:

.. math::

    \begin{align}
        y_{ijd} &\sim \text{Gamma}(\mu_{ijd}, \sigma_{jd}^2), \quad \forall j\in (1, \tau], d \in \{1,2\} \\ 
        \mu_{ijd} &= \beta_{\text{int},d} + ATA_{j - 1, d} \cdot y_{ij-1, d}\\
        \log \mathbf{ATA}_{(1:M-1) \times 2} &\sim \text{MVN}(\mathbf{ATA}_{\text{loc}}, \boldsymbol{\Sigma}_{\text{ATA}}) \\
        \log \boldsymbol{\sigma}_{(1:M-1) \times 2} &\sim \text{MVN}(\boldsymbol{\sigma_{\text{loc}}}, \boldsymbol{\Sigma}_{\sigma})\\
        \boldsymbol{\beta_{\text{int}}} &\sim \text{Normal}(\beta_{\text{int},\text{loc}}, \beta_{\text{int},\text{scale}})\\
        \boldsymbol{\Sigma}_{\text{ATA}} &= \operatorname{diag}(\mathbf{ATA}_{\text{scale}}) \mathbf{R}_{\text{ATA}} \operatorname{diag}(\mathbf{ATA}_{\text{scale}}) \\
        \boldsymbol{\Sigma}_{\sigma} &= \operatorname{diag}(\boldsymbol{\sigma_{\text{scale}}}) \mathbf{R}_{\sigma} \operatorname{diag}(\boldsymbol{\sigma_{\text{scale}}})\\
        \mathbf{R}_{\text{ATA}} &\sim \text{LKJ}(ATA_{\text{LKJ}})\\
        \mathbf{R}_{\sigma} &\sim \text{LKJ}(\sigma_{\text{LKJ}})\\
        \boldsymbol{\beta_{\text{int},\text{loc}}} &= 0.0\\
        \boldsymbol{\beta_{\text{int},\text{scale}}} &= 5.0\\
        \mathbf{ATA}_{\text{loc}} &= 0.0\\
        \mathbf{ATA}_{\text{scale}} &= 5.0\\
        \boldsymbol{\sigma_{\text{loc}}} &= 0.0\\
        \boldsymbol{\sigma_{\text{scale}}} &= 3.0\\
        ATA_{\text{LKJ}} &= 2.0\\
        \sigma_{\text{LKJ}} &= 2.0
    \end{align}


where :math:`\bf{ATA}` is a matrix of *age-to-age factors* that capture how losses change across 
development lags, with columns indicating triangle-specific factors. The age-to-age factors are 
correlated across triangles given their covariance :math:`\boldsymbol{\Sigma}_{\text{ATA}}`. 
Similarly, the expected variance at each development lag within each triangle is captured by 
:math:`\boldsymbol{\sigma}^2`, which is a matrix of variance parameters that are also correlated
across triangles given their covariance :math:`\boldsymbol{\Sigma}_{\sigma}`. 

Covariance terms for both age-to-age factors and variance parameters are constructed with variance 
priors set by the user, in addition to a :math:`2 \times 2` correlation matrix that is estimated 
from the data. The correlation matrix is assumed to follow an LKJ prior (read more on `LKJ correlation distributions here <https://mc-stan.org/docs/functions-reference/correlation_matrix_distributions.html#lkj-correlation>`_). 
Finally, the model also contains intercept terms specific to each triangle, 
:math:`\beta_{\text{int},d}`, which shift the expected losses by a constant amount.

The parameter :math:`\tau \in {2,...,M}` is an integer chosen by an analyst that indicates how many 
development lags should be used to fit the model to, and :math:`\mathrm{Gamma(\mu, \sigma^2)}` is 
the mean-variance parameterization of the Gamma distribution. In practice, :math:`\tau` is 
determined by preprocessing (i.e. clipping) the triangle before fitting. 

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``GMCL`` model is fit using the following API call: 

.. code-block:: python

    model = client.development_model.create(
        triangle=...,
        name="example_name",
        model_type="GMCL",
        config={ # default model_config
            "loss_definition": ["paid", "reported"],
            "loss_family": "gamma",
            "is_general": False,
            "include_intercepts": False,
            "priors": None, # see defaults below
            "recency_decay": 1.0,
            "seed": None
        }
    )

The ``GMCL`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Pair of loss fields to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``["paid", "reported"]``. Note that the ``GMCL`` differs from other loss development models in that it requires two fields to be modeled simultaneously. Therefore, both specified fields must be present in the triangle. 
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``is_general``: Whether the general form of the model should be used. Defaults to ``False``, which effectively sets the correlation matrix on age-to-age factors to the identity matrix (i.e. :math:`\mathbf{R}_{\text{ATA}} = \mathbf{I}`). If set to ``True``, the model will estimate the correlation matrix as specified above.
- ``include_intercepts``: Whether to include intercept terms in the model. Defaults to ``False``, which effectively sets the intercept terms to zero (i.e. :math:`\boldsymbol{\beta_{\text{int}}} = 0`). If set to ``True``, the model will estimate intercept terms for each triangle as specified above.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "ata__scale": 5.0,
        "log_sigma__scale": 3.0,
        "intercept__loc": 0.0,        # when include_intercepts=True
        "intercept__scale": 5.0,      # when include_intercepts=True
        "joint_atas__lkj_prior": 2.0, # when is_general=True  
        "joint_sigmas__lkj_prior": 2.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight data from older evaluation dates. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older evaluation dates will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.
- ``seed``: Random seed for model fitting.


Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``GMCL`` model is used to predict future losses using the following API call:

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

The ``GMCL`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag in ``triangle``. Note that ``GMCL`` can only generative predictions out to the maximum development lag in the training triangle, as there is no mechanism in the model to extrapolate out age-to-age beyond the training data.
- ``include_process_noise``: Whether to include process noise in the predictions. Defaults to ``True``, which generates posterior predictions from the mathematical model as specified above. If set to ``False``, the model will generate predictions without adding process noise to the predicted losses. Referring to the mathematical expression above, this equates to obtaining the expectation :math:`\mu_{ij}` as predictions as oppposed to :math:`y_{ij}`.

.. [1] Zhang, Y. 2010. A general multivariate chain ladder model. Insurance: Mathematics and Economics, 46, 588-599.