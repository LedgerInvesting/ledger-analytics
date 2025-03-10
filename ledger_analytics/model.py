from __future__ import annotations

from abc import ABC, abstractmethod
from bermuda import Triangle
import requests
from typing import Any


class LedgerModel(ABC):
    FIT_URL: str | None = None
    
    def __init__(self, host: str, headers: dict[str, str]) -> None:
        self.host = host
        self.headers = headers
        self._model_id: str | None = None

        if self.FIT_URL is None:
            raise AttributeError(f"FIT_URL needs to be set in {self.__class__.__name__}")
        if self.FIT_URL.split("/")[-1] != "/":
            self.FIT_URL = self.FIT_URL + "/"

    model_id = property(lambda self: self._model_id)

    def fit(self, triangle: Triangle, config: dict[str, Any] | None = None) -> LedgerModel:
        response = requests.post(self.host + self.FIT_URL, json=config, headers=self.headers)
        self._model_id = response.json().get("model").get("id")
        if self._model_id is None:
            raise requests.HTTPError("The model cannot be fit. The following information was returned:\n",
                                      response.json()
                                      )
        return self

    def predict(self, config: dict[str, Any] | None = None) -> Triangle:
        response = requests.post(self.host + self.FIT_URL + "predict", json=config or {}, headers=self.headers)
        prediction_id = response.json()["predictions"]
        triangle = requests.get(self.host + f"triangle/{prediction_id}", headers=self.headers)
        return triangle

    def status(self, task_id: str) -> dict[str, Any]:
        return requests.get(self.host + "tasks/" + task_id).json()


class DevelopmentModel(LedgerModel):
    FIT_URL = "development-model"


class TailModel(LedgerModel):
    FIT_URL = "tail-model"


class ForecastModel(LedgerModel):
    FIT_URL = "forecast-model"
