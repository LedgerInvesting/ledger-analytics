from __future__ import annotations

import time
from abc import ABC, abstractmethod

from bermuda import Triangle as BermudaTriangle
from requests import HTTPError, Response
from rich.console import Console

from .interface import ModelInterface, TriangleInterface
from .model_types import ConfigDict
from .requester import Requester
from .triangle import Triangle


class LedgerModel(ModelInterface):
    def __init__(
        self,
        id: str,
        name: str,
        model_type: str,
        config: ConfigDict | None,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        super().__init__(model_class, endpoint, requester, asynchronous)

        self._endpoint = endpoint
        self._id = id
        self._name = name
        self._model_type = model_type
        self._config = config or {}
        self._model_class = model_class
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None
        self._get_response: Response | None = None

    id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    model_type = property(lambda self: self._model_type)
    config = property(lambda self: self._config)
    model_class = property(lambda self: self._model_class)
    endpoint = property(lambda self: self._endpoint)
    fit_response = property(lambda self: self._fit_response)
    predict_response = property(lambda self: self._predict_response)
    get_response = property(lambda self: self._get_response)
    delete_response = property(lambda self: self._delete_response)

    @classmethod
    def get(
        cls,
        id: str,
        name: str,
        model_type: str,
        config: ConfigDict,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> LedgerModel:
        console = Console()
        with console.status("Retrieving...", spinner="bouncingBar") as _:
            console.log(f"Getting model '{name}' with ID '{id}'")
            get_response = requester.get(endpoint)

        self = cls(
            id,
            name,
            model_type,
            config,
            model_class,
            endpoint,
            requester,
            asynchronous,
        )
        self._get_response = get_response
        return self

    @classmethod
    def fit_from_interface(
        cls,
        triangle_name: str,
        name: str,
        model_type: str,
        config: ConfigDict | None,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> LedgerModel:
        """This method fits a new model and constructs a LedgerModel instance.
        It's intended to be used from the `ModelInterface` class mainly,
        and in the future will likely be superseded by having separate
        `create` and `fit` API endpoints.
        """
        config = {
            "triangle_name": triangle_name,
            "name": name,
            "model_type": model_type,
            "config": config or {},
        }
        fit_response = requester.post(endpoint, data=config)
        id = fit_response.json()["model"]["id"]
        self = cls(
            id=id,
            name=name,
            model_type=model_type,
            config=config,
            model_class=model_class,
            endpoint=endpoint + f"/{id}",
            requester=requester,
            asynchronous=asynchronous,
        )

        self._fit_response = fit_response

        if asynchronous:
            return self

        task_id = self.fit_response.json()["modal_task"]["id"]
        self._run_async_task(
            task_id,
            task=f"Fitting model '{self.name}' on triangle '{triangle_name}'",
        )
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

        task_id = self.predict_response.json()["modal_task"]["id"]
        self._run_async_task(
            task_id=task_id,
            task=f"Predicting from model '{self.name}' on triangle '{triangle_name}'",
        )
        return self

    def delete(self) -> LedgerModel:
        self._delete_response = self._requester.delete(self.endpoint)
        return self

    def _poll(self, task_id: str) -> ConfigDict:
        endpoint = self.endpoint.replace(
            f"{self.model_class_slug}/{self.id}", f"tasks/{task_id}"
        )
        return self._requester.get(endpoint)

    def _run_async_task(self, task_id: str, task: str = ""):
        status = ["CREATED"]
        console = Console()
        with console.status("Working...", spinner="bouncingBar") as _:
            while status[-1].lower() != "success":
                _status = self._poll(task_id).json().get("status")
                status.append(_status)
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
    pass


class TailModel(LedgerModel):
    pass


class ForecastModel(LedgerModel):
    pass
