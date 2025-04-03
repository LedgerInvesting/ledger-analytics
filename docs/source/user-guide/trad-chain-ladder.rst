Traditional Chain Ladder Model (``TraditionalChainLadder``)
-----------------------------------------------------------

The chain ladder method is a simple loss development technique that assumes that the ratio of 
ultimate losses to current losses is the same for all accident periods. Our traditional chain ladder 
model is meant to closely mimic the chain ladder method, and is implemented by the 
``TraditionalChainLadder`` model type. Mathematically, the base ``TraditionalChainLadder`` model is 
expressed as:

.. math::

    \begin{align}
        \begin{split}
            y_{ij} &\sim \mathrm{Normal(\mu_{ij}, \sigma_{ij}^2)},  \quad{\forall j \in (1, \tau]}\\
            \mu_{ij} &= ATA_{j - 1} y_{ij-1}\\
            \sigma_{ij}^2 &= \sigma^2 y_{ij-1}\\
            \log \bf{ATA}_{1:M - 1} &\sim \mathrm{Normal}(ATA_{\text{loc}}, ATA_{\text{scale}})\\
            \sigma^2 &\sim \mathrm{Normal}(\sigma^{2}_{\text{loc}}, \sigma^{2}_{\text{scale}})\\
            ATA_{\text{loc}} &= 0\\
            ATA_{\text{scale}} &= 10^6\\
            \sigma^{2}_{\text{loc}} &= 0\\
            \sigma^{2}_{\text{scale}} &= 1
        \end{split}
    \end{align}

where :math:`\bf{ATA}` is a vector of *age-to-age factors* that capture how losses
change across development lags, :math:`\tau \in {2,...,M}` is an integer chosen by an analyst 
that indicates how many development lags should be used to fit the model to. In practice, 
:math:`\tau` is determined by preprocessing (i.e. clipping) the triangle before fitting. 

Note that the ``TraditionalChainLadder`` model is fit using maximum likelihood estimation (MLE) as
opposed to MCMC sampling. Combined with the wide priors and Normal outcome distribution, the 
age-to-age factors estimated per ``TraditionalChainLadder`` will much more closely resemble the 
age-to-age factors estimated by the chain ladder method.

Model Fit Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

The ``TraditionalChainLadder`` model is fit using the following API call: 

.. code-block:: python

    model = client.development_model.create(
        triangle=...,
        name="example_name",
        model_type="TraditionalChainLadder",
        config={ # default model_config
            "loss_definition": "paid",
            "use_volume_weighting": True,
            "recency_decay": 1.0,
        }
    )

The ``TraditionalChainLadder`` model accepts the following configuration parameters in ``config``:

- ``loss_definition``: Name of loss field to model in the underlying triangle (e.g., ``"reported"``, 
- ``use_volume_weighting``: Whether to compute ATA factors as volume-weighted averages of observed link ratios, as opposed to straight averages. Defaults to ``True``, which performs MLE on the model as specified above. If set to ``False``, the variance term is set instead to :math:`\sigma_{ij}^2 &= \sigma^2`, and the resulting age-to-age factor estimates are not impacted by the loss volume.
- ``priors``: Dictionary of prior distributions to use for model fitting. Default priors are: 

.. code-block:: python

    {
        "ata__loc": 0.0,
        "ata__scale": 1e6,
        "sigma__loc": 0.0,
        "sigma__scale": 1.0,
    }

- ``recency_decay``: Likelihood weight decay to down-weight data from older evaluation dates. Defaults to ``1.0``, which means no decay. If set to a value between ``0.0`` and ``1.0``, the likelihood of older evaluation dates will be downweighted by a geometric decay function with factor ``recency_decay``. See :ref:`geometric-decay` for more information.


Model Predict Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``TraditionalChainLadder`` model is used to predict future losses using the following API call:

.. code-block:: python

    predictions = model.development_model.predict(
        triangle=...,
        config={ # default config
            "max_dev_lag": None,
        }
        target_triangle=None,
    )

Above, ``triangle`` is the triangle to use to start making predictions from and ``target_triangle`` is the triangle to make predictions on. For most use-cases, ``triangle`` will be the same triangle that was used in model fitting, and setting ``target_triangle=None`` will create a squared version of the modeled triangle. However, decoupling ``triangle`` and ``target_triangle`` means users could train the model on one triangle, and then make predictions starting from and/or on a different triangle. By default, predictions will be made out to the maximum development lag in ``triangle``, but users can also set ``max_dev_lag`` in the configuration directly.

The ``TraditionalChainLadder`` prediction behavior can be further changed with configuration parameters in ``config``:

- ``max_dev_lag``: Maximum development lag to predict out to. If not specified, the model will predict out to the maximum development lag in ``triangle``. Note that ``TraditionalChainLadder`` can only generative predictions out to the maximum development lag in the training triangle, as there is no mechanism in the model to extrapolate out age-to-age beyond the training data.
