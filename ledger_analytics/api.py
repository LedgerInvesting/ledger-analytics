from __future__ import annotations

import os
from abc import ABC

from .interface import ModelInterface, TriangleInterface
from .requester import Requester


class BaseClient(ABC):
    def __init__(
        self,
        api_key: str | None = None,
        host: str | None = None,
        asynchronous: bool = False,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("LEDGER_ANALYTICS_API_KEY")
            if api_key is None:
                raise ValueError(
                    "Must pass in a valid `api_key` or set the `LEDGER_ANALYTICS_API_KEY` environment variable."
                )

        self._requester = Requester(api_key)

        if host is None:
            host = "http://localhost:8000/analytics/"

        trailing_slash = host[-1] == "/"
        if trailing_slash:
            self.host = host
        else:
            self.host = host + "/"

        self.asynchronous = asynchronous

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, type, value, traceback):
        pass


class AnalyticsClient(BaseClient):
    def __init__(
        self,
        api_key: str | None = None,
        host: str | None = None,
        asynchronous: bool = False,
    ):
        super().__init__(api_key=api_key, host=host, asynchronous=asynchronous)

    triangle = property(
        lambda self: TriangleInterface("triangle", self.host, self._requester)
    )
    development_model = property(
        lambda self: ModelInterface("development_model", self.host, self._requester)
    )
    tail_model = property(
        lambda self: ModelInterface("tail_model", self.host, self._requester)
    )
    forecast_model = property(
        lambda self: ModelInterface("forecast_model", self.host, self._requester)
    )
