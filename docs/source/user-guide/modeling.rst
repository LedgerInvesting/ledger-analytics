Modeling rationale and implementation
=======================================

LedgerAnalytics provides a range of insurance data science
modeling tools and configuration options, but there
are a few key default options that apply to a range
of our models. Before learning about specific model
implementations, it's helpful to cover this information
at a high level.

Bayesian leaning
----------------------

Unless a model is prefixed with the name ``Traditional``,
our models are, by default, Bayesian models and the posterior
distributions are estimated with efficient Markov chain Monte Carlo
(MCMC) methods. This means that model predictions return triangles
filled with samples from the posterior predictive distribution.
By default, we return 10,000 samples. 
Options to change the number of samples returned, and other
MCMC sampler arguments, will be provided soon.
Our modeling tools also have the option to use other estimation
methods, like maximum likelihood estimation, if users wish.

One of the implications of using stochastic methods is that
results may change depending on the seed used to
seed downstream random number generators. Our models
accept a ``seed: int`` option to ensure models can
be reproducible. **However**, full reproducibility
depends on multiple factors, such as using the same
machine, with the same local environment (e.g. package versions),
the same input data, etc. It is up to the users
to manage this appropriately.

Easy default prior distributions
------------------------------------

Prior distributions are set to be weakly informative by default,
which will work fine in many cases. For select models,
users can alternatively set the ``line_of_business`` argument in the ``config``
dictionary to use line of business-specific prior distributions
that have been internally derived and validated.
See the individual model vignettes for more information about
which lines of business are accepted.
While these values are proprietary, 
users can run prior predictive checks to check the implications
of prior distributions by adding ``prior_only=True`` into the
``config`` dictionary.

Loss likelihood distributions
------------------------------------

All stochastic models modeling pure losses and loss ratios
have the option to set a
``loss_family`` in the ``config`` dictionary to specify the
likelihood distribution.
By default, this is set to ``Gamma`` to use the Gamma
distribution but can also be set to ``Lognormal``, ``Normal``
or ``InverseGaussian``. More complex distributions,
such as hurdle components, will be available in the future.

To aid changing likelihood distributions, our models
use mean-variance parameterizations of the likelihood
distributions. For instance, the 
`mean-variance parameterization of the Gamma <https://en.wikipedia.org/wiki/Gamma_distribution#Mean_and_variance>`_.

Samples as data
-------------------

Our models can receive posterior samples as data to allow
combining model predictions with downstream models.
Under-the-hood, we handle this using a measurement error
assumption, as explained more in our `Bayesian workflow
<https://arxiv.org/abs/2407.14666>`_ paper.

Deterministic data adjustments
--------------------------------

In some cases, we provide options to manipulate input data
to satisfy certain real-world constraints and assumptions
that users may want to impose but are not yet handled
by our models.

.. _geometric-decay:

Geometric decay weighting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Most models can down-weight data from older
evaluation dates using geometric decay weighting,
which is controlled by the ``recency_decay`` option passed
to the ``config`` dictionary. If set to ``None``,
this value is ``1.0`` by default, which means the data is
not down-weighted. If ``0 < recency_decay < 1``, then 
older observations 
are down-weighted by multiplying the raw data
using the rule
:math:`\rho^{(T - t) f}`, where :math:`\rho`
is the ``recency_decay`` value, :math:`T`
and :math:`t` are the maximum and current
evaluation date indices, and :math:`f`
is the triangle resolution in years. In forecasting
models decay weighting is based on the experience period
rather than the evaluation date.

You can play around with this using our Bermuda package:

.. code:: python

   from datetime import date
   from bermuda import meyers_tri, weight_geometric_decay

   weight_test = meyers_tri.derive_fields(
      weight=1.0
   ).clip(max_eval=date(1990, 12, 31))

   rho = 0.8
   evaluation_date_decay = weight_geometric_decay(
    triangle=weight_test,
    annual_decay_factor=rho,
    basis='evaluation',
    tri_fields="weight",
    weight_as_field=False,
   )
   evaluation_date_decay.to_array_data_frame('weight')

           period     0   12   24
    0  1988-01-01  0.64  0.8  1.0
    1  1989-01-01  0.80  1.0  NaN
    2  1990-01-01  1.00  NaN  NaN

The above shows a weighting scheme as applied to loss development, 
the following shows the experience period weighting scheme as
applied to forecast models.

.. code:: python

   experience_date_decay = weight_geometric_decay(
    triangle=weight_test,
    annual_decay_factor=rho,
    basis='experience',
    tri_fields="weight",
    weight_as_field=False,
   )
   experience_date_decay.to_array_data_frame('weight')

           period     0    12    24
    0  1988-01-01  0.64  0.64  0.64
    1  1989-01-01  0.80  0.80   NaN
    2  1990-01-01  1.00   NaN   NaN


Cape Cod method
^^^^^^^^^^^^^^^^^^^^

Users can implement the Cape Cod method,
which down-weights earned premium for less-developed
experience periods by multiplying the raw premium
by the loss emergence percentage or the inverse
of the ultimate development factor. 
This is useful if users want to impose the assumption
that greener experience periods' loss ratios should be more
uncertain. For instance, in forecasting, more recent
experience periods' ultimate loss ratios are based
on, typically, less data than older experience periods.

We recommend users opt for the 'samples as data' approach
above over the Cape Cod adjustment where possible,
which has similar properties but is a model-based
solution that can handle more complex use-cases.

