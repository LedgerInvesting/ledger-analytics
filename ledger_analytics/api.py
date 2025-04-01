from __future__ import annotations

import os
from abc import ABC
from collections import namedtuple

from .interface import ModelInterface, TriangleInterface
from .requester import Requester

DEFAULT_HOST = "https://api.ldgr.app/analytics/"
EnvConfig = namedtuple("EnvConfig", ["host", "api_key"])
ENVIRONMENTS = {
    "PROD": EnvConfig(
        host="https://api.ldgr.app/analytics/",
        api_key=os.getenv("LEDGER_ANALYTICS_API_KEY"),
    ),
    "DEV": EnvConfig(
        host="https://platform-api-development.up.railway.app/analytics/",
        api_key=os.getenv("LEDGER_ANALYTICS_DEV_API_KEY"),
    ),
    "LOCAL": EnvConfig(
        host="http://localhost:8000/analytics/",
        api_key=os.getenv("LEDGER_ANALYTICS_LOCAL_API_KEY"),
    ),
}
ENV = ENVIRONMENTS[os.getenv("LEDGER_ANALYTICS_ENV", "PROD").upper()]


class BaseClient(ABC):
    def __init__(
        self,
        api_key: str | None = None,
        asynchronous: bool = False,
    ) -> None:
        if api_key is None:
            api_key = ENV.api_key
            if api_key is None:
                raise ValueError(
                    "Must pass in a valid `api_key` or set the `LEDGER_ANALYTICS_API_KEY` environment variable."
                )

        self._requester = Requester(api_key)

        self.host = ENV.host

        self.asynchronous = asynchronous

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, type, value, traceback):
        pass


class AnalyticsClient(BaseClient):
    def __init__(
        self,
        api_key: str | None = None,
        asynchronous: bool = False,
    ):
        super().__init__(api_key=api_key, asynchronous=asynchronous)

    triangle = property(
        lambda self: TriangleInterface(self.host, self._requester, self.asynchronous)
    )
    development_model = property(
        lambda self: ModelInterface(
            "development_model", self.host, self._requester, self.asynchronous
        )
    )
    tail_model = property(
        lambda self: ModelInterface(
            "tail_model", self.host, self._requester, self.asynchronous
        )
    )
    forecast_model = property(
        lambda self: ModelInterface(
            "forecast_model", self.host, self._requester, self.asynchronous
        )
    )

    def test_endpoint(self) -> str:
        self._requester.get(self.host + "triangle")
        return "Endpoint working!"
