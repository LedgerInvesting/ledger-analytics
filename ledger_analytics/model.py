from __future__ import annotations

from abc import ABC, abstractmethod

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .requester import Requester
from .triangle import Triangle
from .types import JSONData


class LedgerModel(ABC):
    BASE_ENDPOINT: str | None = None

    def __init__(
        self, host: str, requester: Requester, asynchronous: bool = False
    ) -> None:
        if self.BASE_ENDPOINT is None:
            raise AttributeError(
                f"BASE_ENDPOINT needs to be set in {self.__class__.__name__}"
            )

        self.endpoint = host + self.BASE_ENDPOINT
        self._requester = requester
        self.asynchronous = asynchronous
        self._model_id: str | None = None
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None
        self._triangle = Triangle(host, requester, asynchronous)

    model_id = property(lambda self: self._model_id)
    fit_response = property(lambda self: self._fit_response)
    predict_repsonse = property(lambda self: self._predict_response)

    def fit(self, config: JSONData | None = None) -> LedgerModel:
        self._fit_response = self._requester.post(self.endpoint, data=config)

        try:
            self._model_id = self._fit_response.json().get("model").get("id")
        except Exception:
            raise HTTPError(self._fit_response)

        if self._model_id is None:
            raise HTTPError(
                "The model cannot be fit. The following information was returned:\n",
                self._fit_response.json(),
            )
        return self

    def predict(self, config: JSONData | None = None) -> BermudaTriangle:
        url = self.endpoint + f"/{self._model_id}/predict"
        self._predict_response = self._requester.post(url, data=config)

        try:
            prediction_id = self._predict_response.json()["predictions"]
        except Exception:
            raise HTTPError()

        triangle = self._triangle.get(triangle_id=prediction_id)
        return BermudaTriangle.from_dict(triangle.json()["triangle_data"])


class DevelopmentModel(LedgerModel):
    BASE_ENDPOINT = "development-model"


class TailModel(LedgerModel):
    BASE_ENDPOINT = "tail-model"


class ForecastModel(LedgerModel):
    BASE_ENDPOINT = "forecast-model"
