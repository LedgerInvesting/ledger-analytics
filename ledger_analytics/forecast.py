from enum import Enum

from .config import ValidationConfig
from .model import ForecastModel


class AR1(ForecastModel):
    """AR1.

    This model implements, by default, a Bayesian 
    autoregressive lag-1 forecasting model, with the form:

    ..  math::

        y_{i} &\sim \mathrm{Gamma}(\mu_{i}, \sigma_{i}^2) \\\\
        \mu_{ij} &= \\alpha y_{i - 1} + (1 - \\alpha) \mu \\\\
        \\sigma_{ij}^2 &= \\sigma_{\mathrm{base}} + \\frac{\\sigma_{obs}}{EP}

    where :math:`y` represents loss ratios. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for ChainLadder.

        Attributes:
            ata__loc: the location of the ATA priors, either a float
                or a list of floats, one for each ATA parameter.
        """

        init_log_ata__loc: float = 0.0
        init_log_ata__scale: float = 1.0
        bondy_exp__loc: float = 0.0
        bondy_exp__scale: float = 0.3
        sigma_slope__loc: float = -0.6
        sigma_slope__scale: float = 0.3
        sigma_intercept__loc: float = 0.0
        sigma_intercept__scale: float = 3.0

    class Config(ValidationConfig):
        """ChainLadder model configuration class.

        Attributes:
            loss_family: the loss family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            line_of_business: Line of business used to specify informed priors. Must be
                provided if ``informed_priors_version`` is not ``None``.
            min_rel_pred: Minimum relative prediction for the one-step ahead predictions.
                This is a multiplier of the previous period's loss. Setting to 1.0
                indicates that future losses should be strictly at least the prior period's
                loss amount, avoiding negative development patterns.
            dev_lag_intercept: the development lag offset to apply in the exponential of
                the Bondy exponent term. By default, this is 0.0, but can be set to a
                suitable development lag (in months) to center the Bondy parameters.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the ChainLadderDefaultPriors class for default (non line-of-business)
                priors.
            informed_priors_version: If ``line_of_business`` is set, the priors are based
                on Ledger Investing's proprietary values derived from industry data.
                ``"latest"`` uses priors derived from the most recent industry data.
                Defaults to ``None``.
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: str = "Gamma"
        loss_definition: str = "paid"
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        min_rel_pred: float = 0.0
        dev_lag_intercept: float = 0.0
        priors: dict[str, list[float] | float] | None = None
        informed_priors_verison: str | None = None
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
