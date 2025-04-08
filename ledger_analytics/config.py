from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict


class ValidationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


JSONDict = dict[str, Any]
HTTPMethods = Literal["post", "get", "delete"]

LossFamilies = Literal["Gamma", "Lognormal", "Normal", "InverseGaussian"]
LossFamily = Annotated[LossFamilies, BeforeValidator(lambda value: value.title())]
