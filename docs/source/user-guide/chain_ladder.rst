Chain Ladder Model (``ChainLadder``)
------------------------------------

The chain ladder method is a simple loss development technique that assumes that the ratio of 
ultimate losses to current losses is the same for all accident years. Our chain ladder *model* is 
based on the chain ladder method, and is implemented in the ``ChainLadder`` class. Mathematically,
the base ``ChainLadder`` model is expressed as:

.. math::

    \begin{align}
        \begin{split}
            y_{ij} &\sim \mathrm{Gamma(\mu_{ij}, \sigma_{ij}^2)}\\
            \mu_{ij} &= \log(ATA_{j - 1} y_{ij-1})\\
            \sigma_{ij}^2 &= \exp(\sigma_{\text{int}} + \sigma_{\text{slope}} j + \ln(y_{ij-1})),  \quad{\forall j \in (1, \tau]}\\
            \log \bf{ATA}_{1:M - 1} &\sim \mathrm{Normal}(0, 5)\\
            \sigma_{\text{int}} &\sim \mathrm{Normal}(0, 3)\\
            \sigma_{\text{slope}} &\sim \mathrm{Normal}(-.6, .3)\\
        \end{split}
    \end{align}

where :math:`\bf{ATA}` is a vector of *age-to-age factors* that capture how losses
change across development lags, :math:`\tau \in {2,...,M}` is an integer chosen by an analyst 
that indicates how many development lags should be used to fit the model to, and 
:math:`\mathrm{Gamma(\mu, \sigma^2)}` is the mean-variance parameterization of the 
Gamma distribution. In practice, :math:`\tau` is determined by preprocessing (i.e. clipping) the 
triangle before fitting. 

The ``ChainLadder`` model above is fit using the following API call: 

.. code-block:: python

    model = client.development_model.create(
        triangle=...,
        model_name=...,
        model_type="ChainLadder",
        model_config={ # default model_config
            "loss_definition": "reported",
            "loss_family": "gamma",
            "use_linear_noise": True,
            "use_multivariate": False,
            "line_of_business": None,
            "informed_priors_version": None,
            "priors": {
                "ata__loc": 0.0,
                "ata__scale": 5.0,
                "sigma_slope__loc": -0.6,
                "sigma_slope__scale": 0.3,
                "sigma_intercept__loc": 0.0,
                "sigma_intercept__scale": 3.0,
                "sigma_noise__sigma_scale": 0.5
            },
            "recency_decay": 1.0,
            "seed": None
        }
    )


Model Configuration
^^^^^^^^^^^^^^^^^^^^

The ``ChainLadder`` model accepts the following configuration parameters in ``model_config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, ``"paid"``, or ``"incurred"``). Defaults to ``"reported"``.
- ``loss_family``: Outcome distribution family (e.g., ``"gamma"``, ``"lognormal"``, or ``""normal"``). Defaults to ``"gamma"``.
- ``use_linear_noise``: Whether to use the linear noise variance function as specified in the ``ChainLadder`` equation above. Defaults to ``True``. If set to ``False``, random intercepts are estimated for each development lag such that we have: 

.. math::

    \begin{align}
        \sigma_{ij}^2 &= \exp((\sigma_{\text{int}} + \sigma_{\text{noise},j}) + \sigma_{\text{slope}} j + \ln(y_{ij-1}))\\
        \sigma_{\text{noise},j} &\sim \mathrm{Normal}(0, .5)
    \end{align}

- ``use_multivariate``: Whether to use a industry-informed multivariate normal prior distribution on the age-to-age factors to leverage industry ATA means and covariances across development lags when fitting to the given triangle. Defaults to ``False``. If set to ``True``, ``line_of_business`` and ``informed_priors_version`` must also be specified. Cannot be used with ``use_linear_noise=False``.
- ``line_of_business``: Line of business that the input triangle belongs to. Supported lines include: ``["CA", "MC", "MO", "OO", "PC", "PO", "PP", "SL", "WC"]``. Abbreviations map to the following lines: 

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

- ``informed_priors_version``: Version of the industry-informed priors to use when fitting the model (when ``use_multivariate=True``). Supported versions currently only include: ``"2022"``. Specify as ``"latest"`` to always use the most up-to-date priors available.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "ata__loc": 0.0,
        "ata__scale": 5.0,
        "sigma_slope__loc": -0.6,
        "sigma_slope__scale": 0.3,
        "sigma_intercept__loc": 0.0,
        "sigma_intercept__scale": 3.0,
        "sigma_noise__sigma_scale": 0.5, # for use_linear_noise=False
    }

- ``recency_decay``: Likelihood weight decay for recent observations. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of recent observations will be downweighted by a geometric decay function with factor ``recency_decay``.
- ``seed``: Random seed for model fitting.
