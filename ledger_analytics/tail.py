from datetime import date
from enum import Enum

from .config import ValidationConfig
from .model import TailModel


class GeneralizedBondy(TailModel):
    """GeneralizedBondy.

    This model implements, by default, a Bayesian version of
    the Generalized Bondy tail development model, with the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= \mathrm{ATA}_{j - 1} \cdot y_{ij-1} \\\\
        \mathrm{ATA}_{j - 1} &= \exp(\mathrm{LogInitATA} \\beta^{j - \\delta}) \\\\
        \\sigma_{ij}^2 &= \exp(\sigma_{\mathrm{int}} + \sigma_{\mathrm{slope}} \cdot j - \log(EP))

    where :math:`y` represents loss ratios. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for GeneralizedBondy.

        Attributes:
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
        """GeneralizedBondy model configuration class.

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
        """GeneralizedBondy predict configuration class.

        Attributes:
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        max_dev_lag: float | None = None
        max_eval: date | None = None
        eval_resolution: tuple[int, str] | None = None
        include_process_risk: bool = True
