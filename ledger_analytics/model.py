from __future__ import annotations

import time
from abc import ABC, abstractmethod

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response
from rich.console import Console

from .interface import ModelInterface, TriangleInterface
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
        super().__init__(model_type, endpoint, requester, asynchronous)

        self._model_id = model_id
        self._model_name = model_name
        self._model_config = model_config or {}
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None

    model_id = property(lambda self: self._model_id)
    model_name = property(lambda self: self._model_name)
    model_config = property(lambda self: self._model_config)
    fit_response = property(lambda self: self._fit_response)
    predict_response = property(lambda self: self._predict_response)
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
        model_id = fit_response.json()["model"]["id"]
        self = cls(
            model_id=model_id,
            model_name=model_name,
            model_type=model_type,
            model_config=model_config,
            endpoint=endpoint + f"/{model_id}",
            requester=requester,
            asynchronous=asynchronous,
        )

        if asynchronous:
            return self

        self._fit_response = fit_response
        self._run_async_task(task=f"Fitting model {self.model_name}")
        return self

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
        if self._asynchronous:
            return self
        modal_task = self._fit_response.json()["modal_task"]["id"]
        status = self.poll(modal_task).json().get("status")
        while status.lower() != "success":
            time.sleep(2)
            status = self.poll(modal_task).json().get("status")
            if status.lower() == "success":
                return self

    def predict(
        self, triangle_name: str, predict_config: ConfigDict | None = None
    ) -> Triangle:
        config = {
            "triangle_name": triangle_name,
            "predict_config": predict_config or {},
        }

        url = self.endpoint + "/predict"
        self._predict_response = self._requester.post(url, data=config)

        if self._asynchronous:
            return self

        self._run_async_task(task=f"Predicting from model {self.model_name}")
        return self

    def delete(self) -> LedgerModel:
        self._delete_response = self._requester.delete(self.endpoint)
        return self

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()

    def _run_async_task(self, task: str = ""):
        status = ["CREATED"]
        console = Console()
        with console.status("Working...", spinner="bouncingBar") as _:
            while status[-1].lower() != "success":
                status.append(self.get().json().get("modal_task_info").get("status"))
                if status[-1] != status[-2]:
                    console.log(f"{task}: {status[-1]}")
                if status[-1].lower() in [
                    "success",
                    "failure",
                    "terminated",
                    "timeout",
                    "not_found",
                ]:
                    break


class DevelopmentModel(LedgerModel):
    BASE_ENDPOINT = "development-model"


class TailModel(LedgerModel):
    BASE_ENDPOINT = "tail-model"


class ForecastModel(LedgerModel):
    BASE_ENDPOINT = "forecast-model"
