from __future__ import annotations

import logging

from bermuda import Triangle as BermudaTriangle

from .config import JSONDict
from .requester import Requester

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

    def create(
        self, name: str, data: JSONDict | BermudaTriangle, overwrite: bool = False
    ):
        if isinstance(data, BermudaTriangle):
            data = data.to_dict()

        config = {
            "triangle_name": name,
            "triangle_data": data,
            "overwrite": overwrite,
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

    def get_or_create(self, name: str, data: JSONDict | BermudaTriangle):
        """
        Gets a triangle if it exists with the same data, otherwise creates a new one. Will
        not overwrite an existing triangle with different data.
        """
        try:
            triangle = self.get(name=name)
        except ValueError:
            return self.create(name=name, data=data, overwrite=True)
        existing_data = triangle.data
        data = data.to_dict() if isinstance(data, BermudaTriangle) else data
        if existing_data != data:
            raise ValueError(
                f"Triangle with name '{name}' already exists with different data. "
            )
        return triangle

    def get_or_update(self, name: str, data: JSONDict | BermudaTriangle):
        """
        Gets a triangle if it exists with the same data, otherwise creates a new one. Will
        overwrite an existing triangle with different data.
        """
        try:
            triangle = self.get(name=name)
        except ValueError:
            return self.create(name=name, data=data, overwrite=True)
        data = data.to_dict() if isinstance(data, BermudaTriangle) else data
        existing_data = triangle.data
        if existing_data == data:
            return triangle
        else:
            return self.create(name=name, data=data, overwrite=True)

    def delete(self, name: str | None = None, id: str | None = None) -> None:
        triangle = self.get(name, id)
        triangle.delete()

    def _get_details_from_id_name(
        self, name: str | None = None, id: str | None = None
    ) -> str:
        n_triangles = self.list(limit=1)["count"]
        triangles = [
            result
            for result in self.list(limit=n_triangles).get("results")
            if result.get("name") == name or result.get("id") == id
        ]
        if not len(triangles):
            name_or_id = f"name '{name}'" if id is None else f"ID '{id}'"
            raise ValueError(f"No triangle found with {name_or_id}.")
        return triangles[0]

    def list(self, limit: int = 25) -> list[JSONDict]:
        response = self._requester.get(self.endpoint, params={"limit": limit})
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
        overwrite: bool = False,
        config: JSONDict | None = None,
        timeout: int = 300,
    ):
        triangle_name = triangle if isinstance(triangle, str) else triangle.name
        return ModelRegistry.REGISTRY[to_snake_case(model_type)].fit_from_interface(
            triangle_name,
            name,
            model_type,
            config,
            self.model_class,
            self.endpoint,
            self._requester,
            overwrite=overwrite,
            asynchronous=self._asynchronous,
            timeout=timeout,
        )

    def get(self, name: str | None = None, id: str | None = None):
        model_obj = self._get_details_from_id_name(name, id)
        endpoint = self.endpoint + f"/{model_obj['id']}"
        model_type = model_obj["modal_task_info"]["task_args"]["model_type"]
        return ModelRegistry.REGISTRY[to_snake_case(model_type)].get(
            model_obj["id"],
            model_obj["name"],
            model_type,
            model_obj["modal_task_info"]["task_args"]["model_config"],
            self.model_class,
            endpoint,
            self._requester,
            self._asynchronous,
        )

    def get_or_update(
        self,
        triangle: str | Triangle,
        name: str,
        model_type: str,
        config: JSONDict | None = None,
        timeout: int = 300,
    ):
        """Model Upsert. Gets a model if it exists with the same config, otherwise creates a new one,
        overwriting the existing model."""
        try:
            model = self.get(name=name)
        except ValueError:
            return self.create(
                triangle=triangle,
                name=name,
                model_type=model_type,
                config=config,
                timeout=timeout,
                overwrite=True,
            )
        existing_triangle_name = (
            model.get_response.json().get("triangle", {"name": None}).get("name")
        )
        if not self.check_config_consistency(config, model.config):
            return self.create(
                triangle=triangle,
                name=name,
                model_type=model_type,
                config=config,
                timeout=timeout,
                overwrite=True,
            )
        triangle_name = triangle if isinstance(triangle, str) else triangle.name
        if existing_triangle_name != triangle_name:
            return self.create(
                triangle=triangle,
                name=name,
                model_type=model_type,
                config=config,
                timeout=timeout,
                overwrite=True,
            )
        return model

    def get_or_create(
        self,
        triangle: str | Triangle,
        name: str,
        model_type: str,
        config: JSONDict | None = None,
        timeout: int = 300,
    ):
        """Gets a model if it exists with the same configuration, errors if it exists with an
        inconsistent configuration. Creates a new model if none with the same name exists."""
        try:
            model = self.get(name=name)
        except ValueError:
            return self.create(
                triangle=triangle,
                name=name,
                model_type=model_type,
                config=config,
                timeout=timeout,
                overwrite=True,
            )
        existing_triangle_name = (
            model.get_response.json().get("triangle", {"name": None}).get("name")
        )
        # Check config consistency (model.config will have defaults inserted so we can't
        # just compare the dicts)
        if not self.check_config_consistency(config, model.config):
            raise ValueError(
                f"Model with name '{name}' already exists with different config. "
                f"Existing config: {model.config}. New config: {config}"
                f"Existing triangle name: {existing_triangle_name}. "
            )
        triangle_name = triangle if isinstance(triangle, str) else triangle.name
        if existing_triangle_name != triangle_name:
            raise ValueError(
                f"Model with name '{name}' already exists with different config. "
                f"Existing config: {model.config}. New config: {config}"
                f"Existing triangle name: {existing_triangle_name}. "
            )
        return model

    def check_config_consistency(self, dict1, dict2):
        """
        Recursively checks items present in dict1 are consistent with items in
        dict2, meaning that the non-dictionary values are equal.
        """
        for k, v in dict1.items():
            if isinstance(v, dict):
                if k not in dict2:
                    return False
                if not self.check_config_consistency(v, dict2[k]):
                    return False
            else:
                if k not in dict2:
                    return False
                elif isinstance(v, str):
                    if v.lower() != dict2[k].lower():
                        return False
                else:
                    if v != dict2[k]:
                        return False
        return True

    def predict(
        self,
        triangle: str | Triangle,
        config: JSONDict | None = None,
        target_triangle: str | Triangle | None = None,
        prediction_name: str | None = None,
        timeout: int = 300,
        name: str | None = None,
        id: str | None = None,
        overwrite: bool = False,
    ):
        model = self.get(name, id)
        return model.predict(
            triangle,
            config=config,
            target_triangle=target_triangle,
            prediction_name=prediction_name,
            timeout=timeout,
            overwrite=overwrite,
        )

    def terminate(self, name: str | None = None, id: str | None = None):
        model = self.get(name, id)
        return model.terminate()

    def delete(self, name: str | None = None, id: str | None = None) -> None:
        model = self.get(name, id)
        return model.delete()

    def list(self, limit: int = 25) -> list[JSONDict]:
        return self._requester.get(
            self.endpoint, stream=True, params={"limit": limit}
        ).json()

    def list_model_types(self) -> list[JSONDict]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    @property
    def model_class_slug(self):
        return self.model_class.replace("_", "-")

    def _get_details_from_id_name(
        self, model_name: str | None = None, model_id: str | None = None
    ) -> str:
        n_objects = self.list(limit=1)["count"]
        models = [
            result
            for result in self.list(limit=n_objects).get("results")
            if result.get("name") == model_name or result.get("id") == model_id
        ]
        if not len(models):
            name_or_id = (
                f"name '{model_name}'" if model_id is None else f"ID '{model_id}'"
            )
            raise ValueError(f"No model found with {name_or_id}.")
        return models[0]


class CashflowInterface(metaclass=ModelRegistry):
    """The CashflowInterface class allows basic CRUD operations
    on for Cashflow endpoints and objects."""

    def __init__(
        self,
        model_class: str,
        host: str,
        requester: Requester,
        asynchronous: bool = False,
    ) -> None:
        self._model_class = model_class
        self._host = host
        self._endpoint = host + self.model_class_slug
        self._requester = requester
        self._asynchronous = asynchronous

    model_class = property(lambda self: self._model_class)
    endpoint = property(lambda self: self._endpoint)

    def create(
        self,
        dev_model: str | "DevelopmentModel",
        tail_model: str | "TailModel",
        name: str,
    ):
        dev_model_name = dev_model if isinstance(dev_model, str) else dev_model.name
        tail_model_name = tail_model if isinstance(tail_model, str) else tail_model.name
        return ModelRegistry.REGISTRY["cashflow_model"].fit_from_interface(
            name=name,
            dev_model_name=dev_model_name,
            tail_model_name=tail_model_name,
            model_class=self.model_class,
            endpoint=self.endpoint,
            requester=self._requester,
            asynchronous=self._asynchronous,
        )

    def get(self, name: str | None = None, id: str | None = None):
        model_obj = self._get_details_from_id_name(name, id)
        endpoint = self.endpoint + f"/{model_obj['id']}"
        dev_interface = ModelInterface(
            "development-model", self._host, self._requester, self._asynchronous
        )
        dev_model_name = dev_interface.get(id=model_obj["development_model"]).name
        tail_interface = ModelInterface(
            "tail-model", self._host, self._requester, self._asynchronous
        )
        tail_model_name = tail_interface.get(id=model_obj["tail_model"]).name
        return ModelRegistry.REGISTRY["cashflow_model"].get(
            id=model_obj["id"],
            name=model_obj["name"],
            dev_model_name=dev_model_name,
            tail_model_name=tail_model_name,
            model_class=self.model_class,
            endpoint=endpoint,
            requester=self._requester,
            asynchronous=self._asynchronous,
        )

    def predict(
        self,
        triangle: str | Triangle,
        config: JSONDict | None = None,
        initial_loss_triangle: str | Triangle | None = None,
        timeout: int = 300,
        name: str | None = None,
        id: str | None = None,
        overwrite: bool = False,
    ):
        model = self.get(name, id)
        return model.predict(
            triangle,
            config=config,
            initial_loss_triangle=initial_loss_triangle,
            timeout=timeout,
            overwrite=overwrite,
        )

    def delete(self, name: str | None = None, id: str | None = None) -> None:
        model = self.get(name, id)
        return model.delete()

    def list(self, limit: int = 25) -> list[JSONDict]:
        return self._requester.get(
            self.endpoint, stream=True, params={"limit": limit}
        ).json()

    def list_model_types(self) -> list[JSONDict]:
        url = self.endpoint + "-type"
        return self._requester.get(url).json()

    @property
    def model_class_slug(self):
        return self.model_class.replace("_", "-")

    def _get_details_from_id_name(
        self, model_name: str | None = None, model_id: str | None = None
    ) -> str:
        n_objects = self.list(limit=1)["count"]
        models = [
            result
            for result in self.list(limit=n_objects).get("results")
            if result.get("name") == model_name or result.get("id") == model_id
        ]
        if not len(models):
            name_or_id = (
                f"name '{model_name}'" if model_id is None else f"ID '{model_id}'"
            )
            raise ValueError(f"No model found with {name_or_id}.")
        return models[0]
