from __future__ import annotations

import logging

from bermuda import Triangle as BermudaTriangle

from .requester import Requester
from .types import ConfigDict

logger = logging.getLogger(__name__)


def to_snake_case(x: str) -> str:
    uppers = [s.isupper() if i > 0 else False for i, s in enumerate(x)]
    snake = ["_" + s.lower() if upper else s for upper, s in zip(uppers, x.lower())]
    return "".join(snake)


class Registry(type):
    REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY[to_snake_case(new_cls.__name__)] = new_cls
        return new_cls


class TriangleRegistry(Registry):
    pass


class ModelRegistry(Registry):
    pass


class TriangleInterface(metaclass=TriangleRegistry):
    """The TriangleInterface class handles the basic CRUD operations
    on triangles, managed through AnalyticsClient.
    """

    def __init__(
        self,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self.endpoint = host + "triangle"
        self._requester = requester
        self.asynchronous = asynchronous

    def create(self, name: str, data: ConfigDict):
        if isinstance(data, BermudaTriangle):
            data = data.to_dict()

        config = {
            "triangle_name": name,
            "triangle_data": data,
        }

        post_response = self._requester.post(self.endpoint, data=config)
        id = post_response.json().get("id")
        logger.info(f"Created triangle '{name}' with ID {id}.")

        endpoint = self.endpoint + f"/{id}"
        triangle = TriangleRegistry.REGISTRY["triangle"](
            id,
            name,
            data,
            endpoint,
            self._requester,
        )
        triangle._post_response = post_response
        return triangle

    def get(self, name: str | None = None, id: str | None = None):
        obj = self._get_details_from_id_name(name, id)
        return TriangleRegistry.REGISTRY["triangle"].get(
            obj["id"],
            obj["name"],
            self.endpoint + f"/{obj['id']}",
            self._requester,
        )

    def delete(self, name: str | None = None, id: str | None = None) -> None:
        triangle = self.get(name, id)
        triangle.delete()

    def _get_details_from_id_name(
        self, name: str | None = None, id: str | None = None
    ) -> str:
        triangles = [
            result
            for result in self.list().get("results")
            if result.get("name") == name or result.get("id") == id
        ]
        if not len(triangles):
            name_or_id = f"name '{name}'" if id is None else f"ID '{id}'"
            raise ValueError(f"No triangle found with {name_or_id}.")
        return triangles[0]

    def list(self) -> list[ConfigDict]:
        response = self._requester.get(self.endpoint)
        if not response.ok:
            response.raise_for_status()
        return response.json()


class ModelInterface(metaclass=ModelRegistry):
    """The ModelInterface class allows basic CRUD operations
    on for model endpoints and objects."""

    def __init__(
        self,
        model_class: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self._model_class = model_class
        self._endpoint = host + self.model_class_slug
        self._requester = requester
        self._asynchronous = asynchronous

    model_class = property(lambda self: self._model_class)
    endpoint = property(lambda self: self._endpoint)

    def create(
        self,
        triangle: str | Triangle,
        name: str,
        model_type: str,
        config: ConfigDict | None = None,
        timeout: int = 300,
    ):
        triangle_name = triangle if isinstance(triangle, str) else triangle.name
        return ModelRegistry.REGISTRY[self.model_class].fit_from_interface(
            triangle_name,
            name,
            model_type,
            config,
            self.model_class,
            self.endpoint,
            self._requester,
            self._asynchronous,
            timeout=timeout,
        )

    def get(self, name: str | None = None, id: str | None = None):
        model_obj = self._get_details_from_id_name(name, id)
        endpoint = self.endpoint + f"/{model_obj['id']}"
        return ModelRegistry.REGISTRY[self.model_class].get(
            model_obj["id"],
            model_obj["name"],
            model_obj["modal_task_info"]["task_args"]["model_type"],
            model_obj["modal_task_info"]["task_args"]["model_config"],
            self.model_class,
            endpoint,
            self._requester,
            self._asynchronous,
        )

    def predict(
        self,
        triangle: str | Triangle,
        config: ConfigDict | None = None,
        target_triangle: str | Triangle | None = None,
        timeout: int = 300,
        name: str | None = None,
        id: str | None = None,
    ):
        model = self.get(name, id)
        return model.predict(
            triangle, config=config, target_triangle=target_triangle, timeout=timeout
        )

    def terminate(self, name: str | None = None, id: str | None = None):
        model = self.get(name, id)
        return model.terminate()

    def delete(self, name: str | None = None, id: str | None = None) -> None:
        model = self.get(name, id)
        return model.delete()

    def list(self) -> list[ConfigDict]:
        return self._requester.get(self.endpoint).json()

    def list_model_types(self) -> list[ConfigDict]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    @property
    def model_class_slug(self):
        return self.model_class.replace("_", "-")

    def _get_details_from_id_name(
        self, model_name: str | None = None, model_id: str | None = None
    ) -> str:
        models = [
            result
            for result in self.list().get("results")
            if result.get("name") == model_name or result.get("id") == model_id
        ]
        if not len(models):
            name_or_id = (
                f"name '{model_name}'" if model_id is None else f"ID '{model_id}'"
            )
            raise ValueError(f"No model found with {name_or_id}.")
        return models[0]
