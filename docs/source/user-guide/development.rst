Loss Development Models
========================

For all development models, we use :math:`\mathcal{Y}` to denote the loss development triangle for 
an aggregated pool of insurance policies, defined by:

.. math::

    \mathcal{Y} = \{y_{ij} : i = 1, ..., N; j = 1, ..., N - i + 1\}

where :math:`y_{ij}` is the cumulative loss amount for accident period :math:`i` at development
lag :math:`j`. In real-world data, losses for a given accident period :math:`i` are only known up 
to development lag :math:`j = N - i + 1`, creating the triangular data structure that loss 
triangles are named for. However, sometimes historic data will be available such that we have 
a full *square*, in which case we indicate the development lag with :math:`j = 1, ..., M`.

Some development models may use loss ratios as the target variable as opposed to cumulative losses. 
In such cases we use :math:`\mathcal{LR}` to denote loss ratios, where 
:math:`LR_{ij} = y_{ij} / EP_{i}` and :math:`EP_{i}` indicates the total earned premium for the 
given accident period. In either case, predictions are always generated and returned to the user
on the loss scale.

.. toctree::
   :maxdepth: 2
   :caption: Available Models

   chain-ladder
   gmcl
   manual-ata
   meyers-crc
   Traditional Chain Ladder <trad-chain-ladder>
