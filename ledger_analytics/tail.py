from datetime import date
from enum import Enum
from typing import Literal

from .config import ValidationConfig
from .model import TailModel


class TailDefaultPredictConfig(ValidationConfig):
    """Default tail model prediction class.

    Attributes:
        max_dev_lag: the maximum development lag to predict to.
        max_eval: the maximum evaluation date (diagonal) to predict to.
        eval_resolution: the evaluation date resolution to predict at.
        include_process_risk: should process risk or
            aleatoric uncertainty be included in the predictions.
            Defaults to ``True``. If ``False``, predictions are
            based on the mean function, only.
    """

    max_dev_lag: float | None = None
    max_eval: date | None = None
    eval_resolution: tuple[int, str] | None = None
    include_process_risk: bool = True


class GeneralizedBondy(TailModel):
    """GeneralizedBondy.

    This model implements, by default, a Bayesian version of
    the Generalized Bondy tail development model, with the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= \mathrm{ATA}_{j - 1} \cdot y_{ij-1} \\\\
        \mathrm{ATA}_{j - 1} &= \exp(\mathrm{LogInitATA} \\beta^{j - \\delta}) \\\\
        \\sigma_{ij}^2 &= \exp(\sigma_{\mathrm{int}} + \sigma_{\mathrm{slope}} \cdot (j - \\delta) - \log(EP))

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
                See the DefaultPriors class for default (non line-of-business)
                priors.
            informed_priors_version: If ``line_of_business`` is set, the priors are based
                on Ledger Investing's proprietary values derived from industry data.
                ``"latest"`` uses priors derived from the most recent industry data.
                Defaults to ``None``.
            autofit_override: override the MCMC autofitting procedure arguments. See the documentation
                for a fully description of options in the User Guide.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: Literal["Gamma", "Lognormal", "Normal", "InverseGaussian"] = (
            "Gamma"
        )
        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        min_rel_pred: float = 0.0
        dev_lag_intercept: float = 0.0
        priors: dict[str, list[float] | float] | None = None
        informed_priors_version: str | None = None
        autofit_override: dict[str, float | int | None] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(TailDefaultPredictConfig):
        pass


class Sherman(TailModel):
    """Sherman.

    This model implements, by default, a Bayesian version of
    `Sherman (1984)'s <https://www.casact.org/sites/default/files/database/proceed_proceed84_84122.pdf>`_
    inverse power curve tail development model, 

    * Sherman, RE (1984). Extrapolating, smoothing and interpolating
        development factors. PCAS 71, p. 122-155.

    It has the form:

    ..  math::

        y_{ij} &\sim \mathrm{Gamma}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= \mathrm{ATA}_{j - 1} \cdot y_{ij-1} \\\\
        \mathrm{ATA}_{j - 1} &= 1 + \exp(\mathrm{intercept} - \\beta \cdot (j - \\delta)) \\\\
        \\sigma_{ij}^2 &= \exp(\sigma_{\mathrm{int}} + \sigma_{\mathrm{slope}} \cdot (j - \\delta) - \log(EP))

    where :math:`y` represents loss ratios. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for Sherman.

        Attributes:
        """

        dev_intercept__loc: float = 0.0
        dev_intercept__scale: float = 1.0
        sherman_exp__loc: float = 0.0
        sherman_exp__scale: float = 1.0
        sigma_slope__loc: float = -0.6
        sigma_slope__scale: float = 0.3
        sigma_intercept__loc: float = 0.0
        sigma_intercept__scale: float = 3.0

    class Config(ValidationConfig):
        """Sherman model configuration class.

        Attributes:
            loss_family: the loss family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            min_rel_pred: Minimum relative prediction for the one-step ahead predictions.
                This is a multiplier of the previous period's loss. Setting to 1.0
                indicates that future losses should be strictly at least the prior period's
                loss amount, avoiding negative development patterns.
            dev_lag_intercept: the development lag offset to apply in the exponential of
                the Bondy exponent term. By default, this is 0.0, but can be set to a
                suitable development lag (in months) to center the Bondy parameters.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the DefaultPriors class for default (non line-of-business)
                priors.
            autofit_override: override the MCMC autofitting procedure arguments. See the documentation
                for a fully description of options in the User Guide.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_family: Literal["Gamma", "Lognormal", "Normal", "InverseGaussian"] = (
            "Gamma"
        )
        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        min_rel_pred: float = 0.0
        dev_lag_intercept: float = 0.0
        priors: dict[str, list[float] | float] | None = None
        informed_priors_verison: str | None = None
        autofit_override: dict[str, float | int | None] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(TailDefaultPredictConfig):
        pass


class ClassicalPowerTransformTail(TailModel):
    """ClassicalPowerTransformTail model.

    This model implements a generalization of classical power transform
    tail models on age-to-age factors (ATAs) which, by default, fits a model
    with maximum likelihood estimation of the form:

    ..  math::

        y_{ij} &\sim \mathrm{Normal}(\mu_{ij}, \sigma_{ij}^2) \\\\
        \mu_{ij} &= 1 + \exp(\\beta_{0} + \\beta_{1} \cdot \frac{d^{\\lambda - 1}}{\\lambda}), \quad \lambda != 0 \\\\ 

    where :math:`y` represents ATAs, and :math:`\\lambda`` is a Box-Cox transformation
    parameter. The latter can be set to switch between exponential decay, Sherman and Clark square-root tail
    models.
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for ClassicalPowerTransformTail.

        Attributes:
        """

        dev_slope_offset__loc: float = 0.0
        dev_slope_offset__scale: float = 10.0
        sigma__loc: float = -4.0
        sigma__scale: float = 5.0
        dev_intercept__loc: float = 0.0
        dev_intercept__scale: float = 100.0

    class Config(ValidationConfig):
        """ClassicalPowerTransformTail model configuration class.

        Attributes:
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            lambda_: Box-Cox transformation parameter applied to development lag
                (as measured in years). ``lambda_=1.0`` is equivalent to the exponential
                decay tail model. ``lambda_=0.0`` is equivalent to the Sherman
                inverse-power tail model. ``lambda_=0.5`` is equivalent to the Clark
                square-root tail model.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            min_rel_pred: Minimum relative prediction for the one-step ahead predictions.
                This is a multiplier of the previous period's loss. Setting to 1.0
                indicates that future losses should be strictly at least the prior period's
                loss amount, avoiding negative development patterns.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the DefaultPriors class for default (non line-of-business)
                priors.
            prior_only: should a prior predictive simulation be run?
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        loss_definition: Literal["paid", "reported", "incurred"] = "paid"
        lambda_: float = 1.0
        recency_decay: str | float | None = None
        min_rel_pred: float = 0.0
        priors: dict[str, list[float] | float] | None = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(TailDefaultPredictConfig):
        pass
