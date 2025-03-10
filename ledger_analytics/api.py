from __future__ import annotations

import os
from abc import ABC

from bermuda import Triangle

from .model import DevelopmentModel, ForecastModel, TailModel
from .triangle import TriangleResponse


class BaseLedgerAnalytics(ABC):
    def __init__(self, host: str | None = None, asynchronous: bool = False) -> None:
        api_key = os.getenv("LEDGER_ANALYTICS_API_KEY")
        if api_key is not None:
            print("Found key")
        else:
            raise ValueError("Environment variable not found")
        self.headers = {"Authorization": f"Api-Key {api_key}"}

        if host is None:
            host = "http://localhost:8000/analytics/"

        trailing_slash = host[-1] == "/"
        if trailing_slash:
            self.host = host
        else:
            self.host = host + "/"

        self.asynchronous = asynchronous

    def __enter__(self) -> BaseLedgerAnalytics:
        return self

    def __exit__(self, type, value, traceback):
        pass


class LedgerAnalytics(BaseLedgerAnalytics):
    @property
    def triangle(self):
        return TriangleResponse(host=self.host, headers=self.headers)

    @property
    def development_model(self):
        return DevelopmentModel(host=self.host, headers=self.headers)

    @property
    def tail_model(self):
        return TailModel(host=self.host, headers=self.headers)

    @property
    def forecast_model(self):
        return ForecastModel(host=self.host, headers=self.headers)
