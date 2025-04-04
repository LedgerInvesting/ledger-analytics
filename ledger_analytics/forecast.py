from enum import Enum
from typing import Literal

from .config import ValidationConfig
from .model import ForecastModel


class AR1(ForecastModel):
    """AR1.

    This model implements, by default, a Bayesian 
    autoregressive lag-1 forecasting model, with the form:

    ..  math::

        y_{i} &\sim \mathrm{Gamma}(\mu_{i}, \sigma_{i}^2) \\\\
        \mu_{ij} &= \\alpha y_{i - 1} + (1 - \\alpha) \mu \\\\
        \\sigma_{i}^2 &= \\sigma_{\mathrm{base}}^2 + \\frac{\\sigma_{obs}^2}{EP}

    where :math:`y` represents loss ratios. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for AR1.

        Attributes:
        """

        reversion__loc: float = 0.0
        reversion__scale: float = 1.0
        base_sigma__loc: float = -2.0
        base_sigma__scale: float = 1.0
        obs_sigma__loc: float = -2.0
        obs_sigma__scale: float = 1.0
        target_lr__loc: float = -0.5
        target_lr__scale: float = 1.0

    class Config(ValidationConfig):
        """AR1 model configuration class.

        Attributes:
            loss_family: the likelihood family to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            recency_decay: geometric decay parameter to downweight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the AR1DefaultPriors class for default (non line-of-business)
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
        priors: dict[str, list[float] | float] | None = None
        autofit_override: dict[str, int | float | str] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """AR1 predict configuration class.

        Attributes:
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        include_process_risk: bool = True


class LR_SSM(ForecastModel):
    """LR_SSM (Loss Ratio State Space Model).

    This model is a, by default, Bayesian state space model or
    Bayesian structural time series model similar to a local linear trend
    model with mean reversion (with drift) and a 'momentum' term which
    is analogous to a moving average lag-1 component with decay.
    The model has the form:

    ..  math::

        y_{i} &\sim \mathrm{Gamma}(\mu_{i}, \sigma_{i}^2) \\\\
        \mu_{ij} &= \exp((1 - \phi) \mathrm{LR}_{\mathrm{target}} + \phi \mu_{i - 1} + \zeta_{i - 1} + \epsilon_{i})\\\\
        \zeta_{i} &= \\gamma (\zeta_{i - 1} + \epsilon_{i})\\\\
        \\sigma_{i}^2 &= \\sigma_{\mathrm{base}}^2 + \\frac{\\sigma_{obs}^2}{EP}

    where :math:`y` represents loss ratios. 
    See the model-specific documentation in the User Guide for more details.

    The fit and predict configurations are controlled by :class:`Config` and
    :class:`PredictConfig` classes, respectively.
    """

    class DefaultPriors(Enum):
        """Default priors for LR_SSM.

        Attributes:
        """

        target_log_lr_loc: float = -0.5
        target_log_lr_scale: float = 1.0
        reversion_logit_loc: float = 1.5
        reversion_logit_scale: float = 1.0
        latent_log_noise_loc: float = -2.0
        latent_log_noise_scale: float = 1.0
        obs_log_noise_loc: float = -1.0
        obs_log_noise_scale: float = 1.0
        base_log_noise_loc: float = -5.0
        base_log_noise_scale: float = 1.0
        momentum_logit_loc: float = -1.0
        momentum_logit_scale: float = 1.0
        target_log_lr_diff_scale: float = 1.0
        reversion_logit_diff_scale: float = 1.0
        latent_log_noise_diff_scale: float = 0.25
        obs_log_noise_diff_scale: float = 1.0

    class Config(ValidationConfig):
        """LR_SSM model configuration class.

        Attributes:
            loss_family: the likelihood to use. One of ``"Gamma"``, ``"Lognormal"``,
                ``"Normal"`` or ``"InverseGaussian"``. Defaults to ``"Gamma"``.
            loss_definition: the field to model in the triangle. One of
                ``"paid"`` ``"reported"`` or ``"incurred"``.
            hierarchical: One of [``"full"``, ``"semi"``]. With semi-hierarchical modeling, the
                ``target_log_lr`` is partially pooled across slices. Fully hierarchical
                modeling includes partial pooling of reversion
                and noise parameters as well. Setting to ``None`` disables all hierarchical modeling.
                For convenience, if fitting to just a single triangle, this value will
                automatically be set to None.
            include_mean_reversion: whether to include mean reversion on the latent loss ratios (AR1).
            include_momentum: whether to include momentum on the latent loss ratios (MA1).
            use_cape_cod: Whether to use the Cape Cod method for down-weighting more
                recent, greener experience periods based on the ATU.
            use_measurement_error: Whether to use measurement errors on the loss ratio inputs.
                Setting both ``use_cape_cod`` and ``use_measurement_error`` is almost always a bad
                idea.
            period_years: Number of years in each period - 0.25 for quarterly, etc.
                If supplied along with ``line_of_business``, will convert LOB priors as needed.
            recency_decay: geometric decay parameter to down-weight earlier
                diagonals (see `Modeling rationale...` section
                in the User Guide). Defaults to 1.0 for no geometric decay.
                Can be ``"lookup"`` to choose based on ``line_of_business``.
            line_of_business: Line of business used to specify informed priors. Must be
                provided if ``informed_priors_version`` is not ``None``.
            priors: dictionary of priors. Defaults to ``None`` to use the default priors.
                See the LR_SSMDefaultPriors class for default (non line-of-business)
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
        hierarchical: Literal["full", "semi"] = None
        include_mean_reversion: bool = True
        include_momentum: bool = True
        use_cape_cod: bool = True
        use_measurement_error: bool = True
        period_years: float = 1.0
        recency_decay: str | float | None = None
        line_of_business: str | None = None
        priors: dict[str, list[float] | float] | None = None
        informed_priors_version: str | None = None
        autofit_override: dict[str, int | float | str] = None
        prior_only: bool = False
        seed: int | None = None

    class PredictConfig(ValidationConfig):
        """LR_SSM predict configuration class.

        Attributes:
            include_process_risk: should process risk or
                aleatoric uncertainty be included in the predictions.
                Defaults to ``True``. If ``False``, predictions are
                based on the mean function, only.
        """

        include_process_risk: bool = True
