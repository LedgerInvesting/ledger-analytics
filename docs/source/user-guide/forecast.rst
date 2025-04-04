Forecasting Models
========================

For all forecasting models, we use :math:`\mathcal{LR}` to denote the ultimate loss ratios for an 
aggregated pool of insurance policies, defined by:

.. math::

    \mathcal{LR} = \{LR_{i} : i = 1, ..., N\}

where :math:`LR_{i}` is the ultimate loss ratio amount for accident period :math:`i`. In real-world data, ultimate losses for a given accident period :math:`i` are only known to the extent that we 
have sufficient historic data to observe the losses reach their ultimate state. In practice, this 
means that ultimate loss ratios for recent accident periods will actually be predictions or estimates
of the true ultimate loss ratios. In some cases, users may simply assume that the expected ultimate 
loss ratio is the true loss ratio for these accident periods, but in other cases users may want to 
explicitly account for measurement error or uncertainty in the ultimate loss ratio estimates. 
Currently, our ``SSM`` model is the only model that explicitly accounts for measurement error.

Note that despite our models being formulated to use ultimate loss ratios as the target variable,
ultimate losses and earned premiums are used as input data to fit the models. All forecasting models
use the ultimate losses and premiums to compute loss ratios for modeling internally, and resulting 
outputs (i.e. predictions) are given back on the loss scale (i.e. ultimate losses as opposed to 
ultimate loss ratios).

.. toctree::
   :maxdepth: 2
   :caption: Available Models

   ar1
   ssm
   gcc
