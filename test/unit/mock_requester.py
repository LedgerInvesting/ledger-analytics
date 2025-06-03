import requests
from bermuda import meyers_tri
from requests_mock import Mocker

from ledger_analytics import Requester
from ledger_analytics.config import HTTPMethods, JSONDict


class TriangleMockRequester(Requester):
    def _factory(
        self,
        method: HTTPMethods,
        url: str,
        data: JSONDict,
        stream: bool = False,
        params: JSONDict | None = None,
    ):
        with Mocker() as mocker:
            if method.lower() == "post":
                mocker.post(url, json={"id": "abc"}, status_code=201)
                response = requests.post(url)
            elif method.lower() == "get":
                mocker.get(
                    url,
                    json={
                        "count": 1,
                        "triangle_name": "test_meyers_triangle",
                        "triangle_data": meyers_tri.to_dict(),
                        "results": [
                            {
                                "name": "test_meyers_triangle",
                                "id": "abc",
                            }
                        ],
                    },
                    status_code=200,
                )
                response = requests.get(url)
            elif method.lower() == "delete":
                mocker.delete(url, status_code=201)
                response = requests.delete(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response


class TriangleMockRequesterAfterDeletion(Requester):
    def _factory(
        self,
        method: HTTPMethods,
        url: str,
        data: JSONDict,
        stream: bool = False,
        params: JSONDict | None = None,
    ):
        with Mocker() as mocker:
            if method.lower() == "post":
                mocker.post(url, json={"id": "abc"}, status_code=201)
                response = requests.post(url)
            elif method.lower() == "get":
                mocker.get(url, status_code=404)
                response = requests.get(url)
            elif method.lower() == "delete":
                mocker.delete(url, status_code=201)
                response = requests.delete(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response


class ModelMockRequester(Requester):
    def _factory(
        self,
        method: HTTPMethods,
        url: str,
        data: JSONDict,
        stream: bool = False,
        params: JSONDict | None = None,
    ):
        with Mocker() as mocker:
            if method.lower() == "post" and "predict" not in url:
                mocker.post(url, json={"model": {"id": "model_abc"}}, status_code=201)
                response = requests.post(url)
            elif method.lower() == "post":
                mocker.post(
                    url,
                    json={"id": "model_abc", "predictions": "triangle_abc"},
                    status_code=201,
                )
                response = requests.post(url)
            elif method.lower() == "get":
                mocker.get(
                    url,
                    json={
                        "count": 1,
                        "results": [
                            {
                                "triangle_name": "test_meyers_triangle",
                                "name": "test_chain_ladder",
                                "id": "model_abc",
                                "modal_task_info": {
                                    "id": "abc123",
                                    "task_args": {
                                        "model_config": {},
                                        "model_type": "ChainLadder",
                                    },
                                },
                            }
                        ],
                    },
                    status_code=200,
                )
                response = requests.get(url)
            elif method.lower() == "delete":
                mocker.delete(url, status_code=201)
                response = requests.delete(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response


class ModelMockRequesterAfterDeletion(Requester):
    def _factory(
        self,
        method: HTTPMethods,
        url: str,
        data: JSONDict,
        stream: bool = False,
        params: JSONDict | None = None,
    ):
        with Mocker() as mocker:
            if method.lower() == "get":
                mocker.get(url, status_code=404)
                response = requests.get(url)
            else:
                raise ValueError(f"Unrecognized HTTPMethod {method}.")

        self._catch_status(response)
        return response
