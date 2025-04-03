from enum import Enum

from .config import ValidationConfig
from .model import DevelopmentModel


class ChainLadder(DevelopmentModel):
    """ChainLadder.

    This model implements, by default, a Bayesian chain ladder model
    with the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= \mathrm{ATA}_{j - 1} \cdot y_{ij-1} \\\\
        \sigma_{ij}^2 &= \exp(\sigma_{\mathrm{int}} + \sigma_{\mathrm{noise}_{j}} + \sigma_{\mathrm{slope}} \cdot j) y_{ij-1}

    where :math:`y` represents losses. The hierarchical variance parameter,
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
            loss_family: the loss family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
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
                See the ChainLadderDefaultPriors class for default (non line-of-business)
                priors.
            informed_priors_version: If ``line_of_business`` is set, the priors are based
                on Ledger Investing's proprietary values derived from industry data.
                ``"latest"`` uses priors derived from the most recent industry data.
                Defaults to ``None``.
            use_multivariate: Boolean indicating whether to use a correlated prior
                on age-to-age factors. The correlated prior needs to be combined with
                industry-informed priors for best results.
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: str = "Gamma"
        loss_definition: str = "paid"
        use_linear_noise: bool = False
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        priors: dict[str, list[float] | float] | None = None
        informed_priors_verison: str | None = None
        use_multivariate: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """ChainLadder predict configuration class.

        Attributes:
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        include_process_risk: bool = True


class MeyersCRC(DevelopmentModel):
    """Bayesian MeyersCRC.

    This model implements the MeyersCRC model from 
    `Glenn Meyer's 2019 monograph <https://www.casact.org/sites/default/files/2021-02/08-Meyers.pdf>`_:

        * Meyers (2019). Stochastic loss reserving using Bayesian MCMC models (2nd edition).
            Casualty Actuarial Society.

    The model has the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= \exp(\mathrm{LogELR} + \\alpha_{i} + \\beta_{j}) \\\\
        \sigma_{ij}^2 &= \exp(\sigma_{\mathrm{int}} + \sigma_{\mathrm{slope}} \cdot j - \log(EP))

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
            loss_family: the loss family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the MeyersCRCDefaultPriors class for default (non line-of-business)
                priors.
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: str = "Gamma"
        loss_definition: str = "paid"
        recency_decay: str | float | None = None
        priors: dict[str, list[float] | float] | None = None
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """MeyersCRC predict configuration class.

        Attributes:
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        include_process_risk: bool = True
