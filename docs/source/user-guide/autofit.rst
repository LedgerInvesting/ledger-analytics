MCMC Autofit
===============

Ledger's Bayesian modeling infrastructure includes an autofit
procedure, which checks a fitted model's convergence diagnostics
against a set of standard thresholds and, if any have failed,
attempt to tune certain MCMC parameters and re-fit the model.
This aims to reduce the burden on remote users to constantly
check for convergence.
The autofit arguments are exposed to users via the configuration
dictionary passed to ``create`` methods. 

In general, we recommend users only change the autofit parameters
if they are familiar with Hamiltonion Monte Carlo MCMC tuning
parameters. The parameters are controlled by the ``AutofitControl``
class, and the default parameters are:

..  code:: python

    >>> from ledger_analytics import AutofitControl
    >>> AutofitControl().__dict__

	{'samples_per_chain': 2500,
	 'warmup_per_chain': None,
	 'adapt_delta': 0.8,
	 'max_treedepth': 10,
	 'thin': 1,
	 'max_adapt_delta': 0.99,
	 'max_max_treedepth': 15,
	 'max_samples_per_chain': 4000,
	 'chains': 4,
	 'divergence_rate_threshold': 0.0,
	 'treedepth_rate_threshold': 0.0,
	 'ebfmi_threshold': 0.2,
	 'min_ess': 1000,
	 'max_rhat': 1.05}

If you want to disable autofit from refitting models,
you can set a configuration such as (for an example model):

..	code:: python

    client.development_model.create(
		...,
		config={
			"autofit_override": {
				"max_samples_per_chain": 2500,
				"max_max_treedepth": 10,
				"max_adapt_delta": 0.8,
			}
		},
	)

which stops the samples per chain, maximum treedepth rate
and HMC target acceptance rate parameters from being tuned
to seek convergence.
Note, users pass the autofit arguments into the configuration
as a regular Python dictionary. Behind the scenes, this dictionary
is validated using the ``AutofitControl`` class.

You can see the API documentation for the ``AutofitControl`` class below.

..  autoclass:: ledger_analytics.AutofitControl
