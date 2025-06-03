from __future__ import annotations

import time
from typing import Dict

from requests import Response

from .config import JSONDict, ValidationConfig
from .console import RichConsole
from .interface import CashflowInterface, TriangleInterface
from .requester import Requester
from .triangle import Triangle


class CashflowModel(CashflowInterface):
    def __init__(
        self,
        id: str,
        name: str,
        dev_model_name: str,
        tail_model_name: str,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        super().__init__(model_class, endpoint, requester, asynchronous)

        self._endpoint = endpoint
        self._id = id
        self._name = name
        self._dev_model_name = dev_model_name
        self._tail_model_name = tail_model_name
        self._model_class = model_class
        self._fit_response: Response | None = None
        self._predict_response: Response | None = None
        self._get_response: Response | None = None
        self._captured_stdout: str = ""

    id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    dev_model_name = property(lambda self: self._dev_model_name)
    tail_model_name = property(lambda self: self._tail_model_name)
    model_class = property(lambda self: self._model_class)
    endpoint = property(lambda self: self._endpoint)
    fit_response = property(lambda self: self._fit_response)
    predict_response = property(lambda self: self._predict_response)
    get_response = property(lambda self: self._get_response)
    delete_response = property(lambda self: self._delete_response)
    captured_stdout = property(lambda self: self._captured_stdout)

    @classmethod
    def get(
        cls,
        id: str,
        name: str,
        dev_model_name: str,
        tail_model_name: str,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> CashflowModel:
        console = RichConsole()
        with console.status("Retrieving...", spinner="bouncingBar") as _:
            console.log(f"Getting model '{name}' with ID '{id}'")
            get_response = requester.get(endpoint, stream=True)

        self = cls(
            id,
            name,
            dev_model_name,
            tail_model_name,
            model_class,
            endpoint,
            requester,
            asynchronous,
        )
        self._get_response = get_response
        self._captured_stdout += console.get_stdout()
        return self

    @classmethod
    def fit_from_interface(
        cls,
        name: str,
        dev_model_name: str,
        tail_model_name: str,
        model_class: str,
        endpoint: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> CashflowModel:
        """This method fits a new model and constructs a CashflowModel instance.
        It's intended to be used from the `ModelInterface` class mainly,
        and in the future will likely be superseded by having separate
        `create` and `fit` API endpoints.
        """

        post_data = {
            "development_model_name": dev_model_name,
            "tail_model_name": tail_model_name,
            "name": name,
            "model_config": {},
        }
        fit_response = requester.post(endpoint, data=post_data)
        id = fit_response.json()["model"]["id"]
        self = cls(
            id=id,
            name=name,
            dev_model_name=dev_model_name,
            tail_model_name=tail_model_name,
            model_class=model_class,
            endpoint=endpoint + f"/{id}",
            requester=requester,
            asynchronous=asynchronous,
        )

        self._fit_response = fit_response

        return self

    def predict(
        self,
        triangle: str | Triangle,
        config: JSONDict | None = None,
        initial_loss_triangle: Triangle | str | None = None,
        prediction_name: str | None = None,
        timeout: int = 300,
        overwrite: bool = False,
    ) -> Triangle:
        triangle_name = triangle if isinstance(triangle, str) else triangle.name
        config = {
            "triangle_name": triangle_name,
            "predict_config": self.PredictConfig(**(config or {})).__dict__,
            "overwrite": overwrite,
        }
        if prediction_name:
            config["prediction_name"] = prediction_name

        if isinstance(initial_loss_triangle, Triangle):
            config["predict_config"]["initial_loss_name"] = initial_loss_triangle.name
        elif isinstance(initial_loss_triangle, str):
            config["predict_config"]["initial_loss_name"] = initial_loss_triangle

        url = self.endpoint + "/predict"
        self._predict_response = self._requester.post(url, data=config)

        if self._asynchronous:
            return self

        task_id = self.predict_response.json()["modal_task"]["id"]
        task_response = self._poll_remote_task(
            task_id=task_id,
            task_name=f"Predicting from model '{self.name}' on triangle '{triangle_name}'",
            timeout=timeout,
        )
        if task_response.get("status") != "success":
            raise ValueError(f"Task failed: {task_response['error']}")
        triangle_id = self.predict_response.json()["predictions"]
        triangle = TriangleInterface(
            host=self.endpoint.replace(f"{self.model_class_slug}/{self.id}", ""),
            requester=self._requester,
        ).get(id=triangle_id)
        return triangle

    def delete(self) -> CashflowModel:
        self._delete_response = self._requester.delete(self.endpoint)
        return self

    def _poll(self, task_id: str) -> JSONDict:
        endpoint = self.endpoint.replace(
            f"{self.model_class_slug}/{self.id}", f"tasks/{task_id}"
        )
        return self._requester.get(endpoint)

    def _poll_remote_task(
        self, task_id: str, task_name: str = "", timeout: int = 300
    ) -> dict:
        start = time.time()
        status = ["CREATED"]
        console = RichConsole()
        with console.status("Working...", spinner="bouncingBar") as _:
            while time.time() - start < timeout:
                task = self._poll(task_id).json()
                modal_status = (
                    "FINISHED" if task["task_response"] is not None else "PENDING"
                )
                status.append(modal_status)
                if status[-1] != status[-2]:
                    console.log(f"{task_name}: {status[-1]}")
                if status[-1].lower() == "finished":
                    self._captured_stdout += console.get_stdout()
                    return task["task_response"]
            raise TimeoutError(f"Task '{task}' timed out")

    class PredictConfig(ValidationConfig):
        """Cashflow model configuration class.

        Attributes:
            use_bf: Whether or not to use Bornhuetter-Ferguson method to adjust reserve estimates.
            use_reverse_bf: Whether or not to use the Reverse B-F method to adjust reserve
                estimates.
            gamma: Gamma parameter in the Reverse B-F method.
            min_reserve: Minimum reserve amounts as a function of development lag.
            seed: Seed to use for model sampling. Defaults to ``None``, but it is highly recommended
                to set.
        """

        use_bf: bool = True
        use_reverse_bf: bool = True
        gamma: float = 0.7
        min_reserve: Dict[float, float] | None
        seed: int | None = None
