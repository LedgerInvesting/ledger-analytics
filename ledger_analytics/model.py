from __future__ import annotations

import time
from abc import ABC, abstractmethod

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response
from tqdm import tqdm

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
        remote_task = self._fit_response.json()["modal_task"]["id"]
        self._run_remote_task(remote_task, task="fitting")
        return self

    def predict(
        self,
        triangle_name: str | None = None,
        model_id: str | None = None,
        predict_config: ConfigDict | None = None,
    ) -> Triangle:
        if triangle_name is None:
            triangle_name = self.fit_triangle_name

        config = {
            "triangle_name": triangle_name,
            "predict_config": predict_config or {},
        }

        model_id = model_id or self._model_id

        url = self.endpoint + f"/{model_id}/predict"
        self._predict_response = self._requester.post(url, data=config)
        remote_task = self._predict_response.json()["modal_task"]["id"]
        self._run_remote_task(remote_task, task="predicting")
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

    def _run_remote_task(self, remote_id: str, task: str = ""):
        status = ["CREATED"]
        tqdm_config = {
            "total": 2,
            "bar_format": "{desc}|{bar}| {n_fmt}/{total_fmt} [{unit}]",
        }
        with tqdm(**tqdm_config) as progress:
            progress.set_description(status[-1])
            progress.unit = f"task={task}, total={progress.format_interval(progress.format_dict['elapsed'])}"
            progress.refresh()
            while status[-1].lower() != "success":
                progress.unit = f"task={task}, total={progress.format_interval(progress.format_dict['elapsed'])}"
                progress.refresh()
                status.append(self.poll(remote_id).json().get("status"))
                if status[-1] != status[-2]:
                    progress.set_description(status[-1])
                    progress.update()
                if status[-1].lower() in [
                    "success",
                    "failure",
                    "terminated",
                    "timeout",
                ]:
                    break


class DevelopmentModel(LedgerModel):
    BASE_ENDPOINT = "development-model"


class TailModel(LedgerModel):
    BASE_ENDPOINT = "tail-model"


class ForecastModel(LedgerModel):
    BASE_ENDPOINT = "forecast-model"
