from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .requester import Requester
from .triangle import Triangle
from .types import ConfigDict


class LedgerModel(ABC): BASE_ENDPOINT: str | None = None

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

    def fit(
        self,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None = None,
    ) -> FittedModel:
        config = {
            "triangle_name": triangle_name,
            "model_name": model_name,
            "model_type": model_type,
            "model_config": model_config or {},
        }
        fit_response = self._requester.post(self.endpoint, data=config)

        try:
            model_id = self._fit_response.json().get("model").get("id")
        except Exception:
            raise HTTPError(self._fit_response)

        if model_id is None:
            raise HTTPError(
                "The model cannot be fit. The following information was returned:\n",
                self._fit_response.json(),
            )
        if self.asynchronous:
            return self

        # unsure if the fitted model should inherit the fit task. Perhaps?
        modal_task = self._fit_response.json()["modal_task"]["id"]
        status = self.poll(modal_task).json().get("status")
        while status.lower() != "success":
            time.sleep(2)
            status = self.poll(modal_task).json().get("status")
            if status.lower() == "success":
                return FittedModel(model_id, model_name, triangle_name, self.BASE_ENDPOINT + '/predict', self._requester, fit_response)

    def poll(self, task: str):
        return self._requester.get(
            self.endpoint.replace(self.BASE_ENDPOINT, "tasks") + f"/{task}"
        )

    def delete(self, model_id: str) -> Response:
        if model_id is None:
            # should allow model_name lookup here
            pass

        return self._requester.delete(self.endpoint + f"/{model_id}")

    def list_model_types(self) -> list[str]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()


class DevelopmentModels(LedgerModel):
    BASE_ENDPOINT = "development-model"


class TailModels(LedgerModel):
    BASE_ENDPOINT = "tail-model"


class ForecastModels(LedgerModel):
    BASE_ENDPOINT = "forecast-model"

@dataclass
class FittedModel:
    model_id: str
    model_name: str
    fit_triangle_name: str
    _base_endpoint: str
    _requester: Requester
    response: Response

    def poll(self, task: str):
        return self._requester.get(
            self._base_endpoint.replace(self.BASE_ENDPOINT, "tasks") + f"/{task}"
        )

    def predict(
        self, triangle_name: str | None = None, predict_config: ConfigDict | None = None
    ) -> Triangle:
        if triangle_name is None:
            triangle_name = self.fit_triangle_name

        config = {
            "triangle_name": triangle_name,
            "predict_config": predict_config or {},
        }

        url = self._base_endpoint + f"/{self.model_id}/predict"
        self._predict_response = self._requester.post(url, data=config)
        modal_task = self._predict_response.json()["modal_task"]["id"]
        status = self.poll(modal_task).json().get("status")
        while status.lower() != "success":
            time.sleep(2)
            status = self.poll(modal_task).json().get("status")
            if status.lower() == "success":
                break

        prediction_id = self._predict_response.json()["predictions"]
        return self.requester.triangle.get(triangle_id=prediction_id)


