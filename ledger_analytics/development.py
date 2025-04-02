from pydantic.dataclasses import dataclass

from .model import DevelopmentModel


@dataclass
class ChainLadderConfig(object):
    """Arguments:

    loss_family: the loss family to use
    """

    loss_family: str = "Gamma"
    loss_definition: str = "paid"


class ChainLadder(DevelopmentModel):
    """The ChainLadder class."""

    FIT_CONFIG = ChainLadderConfig
