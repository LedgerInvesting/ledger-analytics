import json

from .config import ValidationConfig


class AutofitControl(ValidationConfig):
    """The HMC (MCMC) autofitting parameters.

    The class holds the parameters users can tune in the autofit procedure.
    Only use this class if you feel confident with HMC tuning parameters.
    When creating models, the intention is that users pass the autofit
    parameters as a Python dict, not use this class.

    If you want to turn off the autofitting procedure completely,
    you can use a configuration such as:

    ..  code:: python

        AutofitControl(
            samples_per_chain: 1000,
            max_samples_per_chain: 1000,
            max_adapt_delta: 0.8,
            max_max_treedepth: 10,
        )

    Attributes:
        samples_per_chain: the number of posterior samples per chain.
        warmup_per_chain: the number of warmup samples per chain.
            If ``None``, defaults to half the posterior ``samples_per_chain``.
        adapt_delta: the initial HMC target average proposal acceptance probability.
        max_treedepth: the initial maximum depth of the binary trees.
        thin: the posterior samples thinning interval. Recommended to stay a ``1``.
        max_adapt_delta: the maximum ``adapt_delta`` value to try.
        max_max_treedeth: the maximum ``max_treedepth`` value to try.
        max_samples_per_chain: the maximum ``samples_per_chain`` to try.
        chains: the number of MCMC chains.
        divergence_rate_threshold: the threshold value of average allowed divergent transitions.
        treedepth_rate_threshold: the threshold value of average allowed iterations
            hitting the ``max_treedepth``.
        ebfmi_threshold: the threshold value of the EBFMI diagnostic.
        min_ess: the minimum effective sample size required.
        max_rhat: the maximum Rhat diagnostic.
    """

    samples_per_chain: int = 2500
    warmup_per_chain: int | None = None
    adapt_delta: float = 0.8
    max_treedepth: int = 10
    thin: int = 1
    max_adapt_delta: float = 0.99
    max_max_treedepth: int = 15
    max_samples_per_chain: int = 4000
    chains: int = 4
    divergence_rate_threshold: float = 0.0
    treedepth_rate_threshold: float = 0.0
    ebfmi_threshold: float = 0.2
    min_ess: int = 1000
    max_rhat: float = 1.05
