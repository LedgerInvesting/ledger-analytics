from pydantic import BaseModel, ConfigDict


class ValidationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
