from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests
from bermuda import Triangle as BermudaTriangle


class LedgerModel(ABC):
    FIT_URL: str | None = None

    def __init__(self, host: str, headers: dict[str, str]) -> None:
        self.host = host
        self.headers = headers
        self._model_id: str | None = None
        self._fit_response: requests.Response | None = None
        self._predict_response: requests.Response | None = None

        if self.FIT_URL is None:
            raise AttributeError(
                f"FIT_URL needs to be set in {self.__class__.__name__}"
            )

    model_id = property(lambda self: self._model_id)
    fit_response = property(lambda self: self._fit_response)
    predict_repsonse = property(lambda self: self._predict_response)

    def fit(self, config: dict[str, Any] | None = None) -> LedgerModel:
        self._fit_response = requests.post(
            self.host + self.FIT_URL, json=config, headers=self.headers
        )

        try:
            self._model_id = self._fit_response.json().get("model").get("id")
        except Exception:
            raise requests.HTTPError()

        if self._model_id is None:
            raise requests.HTTPError(
                "The model cannot be fit. The following information was returned:\n",
                self._fit_response.json(),
            )
        return self

    def predict(self, config: dict[str, Any] | None = None) -> BermudaTriangle:
        self._predict_response = requests.post(
            self.host + self.FIT_URL + "predict",
            json=config or {},
            headers=self.headers,
        )

        try:
            prediction_id = self._predict_response.json()["predictions"]
        except Exception:
            raise requests.HTTPError()

        triangle = requests.get(
            self.host + f"triangle/{prediction_id}", headers=self.headers
        )
        return BermudaTriangle.from_dict(triangle.json()["triangle_data"])


class DevelopmentModel(LedgerModel):
    FIT_URL = "development-model"


class TailModel(LedgerModel):
    FIT_URL = "tail-model"


class ForecastModel(LedgerModel):
    FIT_URL = "forecast-model"
