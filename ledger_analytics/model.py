from __future__ import annotations

import time
from abc import ABC, abstractmethod

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response

from .interface import ModelInterface
from .requester import Requester
from .triangle import Triangle
from .types import ConfigDict


class LedgerModel(ModelInterface):
    BASE_ENDPOINT: str | None = None

    def __init__(
        self, host: str, requester: Requester, asynchronous: bool = False
    ) -> None:
        if self.BASE_ENDPOINT is None:
            raise AttributeError(
                f"BASE_ENDPOINT needs to be set in {self.__class__.__name__}"
            )

        endpoint = host + self.BASE_ENDPOINT
        super().__init__(endpoint, requester, asynchronous)
        self._model_id: str | None = None
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None
        self._triangle = Triangle(host, requester, asynchronous)

    model_id = property(lambda self: self._model_id)
    fit_response = property(lambda self: self._fit_response)
    predict_reponse = property(lambda self: self._predict_response)
    delete_response = property(lambda self: self._delete_response)

    def get():
        # TODO?
        pass

    def fit(
        self,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None = None,
    ) -> LedgerModel:
        config = {
            "triangle_name": triangle_name,
            "model_name": model_name,
            "model_type": model_type,
            "model_config": model_config or {},
        }
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
        if self.asynchronous:
            return self
        modal_task = self._fit_response.json()["modal_task"]["id"]
        status = self.poll(modal_task).json().get("status")
        while status.lower() != "success":
            time.sleep(2)
            status = self.poll(modal_task).json().get("status")
            if status.lower() == "success":
                return self

    def poll(self, task: str):
        return self._requester.get(
            self.endpoint.replace(self.BASE_ENDPOINT, "tasks") + f"/{task}"
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

        url = self.endpoint + f"/{self._model_id}/predict"
        self._predict_response = self._requester.post(url, data=config)
        modal_task = self._predict_response.json()["modal_task"]["id"]
        status = self.poll(modal_task).json().get("status")
        while status.lower() != "success":
            time.sleep(2)
            status = self.poll(modal_task).json().get("status")
            if status.lower() == "success":
                break

        prediction_id = self._predict_response.json()["predictions"]
        return self._triangle.get(triangle_id=prediction_id)

    def delete(self, model_id: str | None = None) -> LedgerModel:
        if model_id is None and self.model_id is None:
            raise ValueError("`model_id` is missing.")

        if model_id is None:
            model_id = self.model_id

        self._delete_response = self._requester.delete(self.endpoint + f"/{model_id}")
        return self

    @property
    def fit_triangle_name(self) -> str:
        if self.fit_response is None:
            return None
        triangle_id = self.fit_response.json().get("model").get("triangle")
        name, _ = self._triangle.get(triangle_id)
        return name

    def list_model_types(self) -> list[str]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()


class DevelopmentModel(LedgerModel):
    BASE_ENDPOINT = "development-model"


class TailModel(LedgerModel):
    BASE_ENDPOINT = "tail-model"


class ForecastModel(LedgerModel):
    BASE_ENDPOINT = "forecast-model"
