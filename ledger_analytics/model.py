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
    def __init__(
        self,
        model_id: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.endpoint = endpoint
        super().__init__(endpoint, requester, asynchronous)

        self._model_id = model_id
        self._model_name = model_name
        self._model_type = model_type
        self._model_config = model_config or {}
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None

    model_id = property(lambda self: self._model_id)
    model_name = property(lambda self: self._model_name)
    model_type = property(lambda self: self._model_type)
    model_config = property(lambda self: self._model_config)
    fit_response = property(lambda self: self._fit_response)
    predict_reponse = property(lambda self: self._predict_response)
    delete_response = property(lambda self: self._delete_response)

    def get(self):
        return self._requester.get(self.endpoint)

    @classmethod
    def fit_from_interface(
        cls,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> LedgerModel:
        # TODO: replace with a dedicated 'create' step for models in the API
        config = {
            "triangle_name": triangle_name,
            "model_name": model_name,
            "model_type": model_type,
            "model_config": model_config or {},
        }
        fit_response = requester.post(endpoint, data=config)
        model_id = fit_response.json().get("model").get("id")

        instance = cls(
            model_id,
            model_name,
            model_type,
            model_config,
            endpoint,
            requester,
            asynchronous,
        )
        return instance

    def fit(
        self,
        triangle_name: str,
        model_name: str,
        model_type: str,
        model_config: ConfigDict | None = None,
    ) -> LedgerModel:
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
