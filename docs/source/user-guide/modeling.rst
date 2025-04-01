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

Easy default prior distributions
------------------------------------

Prior distributions are set to be weakly informative by default,
which will work fine in many cases. Users
can also set the ``line_of_business`` argument in the ``config``
dictionary to user line of business-specific prior distributions
that have been internally derived and validated.
While these values are proprietary, 
users can run prior predictive checks to check the implications
of prior distributions by adding ``prior_only=True`` into the
``config`` dictionary.

Loss likelihood distributions
------------------------------------

Secondly, all stochastic models modeling pure losses and loss ratios
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

