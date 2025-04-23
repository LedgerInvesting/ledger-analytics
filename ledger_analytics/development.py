from enum import Enum
from typing import Literal

from .config import LossFamily, ValidationConfig
from .model import DevelopmentModel


class ChainLadder(DevelopmentModel):
    """ChainLadder.

    This model implements, by default, Ledger's Bayesian chain ladder model
    with the form:

    ..  math::

        y_{ij} &\\sim \mathrm{Gamma(\mu_{ij}, \\sigma_{ij}^2)},  \quad{\\forall j \in (1, M]}\\\\
        \mu_{ij} &= ATA_{j - 1} y_{ij-1}\\\\
        \\sigma_{ij}^2 &= \exp(\\sigma_{\mathrm{int}} + \\sigma_{\mathrm{noise}_{j}} + \\sigma_{\mathrm{slope}} j + \log(y_{ij-1}))\\\\

    where :math:`y` represents losses and M is the total number of development lags. 
    The hierarchical variance parameter,
    :math:`\sigma_{\mathrm{noise}_{j}}`, can be removed by setting the ``use_linear_noise`` argument
    to True. See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for ChainLadder.

        Attributes:
            ata__loc: the location of the ATA priors, either a float
                or a list of floats, one for each ATA parameter.
        """

        ata__loc: float | list[float] = 0.0
        ata__scale: float | list[float] = 5.0
        sigma_slope__loc: float = -0.6
        sigma_slope__scale: float = 0.3
        sigma_intercept__loc: float = 0.0
        sigma_intercept__scale: float = 3.0
        sigma_noise__sigma_scale: float = 0.5

    class Config(ValidationConfig):
        """ChainLadder model configuration class.

        Attributes:
            loss_family: the likelihood family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
                See the ``LossFamily`` type hint class in ``ledger_analytics.config``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            use_linear_noise: Set to True to turn off the hierarchical
                variance parameter in ChainLadder.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            line_of_business: Line of business used to specify informed priors. Must be
                provided if ``informed_priors_version`` is not ``None``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the DefaultPriors class for default (non line-of-business)
                priors.
            informed_priors_version: If ``line_of_business`` is set, the priors are based
                on Ledger Investing's proprietary values derived from industry data.
                ``"latest"`` uses priors derived from the most recent industry data.
                Defaults to ``None``.
            use_multivariate: Boolean indicating whether to use a correlated prior
                on age-to-age factors. The correlated prior needs to be combined with
                industry-informed priors for best results.
            autofit_override: override the MCMC autofitting procedure arguments. See the documentation
                for a fully description of options in the User Guide.
            sigma_volume: Boolean indicating whether to use a volume parameter in the variance
                function.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: LossFamily = "Gamma"
        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        use_linear_noise: bool = False
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        priors: dict[str, list[float] | float] | None = None
        informed_priors_version: str | None = None
        use_multivariate: bool = False
        autofit_override: dict[str, float | int | None] = None
        sigma_volume: bool = False
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """ChainLadder predict configuration class.

        Attributes:
            max_dev_lag: the maximum development lag to predict to.
                Defaults to the maximum in the training data.
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        max_dev_lag: int | None = None
        include_process_risk: bool = True


class TraditionalChainLadder(DevelopmentModel):
    """TraditionalChainLadder.

    This model implements, by default, a traditional chain ladder model
    fit with maximum likelihood estimation with the form:

    ..  math::

        y_{ij} &\sim \mathrm{Normal(\mu_{ij}, \\sigma_{ij}^2)},  \quad{\\forall j \in (1, M]}\\\\
        \mu_{ij} &= ATA_{j - 1} y_{ij-1}\\\\
        \\sigma_{ij}^2 &= \\sigma^2 y_{ij-1}

    where :math:`y` represents losses. 
    The variance term implements volume-weighted averaging by weighting by the previous
    loss amount, but this can be turned off
    in the configuration.
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for TraditionalChainLadder.

        Attributes:
        """

        ata__loc: float | list[float] = 0.0
        ata__scale: float | list[float] = 1e6

    class Config(ValidationConfig):
        """TraditionalChainLadder model configuration class.

        Attributes:
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            use_volume_weighting: whether to compute ATA factors as volume-weighted
                averages of observed link ratios, as opposed to straight averages.
            recency_decay: geometric decay parameter to down-weight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            line_of_business: Line of business used for decay weighting. Must be
                provided if ``recency_decay`` is ``"lookup"``. These weights
                are derived from historical industry data and are current proprietary.
            autofit_override: override the MCMC autofitting procedure arguments.
                See the documentation
            prior_only: should a prior predictive simulation be run?
        """

        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        use_volume_weighting: bool = True
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        autofit_override: dict[str, float | int | None] = None
        prior_only: bool = False

    class PredictConfig(ValidationConfig):
        """TraditionalChainLadder predict configuration class.

        Attributes:
            max_dev_lag: the maximum development lag to predict to.
                Defaults to the maximum in the training data.
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        max_dev_lag: int | None = None
        include_process_risk: bool = True


class ManualATA(DevelopmentModel):
    """ManualAta.

    This model is different from other loss development models in that it uses
    hard-coded age-to-age factors, rather than estimating them from the data.

    ..  math::
      
        y_{ij} &= \mu_{ij}\\\\
        \mu_{ij} &= ATA_{j - 1} y_{ij-1}\\\\
        \\bf{ATA} &= \\text{user input}

    The primary intended use case of this model is for supporting workflows where
    age-to-age factors are selected or adjusted by hand, or age-to-age factors
    are provided by a bureau or other external source without any supporting
    data behind them.

    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        pass

    class Config(ValidationConfig):
        """ManualAta model configuration class.

        Attributes:
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            ata_factors: a list of age-to-age development factors. If
                ``development_resolution`` is 3 and ``development_offset`` is 6, then the
                first factor in the list should be a 6-to-9 month ATA, the second factor
                should be a 9-to-12 month ATA, and so forth.
            development_resolution: the number of months between development lags
                of successive development factors.
            development_offset: the development lag (in months) of the first
                development factor provided.
        """

        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        ata_factors: list[float]
        development_resolution: int = 12
        development_offset: int = 0

    class PredictConfig(ValidationConfig):
        """TraditionalChainLadder predict configuration class.

        Attributes:
            max_dev_lag: the maximum development lag to predict to.
        """

        max_dev_lag: int | None = None


class MeyersCRC(DevelopmentModel):
    """Bayesian MeyersCRC.

    This model implements the MeyersCRC model from 
    `Glenn Meyer's 2019 monograph <https://www.casact.org/sites/default/files/2021-02/08-Meyers.pdf>`_:

        * Meyers (2019). Stochastic loss reserving using Bayesian MCMC models (2nd edition).
            Casualty Actuarial Society.

    The model has the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \\sigma_{ij}^2) \quad{\\forall j \in (1, M]}\\\\
        \mu_{ij} &= \exp(\mathrm{LR}_{\\text{expected}} + \\beta_{\\text{lag},j} + \\beta_{\\text{year},i})\\\\
        \\sigma_{ij}^2 &= \exp(\\sigma_{\\text{int}} + \\sigma_{\\text{slope}} j - \log(\mathrm{EP}_{i}))\\\\

    where :math:`y` is loss ratio.
    See the model-specific documentation and Glenn Meyer's monograph
    in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for MeyersCRC.

        Attributes:
        """

        logelr__loc: float = -0.4
        logelr__scale: float = 10**0.5
        lag_factor__loc: float = 0.0
        lag_factor__scale: float = 10**0.5
        year_factor__loc: float = 0.0
        year_factor__scale: float = 10**0.5
        sigma_intercept__scale: float = 3.0
        sigma_slope__scale: float = 1.0

    class Config(ValidationConfig):
        """MeyersCRC model configuration class.

        Attributes:
            loss_family: the likelihood family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
                See the ``LossFamily`` type hint class in ``ledger_analytics.config``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the DefaultPriors class for default (non line-of-business)
                priors.
            autofit_override: override the MCMC autofitting procedure arguments. See the documentation
                for a fully description of options in the User Guide.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: LossFamily = "Gamma"
        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        recency_decay: str | float | None = None
        priors: dict[str, list[float] | float] | None = None
        autofit_override: dict[str, float | int | None] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """MeyersCRC predict configuration class.

        Attributes:
            max_dev_lag: the maximum development lag to predict to.
                Defaults to the maximum in the training data.
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        max_dev_lag: int | None = None
        include_process_risk: bool = True


class GMCL(DevelopmentModel):
    """GMCL.

    This model implements, by default, a Bayesian (generalized) multivariate
    chain ladder model with or without intercepts. 
    The multivariate chain ladder models paid and reported jointly, which we
    implement by assuming the log-scale age-to-age factors for paid and reported
    losses are multivariate normal. The generalized version of the model extends
    this to assuming the residual variances are also correlated between paid
    and reported losses. Finally, the addition of intercepts allows for cases
    where the regression of losses at development lag j + 1 on losses at lag j
    does not intersect the origin.

    The generalized version of the model has the form:

    ..  math::

        y_{ijd} &\sim \\text{Gamma}(\mu_{ijd}, \\sigma_{jd}^2), \quad \\forall j\in (1, M], d \in \{1,2\} \\\\ 
        \mu_{ijd} &= \\beta_{\\text{int},d} + ATA_{j - 1, d} \cdot y_{ij-1, d}\\\\
        \log \mathbf{ATA}_{(1:M-1) \\times 2} &\sim \\text{MVN}(\mathbf{ATA}_{\\text{loc}}, \\boldsymbol{\Sigma}_{\\text{ATA}}) \\\\
        \log \\boldsymbol{\sigma}_{(1:M-1) \\times 2} &\sim \\text{MVN}(\\boldsymbol{\sigma_{\\text{loc}}}, \\boldsymbol{\Sigma}_{\sigma})

    where :math:`y` represents losses. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for GMCL.

        Attributes:
            ata__loc: the location of the ATA priors, either a float
                or a list of floats, one for each ATA parameter.
        """

        ata__loc: float | list[float] = 0.0
        ata__scale: float | list[float] = 5.0
        sigma_slope__loc: float = -0.6
        sigma_slope__scale: float = 0.3
        sigma_intercept__loc: float = 0.0
        sigma_intercept__scale: float = 3.0
        sigma_noise__sigma_scale: float = 0.5

    class Config(ValidationConfig):
        """GMCL model configuration class.

        Attributes:
            loss_family: the likelihood family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
                See the ``LossFamily`` type hint class in ``ledger_analytics.config``.
            is_general: should the general MCL model be used?
            include_intercepts: should intercepts be included in the mean function?
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the DefaultPriors class for default (non line-of-business)
                priors.
            autofit_override: override the MCMC autofitting procedure arguments.
                See the documentation for a fully description of options in the User Guide.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: LossFamily = "Gamma"
        is_general: bool = False
        include_intercepts: bool = False
        recency_decay: str | float | None = None
        priors: dict[str, list[float] | float] | None = None
        autofit_override: dict[str, float | int | None] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """GMCL predict configuration class.

        Attributes:
            max_dev_lag: the maximum development lag to predict to.
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        max_dev_lag: int | None = None
        include_process_risk: bool = True
